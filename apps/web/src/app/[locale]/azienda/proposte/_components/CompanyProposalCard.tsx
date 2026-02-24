'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import {
  ChevronDown,
  ChevronUp,
  Check,
  Star,
  Clock,
  Play,
  Save,
  Calendar,
  PartyPopper,
  UserCheck,
} from 'lucide-react';
import {
  type Proposal,
  type ProposalCourse,
  statusBadgeStyle,
  formatDate,
  milestoneColor,
} from '../_utils/constants';

export interface CompanyProposalCardProps {
  proposal: Proposal;
  onSaveCompanyUpdate: (proposalId: string, courseId: string, companyNotes: string, deadline: string | null) => void;
  onHire: (proposal: Proposal) => void;
  t: ReturnType<typeof useTranslations>;
  tStatus: ReturnType<typeof useTranslations>;
  tMilestones: ReturnType<typeof useTranslations>;
  tHire: ReturnType<typeof useTranslations>;
}

function DeadlineBadge({ course, t }: { course: ProposalCourse; t: ReturnType<typeof useTranslations> }) {
  if (!course.deadline) return null;

  if (course.is_overdue) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full bg-red-50 text-red-600 border border-red-200">
        <Clock className="w-3 h-3" aria-hidden="true" />
        {t('card.overdue')}
      </span>
    );
  }

  if (course.days_remaining !== null && course.days_remaining < 3) {
    return (
      <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full bg-yellow-50 text-yellow-500 border border-yellow-400/30">
        <Clock className="w-3 h-3" aria-hidden="true" />
        {t('card.deadlineIn', { days: course.days_remaining })}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full bg-neutral-100 text-neutral-600 border border-neutral-200">
      <Clock className="w-3 h-3" aria-hidden="true" />
      {t('card.deadline')}: {formatDate(course.deadline)}
    </span>
  );
}

