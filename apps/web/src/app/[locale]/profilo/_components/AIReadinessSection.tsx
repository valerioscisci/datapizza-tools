'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import {
  Brain,
  ChevronDown,
  ChevronUp,
  RefreshCw,
  Loader2,
  AlertCircle,
  GraduationCap,
  ExternalLink,
} from 'lucide-react';
import { cn } from '@/lib/utils/utils';
import { useAIReadiness } from '../_hooks/useAIReadiness';
import { AIReadinessQuiz } from './AIReadinessQuiz';

function readinessLevelBadgeStyle(level: string): string {
  switch (level) {
    case 'beginner':
      return 'bg-red-50 text-red-600 border-red-200';
    case 'intermediate':
      return 'bg-yellow-50 text-yellow-600 border-yellow-200';
    case 'advanced':
      return 'bg-azure-50 text-azure-700 border-azure-300/30';
    case 'expert':
      return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
    default:
      return 'bg-neutral-100 text-neutral-600 border-neutral-200';
  }
}

function readinessLevelCircleColor(level: string): string {
  switch (level) {
    case 'beginner':
      return 'text-red-500';
    case 'intermediate':
      return 'text-yellow-500';
    case 'advanced':
      return 'text-azure-600';
    case 'expert':
      return 'text-pastelgreen-600';
    default:
      return 'text-neutral-400';
  }
}

function readinessLevelStrokeColor(level: string): string {
  switch (level) {
    case 'beginner':
      return 'stroke-red-500';
    case 'intermediate':
      return 'stroke-yellow-500';
    case 'advanced':
      return 'stroke-azure-600';
    case 'expert':
      return 'stroke-pastelgreen-600';
    default:
      return 'stroke-neutral-300';
  }
}

