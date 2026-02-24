'use client';

import { useTranslations } from 'next-intl';
import { useEffect, useState, useMemo } from 'react';
import { Loader2, Sparkles } from 'lucide-react';
import { useAuth } from '@/lib/auth/use-auth';
import { WORK_MODE_FILTERS } from '../_utils/constants';
import { useJobsData } from '../_hooks/useJobsData';
import { useAIJobMatch } from '../_hooks/useAIJobMatch';
import type { Job } from '../_utils/types';
import { JobCard } from './JobCard';
import { JobDetailDialog } from './JobDetailDialog';

export function JobsPage() {
  const t = useTranslations('jobs');
  const { isAuthenticated } = useAuth();
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState<string>('all');
  const [sortByMatch, setSortByMatch] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const { jobs, total, loading, fetchJobs } = useJobsData();
  const {
    loading: matchLoading,
    error: matchError,
    generatedAt,
    generateMatches,
    getMatchForJob,
    hasMatches,
  } = useAIJobMatch();

  useEffect(() => {
    fetchJobs(page, filter);
  }, [page, filter, fetchJobs]);

  // Sort jobs by match score when sortByMatch is active
  const displayJobs = useMemo(() => {
    if (!sortByMatch || !hasMatches) return jobs;
    return [...jobs].sort((a, b) => {
      const scoreA = getMatchForJob(a.id)?.score ?? -1;
      const scoreB = getMatchForJob(b.id)?.score ?? -1;
      return scoreB - scoreA;
    });
  }, [jobs, sortByMatch, hasMatches, getMatchForJob]);

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

      {/* Filters + Jobs */}
      <section className="py-8 sm:py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Filters Row */}
          <div className="flex flex-wrap items-center gap-2 mb-8">
            {WORK_MODE_FILTERS.map((mode) => (
              <button
                key={mode}
                onClick={() => { setFilter(mode); setPage(1); }}
                aria-pressed={filter === mode}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                  filter === mode
                    ? 'bg-azure-600 text-white'
                    : 'bg-white text-neutral-600 border border-neutral-200 hover:border-azure-300 hover:text-azure-600'
                }`}
              >
                {t(`filters.${mode}`)}
              </button>
            ))}

            {/* Sort by Best Match button — only when matches are loaded */}
            {hasMatches && (
              <button
                onClick={() => setSortByMatch((prev) => !prev)}
                aria-pressed={sortByMatch}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                  sortByMatch
                    ? 'bg-azure-600 text-white'
                    : 'bg-white text-neutral-600 border border-neutral-200 hover:border-azure-300 hover:text-azure-600'
                }`}
              >
                <span className="flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4" aria-hidden="true" />
                  {t('aiMatch.sortBestMatch')}
                </span>
              </button>
            )}

            {/* Spacer to push AI Match button to the right */}
            <div className="flex-1" />

            {/* AI Match Button — only visible when logged in */}
            {isAuthenticated && (
              <button
                onClick={generateMatches}
                disabled={matchLoading}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-azure-600 text-white hover:bg-azure-700 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {matchLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                    {t('aiMatch.loading')}
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" aria-hidden="true" />
                    {t('aiMatch.button')}
                  </>
                )}
              </button>
            )}
          </div>

          {/* Match error */}
          {matchError && (
            <div className="mb-4 px-4 py-2 rounded-lg bg-red-50 text-red-600 text-sm border border-red-200">
              {t('aiMatch.error')}
            </div>
          )}

          {/* Generated at info */}
          {generatedAt && (
            <div className="mb-4 px-4 py-2 rounded-lg bg-azure-50 text-azure-700 text-sm border border-azure-200 flex items-center gap-2">
              <Sparkles className="w-4 h-4" aria-hidden="true" />
              {t('aiMatch.generatedAt', {
                date: new Date(generatedAt).toLocaleDateString('it-IT', {
                  day: 'numeric',
                  month: 'long',
                  year: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                }),
              })}
            </div>
          )}

          {/* Job Cards */}
          <div aria-live="polite">
          {loading ? (
            <div className="text-center py-16">
              <p className="text-neutral-500">{t('loading')}</p>
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-16">
              <p className="text-neutral-500">{t('empty')}</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {displayJobs.map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  match={getMatchForJob(job.id)}
                  onClick={() => setSelectedJob(job)}
                />
              ))}
            </div>
          )}
          </div>

          {/* Pagination */}
          {total > 10 && (
            <div className="flex justify-center gap-2 mt-8">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 text-sm font-medium rounded-lg bg-white border border-neutral-200 text-neutral-600 hover:border-azure-300 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {t('pagination.previous')}
              </button>
              <span className="px-4 py-2 text-sm text-neutral-500">
                {t('pagination.page', { current: page, total: Math.ceil(total / 10) })}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(total / 10)}
                className="px-4 py-2 text-sm font-medium rounded-lg bg-white border border-neutral-200 text-neutral-600 hover:border-azure-300 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {t('pagination.next')}
              </button>
            </div>
          )}
        </div>
      </section>

      {/* Job Detail Dialog */}
      {selectedJob && (
        <JobDetailDialog
          job={selectedJob}
          match={getMatchForJob(selectedJob.id)}
          onClose={() => setSelectedJob(null)}
        />
      )}
    </>
  );
}