export function CompanyProposalCard({
  proposal,
  onSaveCompanyUpdate,
  onHire,
  t,
  tStatus,
  tMilestones,
  tHire,
}: CompanyProposalCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [editingCourse, setEditingCourse] = useState<string | null>(null);
  const [instructionsState, setInstructionsState] = useState<Record<string, string>>({});
  const [deadlineState, setDeadlineState] = useState<Record<string, string>>({});
  const [savingInstructions, setSavingInstructions] = useState<Record<string, boolean>>({});

  const completedCount = proposal.courses.filter((c) => c.is_completed).length;
  const totalCourses = proposal.courses.length;
  const progressPercent = totalCourses > 0 ? (completedCount / totalCourses) * 100 : 0;
  const budget = proposal.budget_range;

  const handleSaveInstructions = async (courseId: string) => {
    const notes = instructionsState[courseId] ?? '';
    const deadline = deadlineState[courseId] || null;
    setSavingInstructions((prev) => ({ ...prev, [courseId]: true }));
    await onSaveCompanyUpdate(proposal.id, courseId, notes, deadline);
    setSavingInstructions((prev) => ({ ...prev, [courseId]: false }));
    setEditingCourse(null);
  };

  const toggleEditCourse = (courseId: string, currentNotes: string | null, currentDeadline: string | null) => {
    if (editingCourse === courseId) {
      setEditingCourse(null);
    } else {
      setEditingCourse(courseId);
      setInstructionsState((prev) => ({ ...prev, [courseId]: currentNotes ?? '' }));
      setDeadlineState((prev) => ({ ...prev, [courseId]: currentDeadline ?? '' }));
    }
  };

  // Hired state
  if (proposal.status === 'hired') {
    return (
      <div className="p-6 bg-white rounded-2xl border border-emerald-200 shadow-lg transition-all duration-300">
        <div className="bg-linear-to-r from-emerald-50 via-pastelgreen-100 to-emerald-50 rounded-xl p-6 mb-4">
          <div className="flex items-center gap-3 mb-2">
            <PartyPopper className="w-8 h-8 text-emerald-600" aria-hidden="true" />
            <div>
              <span className={`inline-flex items-center px-3 py-1 text-xs font-medium rounded-full border ${statusBadgeStyle('hired')}`}>
                {tStatus('hired' as Parameters<typeof tStatus>[0])}
              </span>
            </div>
          </div>
          <h3 className="text-lg font-heading font-semibold text-emerald-700">
            {proposal.talent_name}
          </h3>
          {proposal.hired_at && (
            <p className="text-sm text-emerald-500 mt-1">
              {tHire('hiredAt', { date: formatDate(proposal.hired_at) })}
            </p>
          )}
          {proposal.hiring_notes && (
            <div className="mt-3 p-3 bg-white/60 rounded-lg">
              <p className="text-xs text-emerald-600 font-medium mb-1">{tHire('hiredNotes')}</p>
              <p className="text-sm text-neutral-700">{proposal.hiring_notes}</p>
            </div>
          )}
        </div>

        {/* XP + Milestones */}
        <div className="flex items-center gap-3 flex-wrap">
          {proposal.total_xp > 0 && (
            <span className="inline-flex items-center gap-1 px-2.5 py-1 text-sm font-semibold text-azure-600">
              <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" aria-hidden="true" />
              {proposal.total_xp} {t('card.xp')}
            </span>
          )}
          {proposal.milestones.map((m) => (
            <span
              key={m.id}
              className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full border ${milestoneColor(m.milestone_type)}`}
            >
              {tMilestones(m.milestone_type as Parameters<typeof tMilestones>[0])}
            </span>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 hover:shadow-lg transition-all duration-300">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <Link
            href={`/it/azienda/proposte/${proposal.id}`}
            className="text-lg font-heading font-semibold text-black-950 hover:text-azure-600 transition-colors cursor-pointer"
          >
            {proposal.talent_name}
          </Link>
        </div>
        <div className="flex items-center gap-2 shrink-0">
          {proposal.total_xp > 0 && (
            <span className="inline-flex items-center gap-1 px-2 py-1 text-xs font-semibold text-azure-600">
              <Star className="w-3.5 h-3.5 text-yellow-400 fill-yellow-400" aria-hidden="true" />
              {proposal.total_xp} {t('card.xp')}
            </span>
          )}
          <span className={`inline-flex items-center px-3 py-1 text-xs font-medium rounded-full border ${statusBadgeStyle(proposal.status)}`}>
            {tStatus(proposal.status as Parameters<typeof tStatus>[0])}
          </span>
        </div>
      </div>

      {/* Hire button */}
      {(proposal.status === 'accepted' || proposal.status === 'completed') && (
        <div className="mt-3">
          <button
            onClick={() => onHire(proposal)}
            className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 transition-colors cursor-pointer"
          >
            <UserCheck className="w-4 h-4" aria-hidden="true" />
            {tHire('button')}
          </button>
        </div>
      )}

      {/* Message */}
      {proposal.message && (
        <p className="mt-3 text-sm text-neutral-600 line-clamp-2">
          {proposal.message}
        </p>
      )}

      {/* Budget */}
      {budget && (
        <div className="mt-3">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full bg-yellow-50 text-yellow-500 border border-yellow-400/30">
            {t('card.budget')}: {budget}
          </span>
        </div>
      )}

      {/* Progress */}
      {totalCourses > 0 && (
        <div className="mt-4">
          <div className="flex items-center justify-between mb-1.5">
            <span className="text-xs text-neutral-500 font-medium">{t('card.progress')}</span>
            <span className="text-xs text-neutral-500">
              {t('card.coursesCompleted', { completed: completedCount, total: totalCourses })}
            </span>
          </div>
          <div className="w-full h-2 bg-neutral-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-pastelgreen-500 rounded-full transition-all duration-500"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>
      )}

      {/* Milestone badges */}
      {proposal.milestones.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {proposal.milestones.map((m) => (
            <span
              key={m.id}
              className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full border ${milestoneColor(m.milestone_type)}`}
            >
              {tMilestones(m.milestone_type as Parameters<typeof tMilestones>[0])}
            </span>
          ))}
        </div>
      )}

      {/* Expandable courses */}
      {totalCourses > 0 && (
        <div className="mt-4">
          <button
            onClick={() => setExpanded(!expanded)}
            className="flex items-center gap-1 text-sm text-azure-600 hover:text-azure-700 font-medium cursor-pointer"
          >
            {t('card.courses')} ({totalCourses})
            {expanded ? (
              <ChevronUp className="w-4 h-4" aria-hidden="true" />
            ) : (
              <ChevronDown className="w-4 h-4" aria-hidden="true" />
            )}
          </button>

          {expanded && (
            <div className="mt-2 space-y-3">
              {[...proposal.courses]
                .sort((a, b) => a.order - b.order)
                .map((course) => {
                  const isStarted = !!course.started_at;
                  const isEditing = editingCourse === course.course_id;

                  return (
                    <div
                      key={course.id}
                      className="p-3 bg-neutral-50 rounded-xl border border-neutral-100"
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2 flex-1 min-w-0">
                          <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${
                            course.is_completed
                              ? 'bg-pastelgreen-500 text-white'
                              : isStarted
                                ? 'bg-azure-500 text-white'
                                : 'border-2 border-neutral-300'
                          }`}>
                            {course.is_completed && <Check className="w-3 h-3" aria-hidden="true" />}
                            {!course.is_completed && isStarted && <Play className="w-2.5 h-2.5" aria-hidden="true" />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className={`text-sm font-medium ${course.is_completed ? 'text-neutral-400 line-through' : 'text-black-950'}`}>
                              {course.course_title}
                            </p>
                            <div className="flex items-center gap-2 mt-0.5 flex-wrap">
                              {course.course_provider && (
                                <span className="text-xs text-neutral-500">{course.course_provider}</span>
                              )}
                              {course.course_level && (
                                <span className="text-xs text-neutral-400">{course.course_level}</span>
                              )}
                              {!course.is_completed && isStarted && (
                                <span className="inline-flex items-center px-1.5 py-0.5 text-xs font-medium rounded-full bg-azure-50 text-azure-600 border border-azure-300/30">
                                  {t('card.inProgress')}
                                </span>
                              )}
                              <DeadlineBadge course={course} t={t} />
                            </div>
                          </div>
                        </div>

                        {/* Add/Edit instructions button */}
                        {(proposal.status === 'accepted' || proposal.status === 'sent') && !course.is_completed && (
                          <button
                            onClick={() => toggleEditCourse(course.course_id, course.company_notes, course.deadline)}
                            className="px-3 py-1.5 text-xs font-medium text-azure-600 bg-azure-50 rounded-lg hover:bg-azure-100 transition-colors cursor-pointer shrink-0 ml-2"
                          >
                            {course.company_notes ? t('card.editInstructions') : t('card.addInstructions')}
                          </button>
                        )}
                      </div>

                      {/* Talent notes (read-only for company) */}
                      {course.talent_notes && (
                        <div className="mt-2 p-2.5 bg-pastelgreen-100 rounded-lg border border-pastelgreen-500/20">
                          <p className="text-xs text-pastelgreen-600 font-medium mb-0.5">{t('card.talentNotes')}</p>
                          <p className="text-xs text-neutral-700">{course.talent_notes}</p>
                        </div>
                      )}

                      {/* Company notes display (when not editing) */}
                      {course.company_notes && !isEditing && (
                        <div className="mt-2 p-2.5 bg-azure-50 rounded-lg border border-azure-100">
                          <p className="text-xs text-azure-600 font-medium mb-0.5">{t('card.companyNotes')}</p>
                          <p className="text-xs text-neutral-700">{course.company_notes}</p>
                        </div>
                      )}

                      {/* Inline edit form for company notes + deadline */}
                      {isEditing && (
                        <div className="mt-2 p-3 bg-azure-25 rounded-lg border border-azure-100 space-y-2">
                          <textarea
                            value={instructionsState[course.course_id] ?? ''}
                            onChange={(e) => setInstructionsState((prev) => ({ ...prev, [course.course_id]: e.target.value }))}
                            placeholder={t('card.companyNotes')}
                            className="w-full p-2 text-xs border border-neutral-200 rounded-lg resize-none focus:outline-none focus:border-azure-400 focus:ring-1 focus:ring-azure-400"
                            rows={3}
                          />
                          <div className="flex items-center gap-2">
                            <Calendar className="w-3.5 h-3.5 text-neutral-400" aria-hidden="true" />
                            <label htmlFor={`deadline-${course.course_id}`} className="text-xs text-neutral-600 font-medium">{t('card.deadlineLabel')}:</label>
                            <input
                              id={`deadline-${course.course_id}`}
                              type="date"
                              value={deadlineState[course.course_id] ?? ''}
                              onChange={(e) => setDeadlineState((prev) => ({ ...prev, [course.course_id]: e.target.value }))}
                              className="px-2 py-1 text-xs border border-neutral-200 rounded-lg focus:outline-none focus:border-azure-400 focus:ring-1 focus:ring-azure-400"
                            />
                          </div>
                          <button
                            onClick={() => handleSaveInstructions(course.course_id)}
                            disabled={savingInstructions[course.course_id]}
                            className="inline-flex items-center gap-1 px-3 py-1.5 text-xs font-medium bg-azure-600 text-white rounded-lg hover:bg-azure-700 transition-colors cursor-pointer disabled:opacity-50"
                          >
                            <Save className="w-3 h-3" aria-hidden="true" />
                            {t('card.saveInstructions')}
                          </button>
                        </div>
                      )}
                    </div>
                  );
                })}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
