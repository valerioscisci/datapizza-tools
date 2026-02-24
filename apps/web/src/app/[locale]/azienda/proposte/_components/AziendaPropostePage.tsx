'use client';

import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/use-auth';
import { useState, useEffect, useCallback } from 'react';
import { Briefcase, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { API_BASE, STATUS_TABS, type ProposalListResponse, type Proposal } from '../_utils/constants';
import { CompanyProposalCard } from './CompanyProposalCard';

export function AziendaPropostePage() {
  const t = useTranslations('proposals');
  const tStatus = useTranslations('proposals.status');
  const router = useRouter();
  const { user, accessToken, loading, isCompany } = useAuth();

  const [activeTab, setActiveTab] = useState<string>('all');
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [fetching, setFetching] = useState(true);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/it/login');
    }
    if (!loading && user && !isCompany) {
      router.push('/it/proposte');
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
    if (accessToken && isCompany) {
      fetchProposals();
    }
  }, [accessToken, isCompany, fetchProposals]);

  if (loading || !user || !isCompany) return null;

  return (
    <>
      {/* Header */}
      <section className="bg-linear-to-b from-azure-25 to-white py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-heading font-semibold text-black-950">
            {t('companyTitle')}
          </h1>
          <p className="mt-4 text-lg text-neutral-600 max-w-2xl mx-auto">
            {t('companySubtitle')}
          </p>
        </div>
      </section>

      {/* Tabs + Proposals */}
      <section className="py-8 sm:py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
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
                <p className="text-neutral-500 font-medium">{t('companyEmpty')}</p>
                <p className="text-neutral-400 text-sm mt-2">{t('companyEmptyDescription')}</p>
                <Link
                  href="/it/talenti"
                  className="mt-4 inline-flex items-center px-6 py-3 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer"
                >
                  {t('companyEmptyButton')}
                </Link>
              </div>
            ) : (
              <div className="grid grid-cols-1 gap-4">
                {proposals.map((proposal) => (
                  <CompanyProposalCard
                    key={proposal.id}
                    proposal={proposal}
                    t={t}
                    tStatus={tStatus}
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
