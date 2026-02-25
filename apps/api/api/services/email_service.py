"""Local email notification service.

Stores email notifications in the DB (no SMTP). Emails are viewable via API endpoints.
Each method checks user's NotificationPreference before creating an EmailLog.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone

import structlog
from sqlalchemy.orm import Session

from api.database.models import (
    AICache,
    Course,
    EmailLog,
    NotificationPreference,
    Proposal,
    User,
)

logger = structlog.get_logger()


def _email_wrapper(content_html: str) -> str:
    """Wrap content in Datapizza email template."""
    return (
        '<div style="font-family: \'Helvetica Neue\', sans-serif; max-width: 600px; margin: 0 auto; padding: 24px;">'
        '<div style="background: #1b64f5; padding: 16px 24px; border-radius: 12px 12px 0 0;">'
        '<h1 style="color: white; margin: 0; font-size: 18px;">Datapizza</h1>'
        "</div>"
        '<div style="padding: 24px; border: 1px solid #d5dde2; border-top: none; border-radius: 0 0 12px 12px;">'
        f"{content_html}"
        "</div>"
        "</div>"
    )


class EmailService:
    """Static service for creating local email notifications."""

    @staticmethod
    def send_email(
        db: Session,
        recipient_id: str,
        email_type: str,
        subject: str,
        body_html: str,
        body_text: str | None = None,
        sender_label: str = "Datapizza",
        related_proposal_id: str | None = None,
    ) -> EmailLog | None:
        """Create an EmailLog entry if notifications are enabled for the user.

        Returns the created EmailLog or None if notifications are disabled.
        """
        # Look up recipient
        user = db.query(User).filter(User.id == recipient_id).first()
        if not user:
            logger.warning("email_recipient_not_found", recipient_id=recipient_id)
            return None

        # Check notification preferences (default: all enabled)
        pref = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == recipient_id,
        ).first()

        if pref and not pref.email_notifications:
            logger.info("email_notifications_disabled", user_id=recipient_id, email_type=email_type)
            return None

        email_log = EmailLog(
            id=str(uuid.uuid4()),
            recipient_id=recipient_id,
            recipient_email=user.email,
            sender_label=sender_label,
            email_type=email_type,
            subject=subject,
            body_html=body_html,
            body_text=body_text,
            related_proposal_id=related_proposal_id,
            is_read=0,
            created_at=datetime.now(timezone.utc),
        )
        db.add(email_log)
        db.commit()
        db.refresh(email_log)

        logger.info("email_created", email_id=email_log.id, email_type=email_type, recipient_id=recipient_id)
        return email_log

    @staticmethod
    def send_proposal_received(db: Session, proposal: Proposal, talent: User, company: User) -> EmailLog | None:
        """Email to TALENT when a company sends a proposal."""
        company_name = company.company_name or company.full_name
        subject = f"Nuova proposta formativa da {company_name}"
        content = (
            f"<h2 style='margin-top: 0;'>Hai ricevuto una nuova proposta!</h2>"
            f"<p>Ciao <strong>{talent.full_name}</strong>,</p>"
            f"<p><strong>{company_name}</strong> ti ha inviato una proposta formativa "
            f"personalizzata sulla piattaforma Datapizza.</p>"
            f"<p>Budget indicato: <strong>{proposal.budget_range or 'Non specificato'}</strong></p>"
            f"<p>Accedi alla piattaforma per visualizzare i dettagli e rispondere.</p>"
            f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
        )
        return EmailService.send_email(
            db,
            recipient_id=talent.id,
            email_type="proposal_received",
            subject=subject,
            body_html=_email_wrapper(content),
            body_text=f"Nuova proposta formativa da {company_name}. Accedi per i dettagli.",
            related_proposal_id=proposal.id,
        )

    @staticmethod
    def send_proposal_accepted(db: Session, proposal: Proposal, talent: User, company: User) -> EmailLog | None:
        """Email to COMPANY when talent accepts the proposal."""
        subject = f"{talent.full_name} ha accettato la tua proposta"
        content = (
            f"<h2 style='margin-top: 0;'>Proposta accettata!</h2>"
            f"<p>Ciao <strong>{company.full_name}</strong>,</p>"
            f"<p><strong>{talent.full_name}</strong> ha accettato la tua proposta formativa.</p>"
            f"<p>Il percorso di formazione puo' ora iniziare. Accedi alla piattaforma "
            f"per seguire i progressi del candidato.</p>"
            f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
        )
        return EmailService.send_email(
            db,
            recipient_id=company.id,
            email_type="proposal_accepted",
            subject=subject,
            body_html=_email_wrapper(content),
            body_text=f"{talent.full_name} ha accettato la tua proposta. Accedi per i dettagli.",
            related_proposal_id=proposal.id,
        )

    @staticmethod
    def send_proposal_rejected(db: Session, proposal: Proposal, talent: User, company: User) -> EmailLog | None:
        """Email to COMPANY when talent rejects the proposal."""
        subject = f"{talent.full_name} ha rifiutato la tua proposta"
        content = (
            f"<h2 style='margin-top: 0;'>Proposta rifiutata</h2>"
            f"<p>Ciao <strong>{company.full_name}</strong>,</p>"
            f"<p><strong>{talent.full_name}</strong> ha rifiutato la tua proposta formativa.</p>"
            f"<p>Puoi creare una nuova proposta per un altro candidato dalla sezione Talenti.</p>"
            f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
        )
        return EmailService.send_email(
            db,
            recipient_id=company.id,
            email_type="proposal_rejected",
            subject=subject,
            body_html=_email_wrapper(content),
            body_text=f"{talent.full_name} ha rifiutato la tua proposta.",
            related_proposal_id=proposal.id,
        )

    @staticmethod
    def send_course_started(db: Session, proposal: Proposal, course_title: str, talent: User, company: User) -> EmailLog | None:
        """Email to COMPANY when talent starts a course."""
        subject = f"{talent.full_name} ha iniziato il corso: {course_title}"
        content = (
            f"<h2 style='margin-top: 0;'>Corso iniziato</h2>"
            f"<p>Ciao <strong>{company.full_name}</strong>,</p>"
            f"<p><strong>{talent.full_name}</strong> ha iniziato il corso "
            f"<strong>{course_title}</strong> nel percorso formativo.</p>"
            f"<p>Accedi alla dashboard per seguire i progressi.</p>"
            f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
        )
        return EmailService.send_email(
            db,
            recipient_id=company.id,
            email_type="course_started",
            subject=subject,
            body_html=_email_wrapper(content),
            body_text=f"{talent.full_name} ha iniziato il corso: {course_title}.",
            related_proposal_id=proposal.id,
        )

    @staticmethod
    def send_course_completed(db: Session, proposal: Proposal, course_title: str, talent: User, company: User) -> EmailLog | None:
        """Email to COMPANY when talent completes a course."""
        subject = f"{talent.full_name} ha completato il corso: {course_title}"
        content = (
            f"<h2 style='margin-top: 0;'>Corso completato!</h2>"
            f"<p>Ciao <strong>{company.full_name}</strong>,</p>"
            f"<p><strong>{talent.full_name}</strong> ha completato il corso "
            f"<strong>{course_title}</strong>.</p>"
            f"<p>XP totali del percorso: <strong>{proposal.total_xp or 0}</strong></p>"
            f"<p>Accedi alla dashboard per seguire i prossimi step.</p>"
            f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
        )
        return EmailService.send_email(
            db,
            recipient_id=company.id,
            email_type="course_completed",
            subject=subject,
            body_html=_email_wrapper(content),
            body_text=f"{talent.full_name} ha completato il corso: {course_title}.",
            related_proposal_id=proposal.id,
        )

    @staticmethod
    def send_milestone_reached(db: Session, proposal: Proposal, milestone_type: str, xp_earned: int, talent: User) -> EmailLog | None:
        """Email to TALENT when a milestone is reached."""
        subject = f"Traguardo raggiunto! +{xp_earned} XP"
        content = (
            f"<h2 style='margin-top: 0;'>Congratulazioni!</h2>"
            f"<p>Ciao <strong>{talent.full_name}</strong>,</p>"
            f"<p>Hai raggiunto un nuovo traguardo: <strong>{milestone_type}</strong></p>"
            f"<p>Hai guadagnato <strong>+{xp_earned} XP</strong>!</p>"
            f"<p>XP totali del percorso: <strong>{proposal.total_xp or 0}</strong></p>"
            f"<p>Continua cosi'!</p>"
            f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
        )
        return EmailService.send_email(
            db,
            recipient_id=talent.id,
            email_type="milestone_reached",
            subject=subject,
            body_html=_email_wrapper(content),
            body_text=f"Traguardo raggiunto: {milestone_type}. +{xp_earned} XP",
            related_proposal_id=proposal.id,
        )

    @staticmethod
    def send_hiring_confirmation(db: Session, proposal: Proposal, talent: User, company: User) -> list[EmailLog]:
        """Emails to BOTH talent and company when hiring is confirmed."""
        company_name = company.company_name or company.full_name
        results = []

        # Email to talent
        talent_subject = f"Congratulazioni! Sei stato assunto da {company_name}"
        talent_content = (
            f"<h2 style='margin-top: 0;'>Sei stato assunto!</h2>"
            f"<p>Ciao <strong>{talent.full_name}</strong>,</p>"
            f"<p>Congratulazioni! <strong>{company_name}</strong> ti ha assunto "
            f"dopo il completamento del percorso formativo.</p>"
            f"<p>XP totali guadagnati: <strong>{proposal.total_xp or 0}</strong></p>"
            f"<p>In bocca al lupo per la tua nuova avventura!</p>"
            f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
        )
        talent_email = EmailService.send_email(
            db,
            recipient_id=talent.id,
            email_type="hiring_confirmation",
            subject=talent_subject,
            body_html=_email_wrapper(talent_content),
            body_text=f"Congratulazioni! Sei stato assunto da {company_name}.",
            related_proposal_id=proposal.id,
        )
        if talent_email:
            results.append(talent_email)

        # Email to company
        company_subject = f"Assunzione confermata: {talent.full_name}"
        company_content = (
            f"<h2 style='margin-top: 0;'>Assunzione confermata</h2>"
            f"<p>Ciao <strong>{company.full_name}</strong>,</p>"
            f"<p>L'assunzione di <strong>{talent.full_name}</strong> e' stata confermata.</p>"
            f"<p>XP totali del percorso: <strong>{proposal.total_xp or 0}</strong></p>"
            f"<p>Benvenuto nel team!</p>"
            f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
        )
        company_email = EmailService.send_email(
            db,
            recipient_id=company.id,
            email_type="hiring_confirmation",
            subject=company_subject,
            body_html=_email_wrapper(company_content),
            body_text=f"Assunzione confermata: {talent.full_name}.",
            related_proposal_id=proposal.id,
        )
        if company_email:
            results.append(company_email)

        return results

    @staticmethod
    def generate_daily_digest(db: Session, user: User) -> EmailLog | None:
        """Generate a daily digest email with course/article suggestions.

        Checks daily_digest preference first.
        Uses AICache career_advice if available, otherwise falls back to recent courses.
        """
        # Check preference
        pref = db.query(NotificationPreference).filter(
            NotificationPreference.user_id == user.id,
        ).first()

        if pref and not pref.daily_digest:
            logger.info("daily_digest_disabled", user_id=user.id)
            return None

        # Try to use cached career advice for personalized suggestions
        now = datetime.now(timezone.utc)
        cache = db.query(AICache).filter(
            AICache.user_id == user.id,
            AICache.cache_type == "career_advice",
        ).first()

        suggestions_html = ""
        if cache:
            try:
                advice = json.loads(cache.content_json)
                courses_list = advice.get("recommended_courses", [])[:3]
                skill_gaps = advice.get("skill_gaps", [])[:5]
                career_direction = advice.get("career_direction", "")

                if career_direction:
                    suggestions_html += f"<p><strong>Direzione consigliata:</strong> {career_direction}</p>"

                if courses_list:
                    suggestions_html += "<h3>Corsi consigliati per te</h3><ul>"
                    for c in courses_list:
                        reason = c.get("reason", "")
                        course_id = c.get("course_id", "")
                        suggestions_html += f"<li><strong>{course_id}</strong> — {reason}</li>"
                    suggestions_html += "</ul>"

                if skill_gaps:
                    suggestions_html += "<h3>Competenze da sviluppare</h3><ul>"
                    for skill in skill_gaps:
                        suggestions_html += f"<li>{skill}</li>"
                    suggestions_html += "</ul>"
            except (json.JSONDecodeError, TypeError):
                cache = None

        # Fallback: 3 most recent courses
        if not suggestions_html:
            recent_courses = db.query(Course).filter(
                Course.is_active == 1,
            ).order_by(Course.created_at.desc()).limit(3).all()

            if recent_courses:
                suggestions_html += "<h3>Corsi in evidenza</h3><ul>"
                for course in recent_courses:
                    suggestions_html += (
                        f"<li><strong>{course.title}</strong> ({course.provider}) "
                        f"— Livello: {course.level}</li>"
                    )
                suggestions_html += "</ul>"
            else:
                suggestions_html += "<p>Nessun corso disponibile al momento. Torna a trovarci presto!</p>"

        subject = "Il tuo digest giornaliero — Datapizza"
        content = (
            f"<h2 style='margin-top: 0;'>Buongiorno {user.full_name}!</h2>"
            f"<p>Ecco il tuo digest giornaliero con suggerimenti personalizzati.</p>"
            f"{suggestions_html}"
            f"<p style='margin-top: 24px;'>Continua a formarti e resta aggiornato!</p>"
            f"<p style='margin-top: 24px; color: #6b7280; font-size: 14px;'>— Il team Datapizza</p>"
        )

        return EmailService.send_email(
            db,
            recipient_id=user.id,
            email_type="daily_digest",
            subject=subject,
            body_html=_email_wrapper(content),
            body_text=f"Digest giornaliero per {user.full_name}. Accedi per i dettagli.",
        )
