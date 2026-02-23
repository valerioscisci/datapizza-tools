'use client';

import { useTranslations } from 'next-intl';
import { useAuth } from '@/lib/auth/use-auth';
import { useRouter } from 'next/navigation';
import { useEffect, useState, useCallback } from 'react';
import { Briefcase, Calendar } from 'lucide-react';
import { formatSalary, formatDate, workModeLabel } from '@/lib/job-utils';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

interface ApplicationJob {
  id: string;
  title: string;
  company: string;
  location: string;
  work_mode: string;
  salary_min: number | null;
  salary_max: number | null;
  tags: string[];
  experience_level: string;
  experience_years: string | null;
  smart_working: string | null;
  welfare: string | null;
}

interface Application {
  id: string;
  job: ApplicationJob;
  status: string;
  status_detail: string | null;
  recruiter_name: string | null;
  recruiter_role: string | null;
  applied_at: string;
  updated_at: string | null;
}

interface ApplicationListResponse {
  items: Application[];
  total: number;
  counts: Record<string, number>;
}

const STATUS_TABS = ['proposta', 'da_completare', 'attiva', 'archiviata'] as const;

const TAB_LABEL_MAP: Record<string, string> = {
  proposta: 'proposte',
  da_completare: 'da_completare',
  attiva: 'attive',
  archiviata: 'archiviate',
};

function statusBadgeStyle(status: string): string {
  switch (status) {
    case 'attiva': return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
    case 'proposta': return 'bg-azure-50 text-azure-700 border-azure-300/30';
    case 'da_completare': return 'bg-yellow-50 text-yellow-500 border-yellow-400/30';
    case 'archiviata': return 'bg-neutral-100 text-neutral-500 border-neutral-300/30';
    default: return 'bg-neutral-100 text-neutral-600 border-neutral-200';
  }
}

function ApplicationCard({ app }: { app: Application }) {
  const t = useTranslations('applications');
  const salary = formatSalary(app.job.salary_min, app.job.salary_max);

  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 hover:shadow-lg transition-all duration-300">
      <div className="flex items-start gap-4">
        {/* Company Logo Placeholder */}
        <div className="w-14 h-14 bg-neutral-100 rounded-full flex items-center justify-center shrink-0 border border-neutral-200">
          <Briefcase className="w-6 h-6 text-neutral-400" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="text-lg font-semibold text-black-950">{app.job.title}</h3>
              <p className="text-sm text-azure-600 font-medium mt-0.5">{app.job.company}</p>
            </div>
            {/* Status Badge */}
            <span className={`inline-flex items-center px-3 py-1 text-xs font-medium rounded-full border shrink-0 ${statusBadgeStyle(app.status)}`}>
              {app.status_detail || app.status}
            </span>
          </div>
        </div>
      </div>

      {/* Info Badges */}
      <div className="flex flex-wrap gap-2 mt-4">
        {salary && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full border bg-yellow-50 text-yellow-500 border-yellow-400/30">
            💰 RAL {salary}
          </span>
        )}
        {app.job.experience_years && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full border bg-azure-50 text-azure-700 border-azure-300/30">
            🧑‍💼 {app.job.experience_years}
          </span>
        )}
        <span className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full border bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30">
          👥 {workModeLabel(app.job.work_mode)}
        </span>
      </div>

      {/* Tech Tags */}
      {app.job.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {app.job.tags.map((tag, i) => (
            <span
              key={tag}
              className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full border ${
                i < 2
                  ? 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30'
                  : 'bg-neutral-100 text-neutral-600 border-neutral-200'
              }`}
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Status Detail Box */}
      <div className="mt-4 pt-4 border-t border-neutral-100">
        <div className="flex items-center justify-between">
          <div>
            {app.recruiter_name && (
              <p className="text-sm text-neutral-700">
                <span className="font-medium">{app.recruiter_name}</span>
                {app.recruiter_role && (
                  <span className="text-neutral-400 ml-1">- {app.recruiter_role}</span>
                )}
              </p>
            )}
          </div>
          <div className="flex items-center gap-1 text-xs text-neutral-400">
            <Calendar className="w-3.5 h-3.5" />
            {formatDate(app.applied_at)}
          </div>
        </div>
      </div>
    </div>
  );
}

export default function CandidaturePage() {
  const t = useTranslations('applications');
  const { user, accessToken, loading } = useAuth();
  const router = useRouter();

  const [activeTab, setActiveTab] = useState<string>('attiva');
  const [applications, setApplications] = useState<Application[]>([]);
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [fetching, setFetching] = useState(true);

  const fetchApplications = useCallback(async (status: string) => {
    if (!accessToken) return;
    setFetching(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/applications?status=${status}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error('Failed to fetch');
      const data: ApplicationListResponse = await res.json();
      setApplications(data.items);
      setCounts(data.counts);
    } catch {
      setApplications([]);
    } finally {
      setFetching(false);
    }
  }, [accessToken]);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/it/login');
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (accessToken) {
      fetchApplications(activeTab);
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