export function AIReadinessSection() {
  const t = useTranslations('profile.aiReadiness');

  const { readiness, suggestions, loading, error, submitQuiz } = useAIReadiness();
  const [expanded, setExpanded] = useState(false);
  const [showQuiz, setShowQuiz] = useState(false);

  const handleQuizSubmit = async (answers: Record<string, number>) => {
    await submitQuiz(answers);
    setShowQuiz(false);
  };

  // Circular progress SVG params
  const circleRadius = 40;
  const circleCircumference = 2 * Math.PI * circleRadius;
  const scorePercent = readiness?.total_score ?? 0;
  const strokeDashoffset = circleCircumference - (scorePercent / 100) * circleCircumference;

  return (
    <>
      <div className="border border-neutral-200 rounded-lg bg-white overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-5">
          <button
            onClick={() => setExpanded((prev) => !prev)}
            className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
          >
            <div className="w-10 h-10 bg-azure-50 rounded-full flex items-center justify-center shrink-0">
              <Brain className="w-5 h-5 text-azure-600" aria-hidden="true" />
            </div>
            <div className="text-left">
              <h3 className="text-lg font-semibold text-black-950">{t('title')}</h3>
              <p className="text-xs text-neutral-400 mt-0.5">{t('subtitle')}</p>
            </div>
            {expanded ? (
              <ChevronUp className="w-5 h-5 text-neutral-400 ml-2" aria-hidden="true" />
            ) : (
              <ChevronDown className="w-5 h-5 text-neutral-400 ml-2" aria-hidden="true" />
            )}
          </button>

          {/* Quiz CTA button */}
          <button
            onClick={() => setShowQuiz(true)}
            disabled={loading}
            className={cn(
              'inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer',
              loading
                ? 'bg-neutral-100 text-neutral-400 cursor-not-allowed'
                : 'bg-azure-600 text-white hover:bg-azure-700'
            )}
          >
            {loading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                {t('loading')}
              </>
            ) : readiness ? (
              <>
                <RefreshCw className="w-4 h-4" aria-hidden="true" />
                {t('retakeQuiz')}
              </>
            ) : (
              <>
                <Brain className="w-4 h-4" aria-hidden="true" />
                {t('takeQuiz')}
              </>
            )}
          </button>
        </div>

        {/* Collapsible content */}
        {expanded && (
          <div className="px-5 pb-5 space-y-6" aria-live="polite">
            {/* Error state */}
            {error && (
              <div className="flex items-start gap-3 p-4 bg-red-50 rounded-lg border border-red-200">
                <AlertCircle className="w-5 h-5 text-red-500 mt-0.5 shrink-0" aria-hidden="true" />
                <p className="text-sm text-red-700">{t('error')}</p>
              </div>
            )}

            {/* Loading state */}
            {loading && (
              <div className="space-y-4">
                <div className="animate-pulse rounded-lg bg-neutral-100 h-24" />
                <div className="animate-pulse rounded-lg bg-neutral-100 h-32" />
              </div>
            )}

            {/* Empty state — no assessment */}
            {!loading && !readiness && !error && (
              <div className="text-center py-8">
                <Brain className="w-10 h-10 text-neutral-300 mx-auto mb-3" aria-hidden="true" />
                <p className="text-base font-heading font-semibold text-neutral-700 mb-1">
                  {t('emptyState.title')}
                </p>
                <p className="text-sm text-neutral-500 mb-4">
                  {t('emptyState.description')}
                </p>
                <button
                  onClick={() => setShowQuiz(true)}
                  className="inline-flex items-center gap-2 px-5 py-2.5 text-sm font-medium rounded-lg bg-azure-600 text-white hover:bg-azure-700 transition-colors cursor-pointer"
                >
                  <Brain className="w-4 h-4" aria-hidden="true" />
                  {t('takeQuiz')}
                </button>
              </div>
            )}

            {/* Assessment results */}
            {!loading && readiness && (
              <>
                {/* Score display */}
                <div className="flex flex-col sm:flex-row items-center gap-6 p-4 rounded-lg bg-neutral-50 border border-neutral-100">
                  {/* Circular progress */}
                  <div className="relative w-28 h-28 shrink-0">
                    <svg className="w-28 h-28 -rotate-90" viewBox="0 0 100 100">
                      <circle
                        cx="50"
                        cy="50"
                        r={circleRadius}
                        fill="none"
                        stroke="currentColor"
                        strokeWidth="8"
                        className="text-neutral-200"
                      />
                      <circle
                        cx="50"
                        cy="50"
                        r={circleRadius}
                        fill="none"
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={circleCircumference}
                        strokeDashoffset={strokeDashoffset}
                        className={cn('transition-all duration-700 ease-out', readinessLevelStrokeColor(readiness.readiness_level))}
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className={cn('text-2xl font-heading font-semibold', readinessLevelCircleColor(readiness.readiness_level))}>
                        {readiness.total_score}%
                      </span>
                    </div>
                  </div>

                  {/* Score details */}
                  <div className="text-center sm:text-left">
                    <p className="text-sm text-neutral-500 mb-1">{t('score')}</p>
                    <div className="flex items-center gap-2 justify-center sm:justify-start">
                      <span
                        className={cn(
                          'inline-flex items-center px-3 py-1 text-sm font-medium rounded-full border',
                          readinessLevelBadgeStyle(readiness.readiness_level)
                        )}
                      >
                        {t(`levels.${readiness.readiness_level}` as Parameters<typeof t>[0])}
                      </span>
                    </div>
                    <p className="text-xs text-neutral-400 mt-2">
                      {t('quizVersion', { version: readiness.quiz_version })}
                    </p>
                  </div>
                </div>

                {/* Course suggestions */}
                {suggestions && suggestions.suggestions.length > 0 && (
                  <div>
                    <h4 className="text-sm font-semibold text-neutral-900 mb-1">
                      {t('suggestions.title')}
                    </h4>
                    {suggestions.weak_categories.length > 0 && (
                      <p className="text-xs text-neutral-500 mb-3">
                        {t('suggestions.subtitle', { categories: suggestions.weak_categories.join(', ') })}
                      </p>
                    )}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      {suggestions.suggestions.map((course) => (
                        <div
                          key={course.id}
                          className="p-4 rounded-lg border border-neutral-200 bg-white hover:border-azure-300 transition-colors"
                        >
                          <div className="flex items-start gap-2 mb-2">
                            <GraduationCap className="w-4 h-4 text-azure-600 mt-0.5 shrink-0" aria-hidden="true" />
                            <div className="min-w-0">
                              <p className="text-sm font-semibold text-neutral-900 line-clamp-2">
                                {course.title}
                              </p>
                              {course.provider && (
                                <p className="text-xs text-neutral-500 mt-0.5">
                                  {course.provider}
                                </p>
                              )}
                            </div>
                          </div>
                          <div className="flex items-center gap-2 mb-2">
                            <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full bg-azure-50 text-azure-700 border border-azure-300/30">
                              {course.level}
                            </span>
                            <span className="inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full bg-neutral-100 text-neutral-600 border border-neutral-200">
                              {course.category}
                            </span>
                          </div>
                          <a
                            href={course.url ?? '/it/courses'}
                            target={course.url ? '_blank' : undefined}
                            rel={course.url ? 'noopener noreferrer' : undefined}
                            className="inline-flex items-center gap-1.5 text-xs font-medium text-azure-600 hover:text-azure-700 cursor-pointer"
                          >
                            {t('suggestions.goToCourse')}
                            <ExternalLink className="w-3 h-3" aria-hidden="true" />
                          </a>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* No suggestions */}
                {suggestions && suggestions.suggestions.length === 0 && (
                  <div className="text-center py-4">
                    <p className="text-sm text-neutral-500">{t('suggestions.noCourses')}</p>
                  </div>
                )}
              </>
            )}
          </div>
        )}
      </div>

      {/* Quiz Modal */}
      {showQuiz && (
        <AIReadinessQuiz
          onSubmit={handleQuizSubmit}
          onClose={() => setShowQuiz(false)}
          loading={loading}
        />
      )}
    </>
  );
}
