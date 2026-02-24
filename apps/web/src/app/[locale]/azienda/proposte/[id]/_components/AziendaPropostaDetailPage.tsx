'use client';

import { useTranslations } from 'next-intl';
import { useParams, useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/use-auth';
import { useState, useEffect, useCallback, useRef } from 'react';
import Link from 'next/link';
import {
  ArrowLeft,
  Star,
  Loader2,
  Clock,
  Save,
  Calendar,
  UserCheck,
  PartyPopper,
} from 'lucide-react';
import {
  API_BASE,
  type Proposal,
  statusBadgeStyle,
  formatDate,
  milestoneColor,
} from '../../_utils/constants';
import { courseStatusIcon } from '../../../../proposte/_utils/courseStatusIcon';
import { ChatSection } from '../../../../proposte/[id]/_components/ChatSection';
import { HireConfirmationModal } from '../../_components/HireConfirmationModal';

export function AziendaPropostaDetailPage() {
  const t = useTranslations('proposals');
  const tStatus = useTranslations('proposals.status');
  const tMilestones = useTranslations('proposals.milestones');
  const tHire = useTranslations('proposals.hire');
  const params = useParams();
  const router = useRouter();
  const { user, accessToken, loading, isCompany } = useAuth();

  const [proposal, setProposal] = useState<Proposal | null>(null);
  const [fetching, setFetching] = useState(true);
  const [editingCourse, setEditingCourse] = useState<string | null>(null);
  const [instructionsState, setInstructionsState] = useState<Record<string, string>>({});
  const [deadlineState, setDeadlineState] = useState<Record<string, string>>({});
  const [savingInstructions, setSavingInstructions] = useState<Record<string, boolean>>({});
  const [hireModalOpen, setHireModalOpen] = useState(false);
  const [hireSuccess, setHireSuccess] = useState(false);
  const feedbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const proposalId = params.id as string;

  useEffect(() => {
    return () => {
      if (feedbackTimerRef.current) clearTimeout(feedbackTimerRef.current);
    };
  }, []);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/it/login');
    }
    if (!loading && user && !isCompany) {
      router.push(`/it/proposte/${proposalId}`);
    }
  }, [user, loading, router, isCompany, proposalId]);

  const fetchProposal = useCallback(async () => {
    if (!accessToken) return;
    setFetching(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/proposals/${proposalId}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error('Not found');
      const data: Proposal = await res.json();
      setProposal(data);
    } catch {
      setProposal(null);
    } finally {
      setFetching(false);
    }
  }, [accessToken, proposalId]);

  useEffect(() => {
    if (accessToken && isCompany) {
      fetchProposal();
    }
  }, [accessToken, isCompany, fetchProposal]);

  const handleSaveInstructions = async (courseId: string) => {
    if (!accessToken) return;
    const notes = instructionsState[courseId] ?? '';
    const deadline = deadlineState[courseId] || null;
    setSavingInstructions((prev) => ({ ...prev, [courseId]: true }));
    try {
      await fetch(`${API_BASE}/api/v1/proposals/${proposalId}/courses/${courseId}/company-update`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ company_notes: notes, deadline: deadline }),
      });
      fetchProposal();
    } catch {
      // Silently fail
    } finally {
      setSavingInstructions((prev) => ({ ...prev, [courseId]: false }));
      setEditingCourse(null);
    }
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

  const handleHireConfirm = async (hiringNotes: string) => {
    if (!accessToken || !proposal) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/proposals/${proposalId}`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: 'hired', hiring_notes: hiringNotes || null }),
      });
      if (res.ok) {
        setHireModalOpen(false);
        setHireSuccess(true);
        if (feedbackTimerRef.current) clearTimeout(feedbackTimerRef.current);
        feedbackTimerRef.current = setTimeout(() => setHireSuccess(false), 4000);
        fetchProposal();
      }
    } catch {
      // Silently fail
    }
  };

  if (loading || !user || !isCompany) return null;

  if (fetching) {
    return (
      <div className="flex items-center justify-center py-32">
        <Loader2 className="w-6 h-6 animate-spin text-azure-600" aria-hidden="true" />
      </div>
    );
  }

  if (!proposal) {
    return (
      <div className="max-w-5xl mx-auto px-4 py-16 text-center">
        <p className="text-neutral-500">{t('companyEmpty')}</p>
      </div>
    );
  }

  const completedCount = proposal.courses.filter((c) => c.is_completed).length;
  const totalCourses = proposal.courses.length;
  const progressPercent = totalCourses > 0 ? (completedCount / totalCourses) * 100 : 0;
  const budget = proposal.budget_range;

  return (
    <>
      {/* Header */}
      <section className="bg-linear-to-b from-azure-25 to-white py-12 sm:py-16">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Back link */}
          <Link
            href="/it/azienda/proposte"
            className="inline-flex items-center gap-1 text-sm text-azure-600 hover:text-azure-700 font-medium mb-6 cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" aria-hidden="true" />
            {t('detail.backToList')}
          </Link>

          {/* Success toast */}
          {hireSuccess && (
            <div className="mb-4 p-3 rounded-lg bg-emerald-50 border border-emerald-200 text-sm text-emerald-600 font-medium">
              {tHire('success')}
            </div>
          )}

          {/* Hired celebration */}
          {proposal.status === 'hired' && (
            <div className="bg-linear-to-r from-emerald-50 via-pastelgreen-100 to-emerald-50 rounded-2xl p-6 mb-6">
              <div className="flex items-center gap-3 mb-2">
                <PartyPopper className="w-8 h-8 text-emerald-600" aria-hidden="true" />
                <span className={`inline-flex items-center px-3 py-1 text-xs font-medium rounded-full border ${statusBadgeStyle('hired')}`}>
                  {tStatus('hired' as Parameters<typeof tStatus>[0])}
                </span>
              </div>
              <h1 className="text-2xl font-heading font-semibold text-emerald-700">
                {proposal.talent_name}
              </h1>
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
          )}

          {/* Talent info + status + hire button */}
          {proposal.status !== 'hired' && (
            <div className="flex items-start justify-between gap-4 flex-wrap">
              <div>
                <h1 className="text-3xl font-heading font-semibold text-black-950">
                  {proposal.talent_name}
                </h1>
                <p className="text-sm text-neutral-500 mt-1">{t('detail.title')}</p>
              </div>
              <div className="flex items-center gap-3 flex-wrap">
                {(proposal.status === 'accepted' || proposal.status === 'completed') && (
                  <button
                    onClick={() => setHireModalOpen(true)}
                    className="inline-flex items-center gap-1.5 px-5 py-2.5 text-sm font-medium bg-emerald-500 text-white rounded-xl hover:bg-emerald-600 transition-colors cursor-pointer"
                  >
                    <UserCheck className="w-4 h-4" aria-hidden="true" />
                    {tHire('button')}
                  </button>
                )}
                {budget && (
                  <span className="inline-flex items-center gap-1 px-3 py-1.5 text-sm font-medium rounded-full bg-yellow-50 text-yellow-500 border border-yellow-400/30">
                    {t('card.budget')}: {budget}
                  </span>
                )}
                <span className={`inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-full border ${statusBadgeStyle(proposal.status)}`}>
                  {tStatus(proposal.status as Parameters<typeof tStatus>[0])}
                </span>
              </div>
            </div>
          )}

          {/* XP + Milestones */}
          <div className="flex items-center gap-3 flex-wrap mt-4">
            {proposal.total_xp > 0 && (
              <span className="inline-flex items-center gap-1.5 px-3 py-1.5 text-base font-bold text-azure-600">
                <Star className="w-5 h-5 text-yellow-400 fill-yellow-400" aria-hidden="true" />
                {proposal.total_xp} {t('card.xp')}
              </span>
            )}
            {proposal.milestones.map((m) => (
              <span
                key={m.id}
                className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full border ${milestoneColor(m.milestone_type)}`}
              >
                {tMilestones(m.milestone_type as Parameters<typeof tMilestones>[0])}
              </span>
            ))}
          </div>

          {/* Progress bar */}
          {totalCourses > 0 && (
            <div className="mt-4">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs text-neutral-500 font-medium">{t('card.progress')}</span>
                <span className="text-xs text-neutral-500">
                  {t('card.coursesCompleted', { completed: completedCount, total: totalCourses })}
                </span>
              </div>
              <div className="w-full h-2.5 bg-neutral-200 rounded-full overflow-hidden">
                <div
                  className="h-full bg-pastelgreen-500 rounded-full transition-all duration-500"
                  style={{ width: `${progressPercent}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </section>

      {/* Learning Path */}
      <section className="py-8 sm:py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-xl font-heading font-semibold text-black-950 mb-6">
            {t('detail.learningPath')}
          </h2>

          {/* Timeline */}
          <div className="relative">
            {/* Timeline line */}
            <div className="absolute left-4 top-0 bottom-0 w-0.5 bg-neutral-200" />

            <div className="space-y-6">
              {[...proposal.courses]
                .sort((a, b) => a.order - b.order)
                .map((course) => {
                  const { bgClass, icon } = courseStatusIcon(course);
                  const isStarted = !!course.started_at;
                  const isEditing = editingCourse === course.course_id;

                  return (
                    <div key={course.id} className="relative pl-12">
                      {/* Timeline dot */}
                      <div className={`absolute left-2 top-3 w-5 h-5 rounded-full flex items-center justify-center z-10 ${bgClass}`}>
                        {icon}
                      </div>

                      {/* Course card */}
                      <div className="p-4 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 transition-colors">
                        <div className="flex items-start justify-between gap-3 flex-wrap">
                          <div className="flex-1 min-w-0">
                            <h3 className="text-base font-medium text-black-950">{course.course_title}</h3>
                            <div className="flex items-center gap-2 mt-1 flex-wrap">
                              {course.course_provider && (
                                <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full bg-neutral-100 text-neutral-600">
                                  {course.course_provider}
                                </span>
                              )}
                              {course.course_level && (
                                <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full bg-azure-50 text-azure-600">
                                  {course.course_level}
                                </span>
                              )}
                              {course.course_duration && (
                                <span className="text-xs text-neutral-500">{course.course_duration}</span>
                              )}
                              {course.course_category && (
                                <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full bg-fuchsia-50 text-fuchsia-600">
                                  {course.course_category}
                                </span>
                              )}
                            </div>
                          </div>

                          {/* Status + edit button */}
                          <div className="flex items-center gap-2 shrink-0">
                            {!isStarted && !course.is_completed && (
                              <span className="text-xs text-neutral-400">{t('detail.notStarted')}</span>
                            )}
                            {!course.is_completed && isStarted && (
                              <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full bg-azure-50 text-azure-600 border border-azure-300/30">
                                {t('card.inProgress')}
                              </span>
                            )}
                            {(proposal.status === 'accepted' || proposal.status === 'sent') && !course.is_completed && (
                              <button
                                onClick={() => toggleEditCourse(course.course_id, course.company_notes, course.deadline)}
                                className="px-3 py-1.5 text-xs font-medium text-azure-600 bg-azure-50 rounded-lg hover:bg-azure-100 transition-colors cursor-pointer"
                              >
                                {course.company_notes ? t('card.editInstructions') : t('card.addInstructions')}
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Deadline */}
                        {course.deadline && !isEditing && (
                          <div className="mt-2">
                            {course.is_overdue ? (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full bg-red-50 text-red-600 border border-red-200">
                                <Clock className="w-3 h-3" aria-hidden="true" />
                                {t('card.overdue')}
                              </span>
                            ) : course.days_remaining !== null ? (
                              <span className={`inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full ${
                                course.days_remaining < 3
                                  ? 'bg-yellow-50 text-yellow-500 border border-yellow-400/30'
                                  : 'bg-neutral-100 text-neutral-600 border border-neutral-200'
                              }`}>
                                <Clock className="w-3 h-3" aria-hidden="true" />
                                {t('card.deadlineIn', { days: course.days_remaining })}
                              </span>
                            ) : (
                              <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium rounded-full bg-neutral-100 text-neutral-600 border border-neutral-200">
                                <Clock className="w-3 h-3" aria-hidden="true" />
                                {t('card.deadline')}: {formatDate(course.deadline)}
                              </span>
                            )}
                          </div>
                        )}

                        {/* XP earned */}
                        {course.xp_earned > 0 && (
                          <div className="mt-2">
                            <span className="inline-flex items-center gap-1 text-xs font-medium text-azure-600">
                              <Star className="w-3 h-3 text-yellow-400 fill-yellow-400" aria-hidden="true" />
                              +{course.xp_earned} {t('card.xp')}
                            </span>
                          </div>
                        )}

                        {/* Talent notes (read-only for company) */}
                        {course.talent_notes && (
                          <div className="mt-3 p-2.5 bg-pastelgreen-100 rounded-lg border border-pastelgreen-500/20">
                            <p className="text-xs text-pastelgreen-600 font-medium mb-0.5">{t('card.talentNotes')}</p>
                            <p className="text-xs text-neutral-700">{course.talent_notes}</p>
                          </div>
                        )}

                        {/* Company notes display (when not editing) */}
                        {course.company_notes && !isEditing && (
                          <div className="mt-3 p-2.5 bg-azure-50 rounded-lg border border-azure-100">
                            <p className="text-xs text-azure-600 font-medium mb-0.5">{t('card.companyNotes')}</p>
                            <p className="text-xs text-neutral-700">{course.company_notes}</p>
                          </div>
                        )}

                        {/* Inline edit form for company notes + deadline */}
                        {isEditing && (
                          <div className="mt-3 p-3 bg-azure-25 rounded-lg border border-azure-100 space-y-2">
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
                    </div>
                  );
                })}
            </div>
          </div>

          {/* Chat Section */}
          {user && accessToken && (
            <ChatSection
              proposalId={proposalId}
              accessToken={accessToken}
              currentUserId={user.id}
              currentUserType="company"
              proposalStatus={proposal.status}
            />
          )}
        </div>
      </section>

      {/* Hire Confirmation Modal */}
      {hireModalOpen && proposal && (
        <HireConfirmationModal
          proposal={proposal}
          onConfirm={handleHireConfirm}
          onCancel={() => setHireModalOpen(false)}
          tHire={tHire}
        />
      )}
    </>
  );
}
