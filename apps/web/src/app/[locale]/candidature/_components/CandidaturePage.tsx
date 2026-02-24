'use client';

import { useTranslations } from 'next-intl';
import { useAuth } from '@/lib/auth/use-auth';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Briefcase } from 'lucide-react';
import { STATUS_TABS, TAB_LABEL_MAP } from '../_utils/constants';
import { useCandidatureData } from '../_hooks/useCandidatureData';
import { ApplicationCard } from './ApplicationCard';

export function CandidaturePage() {
  const t = useTranslations('applications');
  const { user, accessToken, loading } = useAuth();
  const router = useRouter();

  const [activeTab, setActiveTab] = useState<string>('attiva');
  const { applications, counts, fetching, fetchApplications } = useCandidatureData();

  useEffect(() => {
    if (!loading && !user) {
      router.push('/it/login');
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (accessToken) {
      fetchApplications(activeTab, accessToken);
    }
  }, [activeTab, accessToken, fetchApplications]);

  if (loading || !user) return null;

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

      {/* Tabs + Applications */}
      <section className="py-8 sm:py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Tabs */}
          <div className="flex flex-wrap gap-2 mb-8">
            {STATUS_TABS.map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer flex items-center gap-2 ${
                  activeTab === tab
                    ? 'bg-azure-600 text-white'
                    : 'bg-white text-neutral-600 border border-neutral-200 hover:border-azure-300 hover:text-azure-600'
                }`}
              >
                {t(`tabs.${TAB_LABEL_MAP[tab]}`)}
                {(counts[tab] ?? 0) > 0 && (
                  <span className={`inline-flex items-center justify-center min-w-5 h-5 px-1.5 text-xs font-semibold rounded-full ${
                    activeTab === tab
                      ? 'bg-white/20 text-white'
                      : 'bg-azure-100 text-azure-700'
                  }`}>
                    {counts[tab]}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Application Cards */}
          {fetching ? (
            <div className="text-center py-16">
              <p className="text-neutral-500">{t('loading')}</p>
            </div>
          ) : applications.length === 0 ? (
            <div className="text-center py-16">
              <Briefcase className="w-12 h-12 text-neutral-300 mx-auto mb-4" />
              <p className="text-neutral-500">{t('empty')}</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {applications.map((app) => (
                <ApplicationCard key={app.id} app={app} />
              ))}
            </div>
          )}
        </div>
      </section>
    </>
  );
}
