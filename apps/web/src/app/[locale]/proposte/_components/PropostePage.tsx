'use client';

import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/use-auth';
import { useState, useEffect, useCallback, useRef } from 'react';
import { Briefcase, Loader2 } from 'lucide-react';
import { API_BASE, STATUS_TABS, type ProposalListResponse, type Proposal } from '../_utils/constants';
import { ProposalCard } from './ProposalCard';

export function PropostePage() {
  const t = useTranslations('proposals');
  const tStatus = useTranslations('proposals.status');
  const tMilestones = useTranslations('proposals.milestones');
  const tHire = useTranslations('proposals.hire');
  const router = useRouter();
  const { user, accessToken, loading, isCompany } = useAuth();

  const [activeTab, setActiveTab] = useState<string>('all');
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [fetching, setFetching] = useState(true);
  const [actionFeedback, setActionFeedback] = useState<'error' | null>(null);
  const feedbackTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Cleanup feedback timer on unmount
  useEffect(() => {
    return () => {
      if (feedbackTimerRef.current) clearTimeout(feedbackTimerRef.current);
    };
  }, []);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/it/login');
    }
    if (!loading && isCompany) {
      router.push('/it/azienda/proposte');
    }
  }, [user, loading, router, isCompany]);

  const fetchProposals = useCallback(async () => {
    if (!accessToken) return;
    setFetching(true);
    try {
      const params = new URLSearchParams();
      if (activeTab !== 'all') {
        params.set('status', activeTab);
      }
      const res = await fetch(`${API_BASE}/api/v1/proposals?${params}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error('Failed to fetch');
      const data: ProposalListResponse = await res.json();
      setProposals(data.items);
    } catch {
      setProposals([]);
    } finally {
      setFetching(false);
    }
  }, [accessToken, activeTab]);

  useEffect(() => {
    if (accessToken && !isCompany) {
      fetchProposals();
    }
  }, [accessToken, isCompany, fetchProposals]);

  const showErrorFeedback = useCallback(() => {
    setActionFeedback('error');
    if (feedbackTimerRef.current) clearTimeout(feedbackTimerRef.current);
    feedbackTimerRef.current = setTimeout(() => setActionFeedback(null), 3000);
  }, []);

  const handleAccept = async (id: string) => {
    if (!accessToken) return;
    setActionFeedback(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/proposals/${id}`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: 'accepted' }),
      });
      if (res.ok) {
        fetchProposals();
      } else {
        showErrorFeedback();
      }
    } catch {
      showErrorFeedback();
    }
  };

  const handleReject = async (id: string) => {
    if (!accessToken) return;
    setActionFeedback(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/proposals/${id}`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status: 'rejected' }),
      });
      if (res.ok) {
        fetchProposals();
      } else {
        showErrorFeedback();
      }
    } catch {
      showErrorFeedback();
    }
  };

  const handleMarkCourseComplete = async (proposalId: string, courseId: string) => {
    if (!accessToken) return;
    setActionFeedback(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/proposals/${proposalId}/courses/${courseId}`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      if (res.ok) {
        fetchProposals();
      } else {
        showErrorFeedback();
      }
    } catch {
      showErrorFeedback();
    }
  };

  const handleStartCourse = async (proposalId: string, courseId: string) => {
    if (!accessToken) return;
    setActionFeedback(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/proposals/${proposalId}/courses/${courseId}/start`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });
      if (res.ok) {
        fetchProposals();
      } else {
        showErrorFeedback();
      }
    } catch {
      showErrorFeedback();
    }
  };

  const handleSaveTalentNotes = async (proposalId: string, courseId: string, notes: string) => {
    if (!accessToken) return;
    setActionFeedback(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/proposals/${proposalId}/courses/${courseId}/notes`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ talent_notes: notes }),
      });
      if (res.ok) {
        fetchProposals();
      } else {
        showErrorFeedback();
      }
    } catch {
      showErrorFeedback();
    }
  };

  if (loading || !user || isCompany) return null;

  return (
    <>
      {/* Header */}
      <section className="bg-linear-to-b from-azure-25 to-white py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-heading font-semibold text-black-950">
            {t('title')}
          </h1>
          <p className="mt-4 text-lg text-neutral-600 max-w-2xl mx-auto">
            {t('subtitle')}
          </p>
        </div>
      </section>

      {/* Tabs + Proposals */}
      <section className="py-8 sm:py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Action feedback */}
          {actionFeedback === 'error' && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-600">
              {t('create.error' as Parameters<typeof t>[0])}
            </div>
          )}

          {/* Tabs */}
          <div className="flex flex-wrap gap-2 mb-8">
            {STATUS_TABS.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                aria-pressed={activeTab === tab}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer flex items-center gap-2 ${
                  activeTab === tab
                    ? 'bg-azure-600 text-white'
                    : 'bg-white text-neutral-600 border border-neutral-200 hover:border-azure-300 hover:text-azure-600'
                }`}
              >
                {t(`tabs.${tab}` as Parameters<typeof t>[0])}
              </button>
            ))}
          </div>

          {/* Proposal Cards */}
          <div aria-live="polite">
            {fetching ? (
              <div className="text-center py-16">
                <div className="flex items-center justify-center gap-2 text-neutral-500">
                  <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
                  <span>{t('loading')}</span>
                </div>
              </div>
            ) : proposals.length === 0 ? (
              <div className="text-center py-16">
                <Briefcase className="w-12 h-12 text-neutral-300 mx-auto mb-4" aria-hidden="true" />
                <p className="text-neutral-500 font-medium">{t('empty')}</p>
                <p className="text-neutral-400 text-sm mt-2">{t('emptyDescription')}</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {proposals.map((proposal) => (
                  <ProposalCard
                    key={proposal.id}
                    proposal={proposal}
                    onAccept={handleAccept}
                    onReject={handleReject}
                    onMarkCourseComplete={handleMarkCourseComplete}
                    onStartCourse={handleStartCourse}
                    onSaveTalentNotes={handleSaveTalentNotes}
                    t={t}
                    tStatus={tStatus}
                    tMilestones={tMilestones}
                    tHire={tHire}
                  />
                ))}
              </div>
            )}
          </div>
        </div>
      </section>
    </>
  );
}
