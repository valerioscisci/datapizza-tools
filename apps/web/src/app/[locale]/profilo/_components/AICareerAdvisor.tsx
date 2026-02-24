'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import {
  ChevronDown,
  ChevronUp,
  Sparkles,
  Loader2,
  ExternalLink,
  AlertCircle,
  GraduationCap,
  Newspaper,
  Target,
  RefreshCw,
} from 'lucide-react';
import { formatDate } from '@/lib/job-utils';
import { useAICareerAdvice } from '../_hooks/useAICareerAdvice';
import type { ProfileResponse } from '../_utils/constants';

interface AICareerAdvisorProps {
  profile: ProfileResponse;
}

function levelBadgeStyle(level?: string): string {
  switch (level) {
    case 'beginner':
      return 'bg-pastelgreen-100 text-pastelgreen-600';
    case 'intermediate':
      return 'bg-azure-50 text-azure-700';
    case 'advanced':
      return 'bg-red-50 text-red-600';
    default:
      return 'bg-neutral-100 text-neutral-600';
  }
}

export function AICareerAdvisor({ profile }: AICareerAdvisorProps) {
  const t = useTranslations('profile.aiAdvisor');
  const tLevels = useTranslations('courses.levels');
  const [expanded, setExpanded] = useState(false);
  const { advice, loading, error, generateAdvice } = useAICareerAdvice();

  const hasSkills = profile.skills && profile.skills.length > 0;

  function levelLabel(level?: string): string {
    if (!level) return '';
    try {
      return tLevels(level);
    } catch {
      return level;
    }
  }

  return (
    <div className="border border-neutral-200 rounded-lg bg-white overflow-hidden">
      {/* Header — expand/collapse + generate button side by side */}
      <div className="flex items-center justify-between p-5">
        <button
          onClick={() => setExpanded((prev) => !prev)}
          className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
        >
          <div className="w-10 h-10 bg-azure-50 rounded-full flex items-center justify-center shrink-0">
            <Sparkles className="w-5 h-5 text-azure-600" aria-hidden="true" />
          </div>
          <div className="text-left">
            <h3 className="text-lg font-semibold text-black-950">{t('title')}</h3>
            {advice?.generated_at && (
              <p className="text-xs text-neutral-400 mt-0.5">
                {t('generatedAt', {
                  date: formatDate(advice.generated_at, 'short'),
                })}
              </p>
            )}
          </div>
          {expanded ? (
            <ChevronUp className="w-5 h-5 text-neutral-400 ml-2" aria-hidden="true" />
          ) : (
            <ChevronDown className="w-5 h-5 text-neutral-400 ml-2" aria-hidden="true" />
          )}
        </button>

        {/* Generate / Regenerate — separate button, not nested */}
        {hasSkills && (
          <button
            onClick={() => { if (!loading) generateAdvice(); }}
            disabled={loading}
            className={`inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
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
                {advice ? (
                  <RefreshCw className="w-4 h-4" aria-hidden="true" />
                ) : (
                  <Sparkles className="w-4 h-4" aria-hidden="true" />
                )}
                {advice ? t('regenerate') : t('generate')}
              </>
            )}
          </button>
        )}
      </div>

      {/* Collapsible content */}
      {expanded && (
        <div className="px-5 pb-5 space-y-6" aria-live="polite">
          {/* No skills message */}
          {!hasSkills && (
            <div className="flex items-start gap-3 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
              <AlertCircle className="w-5 h-5 text-yellow-500 mt-0.5 shrink-0" aria-hidden="true" />
              <p className="text-sm text-yellow-700">{t('noSkills')}</p>
            </div>
          )}

          {/* Error state */}
          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-50 rounded-lg border border-red-200">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 shrink-0" aria-hidden="true" />
              <div>
                <p className="text-sm text-red-700">{t('error')}</p>
                <button
                  onClick={generateAdvice}
                  className="mt-2 text-sm text-red-600 font-medium underline cursor-pointer"
                >
                  {t('regenerate')}
                </button>
              </div>
            </div>
          )}

          {/* Loading state */}
          {loading && (
            <div className="space-y-4">
              <div className="animate-pulse rounded-lg bg-neutral-100 h-24" />
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="animate-pulse rounded-lg bg-neutral-100 h-32" />
                <div className="animate-pulse rounded-lg bg-neutral-100 h-32" />
                <div className="animate-pulse rounded-lg bg-neutral-100 h-32" />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="animate-pulse rounded-lg bg-neutral-100 h-32" />
                <div className="animate-pulse rounded-lg bg-neutral-100 h-32" />
                <div className="animate-pulse rounded-lg bg-neutral-100 h-32" />
              </div>
            </div>
          )}

          {/* Advice content */}
          {!loading && advice && (
            <>
              {/* Career Direction */}
              <div className="p-4 rounded-lg bg-azure-50 border border-azure-200">
                <div className="flex items-center gap-2 mb-2">
                  <Target className="w-5 h-5 text-azure-600" aria-hidden="true" />
                  <h4 className="text-sm font-semibold text-azure-700">
                    {t('careerDirection')}
                  </h4>
                </div>
                <p className="text-sm text-azure-700 leading-relaxed">
                  {advice.career_direction}
                </p>
              </div>

              {/* Skill Gaps */}
              {advice.skill_gaps.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-neutral-900 mb-3">
                    {t('skillGaps')}
                  </h4>
                  <div className="flex flex-wrap gap-2">
                    {advice.skill_gaps.map((gap) => (
                      <span
                        key={gap}
                        className="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-full bg-red-50 text-red-600 border border-red-200"
                      >
                        {gap}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommended Courses */}
              {advice.recommended_courses.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-neutral-900 mb-3">
                    {t('recommendedCourses')}
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {advice.recommended_courses.map((course) => (
                      <div
                        key={course.course_id}
                        className="p-4 rounded-lg border border-neutral-200 bg-white hover:border-azure-300 transition-colors"
                      >
                        <div className="flex items-start gap-2 mb-2">
                          <GraduationCap className="w-4 h-4 text-azure-600 mt-0.5 shrink-0" aria-hidden="true" />
                          <div className="min-w-0">
                            <p className="text-sm font-semibold text-neutral-900 line-clamp-2">
                              {course.title ?? `Corso ${course.course_id.slice(0, 8)}`}
                            </p>
                            {course.provider && (
                              <p className="text-xs text-neutral-500 mt-0.5">
                                {course.provider}
                              </p>
                            )}
                          </div>
                        </div>
                        {course.level && (
                          <span
                            className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full mb-2 ${levelBadgeStyle(course.level)}`}
                          >
                            {levelLabel(course.level)}
                          </span>
                        )}
                        <p className="text-xs text-neutral-600 leading-relaxed mb-3">
                          <span className="font-medium text-neutral-500">
                            {t('reason')}:
                          </span>{' '}
                          {course.reason}
                        </p>
                        <a
                          href="/it/courses"
                          className="inline-flex items-center gap-1.5 text-xs font-medium text-azure-600 hover:text-azure-700 cursor-pointer"
                        >
                          {t('goToCourse')}
                          <GraduationCap className="w-3 h-3" aria-hidden="true" />
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Recommended Articles */}
              {advice.recommended_articles.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-neutral-900 mb-3">
                    {t('recommendedArticles')}
                  </h4>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    {advice.recommended_articles.map((article) => (
                      <div
                        key={article.news_id}
                        className="p-4 rounded-lg border border-neutral-200 bg-white hover:border-azure-300 transition-colors"
                      >
                        <div className="flex items-start gap-2 mb-2">
                          <Newspaper className="w-4 h-4 text-azure-600 mt-0.5 shrink-0" aria-hidden="true" />
                          <div className="min-w-0">
                            <p className="text-sm font-semibold text-neutral-900 line-clamp-2">
                              {article.title ?? `Articolo ${article.news_id.slice(0, 8)}`}
                            </p>
                            {article.source && (
                              <p className="text-xs text-neutral-500 mt-0.5">
                                {article.source}
                              </p>
                            )}
                          </div>
                        </div>
                        <p className="text-xs text-neutral-600 leading-relaxed mb-3">
                          <span className="font-medium text-neutral-500">
                            {t('reason')}:
                          </span>{' '}
                          {article.reason}
                        </p>
                        <a
                          href={article.source_url ?? '/it/news'}
                          target={article.source_url ? '_blank' : undefined}
                          rel={article.source_url ? 'noopener noreferrer' : undefined}
                          className="inline-flex items-center gap-1.5 text-xs font-medium text-azure-600 hover:text-azure-700 cursor-pointer"
                        >
                          {t('readArticle')}
                          <ExternalLink className="w-3 h-3" aria-hidden="true" />
                        </a>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}

          {/* Empty state — has skills but no advice generated and not loading */}
          {!loading && !advice && !error && hasSkills && (
            <div className="text-center py-8">
              <Sparkles className="w-8 h-8 text-neutral-300 mx-auto mb-3" aria-hidden="true" />
              <p className="text-sm text-neutral-500">{t('fillProfile')}</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
