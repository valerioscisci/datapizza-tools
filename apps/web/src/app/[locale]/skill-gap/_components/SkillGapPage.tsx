'use client';

import { useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  Loader2,
  Sparkles,
  RefreshCw,
  AlertCircle,
  Info,
} from 'lucide-react';
import { useAuth } from '@/lib/auth/use-auth';
import { formatDate } from '@/lib/job-utils';
import { useSkillGapAnalysis } from '../_hooks/useSkillGapAnalysis';
import { SkillStatusTable } from './SkillStatusTable';
import { MissingSkillsSection } from './MissingSkillsSection';
import { MarketTrendsSection } from './MarketTrendsSection';
import { SkillGapInsights } from './SkillGapInsights';

export function SkillGapPage() {
  const t = useTranslations('skillGap');
  const { user, loading: authLoading, isCompany } = useAuth();
  const router = useRouter();
  const { analysis, courseDetails, loading, error, generate } = useSkillGapAnalysis();

  // Auth guard: redirect unauthenticated and company users
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/it/login');
    } else if (!authLoading && user && isCompany) {
      router.push('/it/azienda/proposte');
    }
  }, [user, authLoading, isCompany, router]);

  if (authLoading || !user || isCompany) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center gap-2 text-neutral-500">
          <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
          <span>{t('loading')}</span>
        </div>
      </div>
    );
  }

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

          {/* Generate / Regenerate button */}
          <div className="mt-8 flex items-center justify-center gap-4">
            <button
              onClick={() => { if (!loading) generate(); }}
              disabled={loading}
              className={`inline-flex items-center gap-2 px-6 py-3 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                loading
                  ? 'bg-neutral-100 text-neutral-400 cursor-not-allowed'
                  : 'bg-azure-600 text-white hover:bg-azure-700'
              }`}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                  {t('loading')}
                </>
              ) : (
                <>
                  {analysis ? (
                    <RefreshCw className="w-4 h-4" aria-hidden="true" />
                  ) : (
                    <Sparkles className="w-4 h-4" aria-hidden="true" />
                  )}
                  {analysis ? t('regenerate') : t('generate')}
                </>
              )}
            </button>
          </div>

          {/* Generated at timestamp */}
          {analysis?.generated_at && (
            <p className="mt-3 text-xs text-neutral-400">
              {t('generatedAt', { date: formatDate(analysis.generated_at, 'short') })}
            </p>
          )}
        </div>
      </section>

      {/* Content */}
      <section className="py-8 sm:py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* No skills warning */}
          {analysis?.no_skills_warning && (
            <div className="mb-6 p-4 rounded-lg bg-yellow-50 border border-yellow-200 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5 shrink-0" aria-hidden="true" />
              <div>
                <p className="text-sm font-semibold text-yellow-700">{t('noSkills.title')}</p>
                <p className="text-sm text-yellow-600 mt-0.5">{t('noSkills.description')}</p>
                <Link
                  href="/it/profilo"
                  className="inline-block mt-2 text-sm font-medium text-yellow-700 underline hover:text-yellow-800"
                >
                  {t('noSkills.cta')}
                </Link>
              </div>
            </div>
          )}

          {/* AI unavailable info */}
          {analysis?.ai_unavailable && (
            <div className="mb-6 p-4 rounded-lg bg-azure-50 border border-azure-200 flex items-center gap-3">
              <Info className="w-5 h-5 text-azure-600 shrink-0" aria-hidden="true" />
              <p className="text-sm text-azure-700">{t('aiUnavailable')}</p>
            </div>
          )}

          {/* Error state */}
          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 flex items-start gap-3">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 shrink-0" aria-hidden="true" />
              <div>
                <p className="text-sm text-red-700">{t('error')}</p>
                <button
                  onClick={generate}
                  className="mt-2 text-sm text-red-600 font-medium underline cursor-pointer"
                >
                  {t('regenerate')}
                </button>
              </div>
            </div>
          )}

          {/* Loading skeleton */}
          {loading && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="animate-pulse rounded-lg bg-neutral-100 h-64" />
              <div className="animate-pulse rounded-lg bg-neutral-100 h-64" />
              <div className="animate-pulse rounded-lg bg-neutral-100 h-64" />
              <div className="animate-pulse rounded-lg bg-neutral-100 h-64" />
            </div>
          )}

          {/* Analysis results */}
          {!loading && analysis && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Top-left: User Skills */}
              <SkillStatusTable skills={analysis.user_skills} />

              {/* Top-right: Missing Skills */}
              <MissingSkillsSection
                skills={analysis.missing_skills}
                courseDetails={courseDetails}
                userSkills={analysis.user_skills.map(s => s.skill)}
              />

              {/* Bottom-left: Market Trends */}
              <MarketTrendsSection trends={analysis.market_trends} />

              {/* Bottom-right: AI Insights */}
              <SkillGapInsights
                insights={analysis.personalized_insights}
                aiUnavailable={analysis.ai_unavailable}
              />
            </div>
          )}

          {/* Empty state — no analysis yet and not loading */}
          {!loading && !analysis && !error && (
            <div className="text-center py-16">
              <Sparkles className="w-12 h-12 text-neutral-300 mx-auto mb-4" aria-hidden="true" />
              <p className="text-sm text-neutral-500">{t('insights.empty')}</p>
            </div>
          )}
        </div>
      </section>
    </>
  );
}
