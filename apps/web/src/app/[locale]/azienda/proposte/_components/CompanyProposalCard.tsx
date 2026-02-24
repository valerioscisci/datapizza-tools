'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { ChevronDown, ChevronUp, Check } from 'lucide-react';
import { type Proposal, statusBadgeStyle, formatBudget } from '../_utils/constants';

export interface CompanyProposalCardProps {
  proposal: Proposal;
  t: ReturnType<typeof useTranslations>;
  tStatus: ReturnType<typeof useTranslations>;
}

export function CompanyProposalCard({
  proposal,
  t,
  tStatus,
}: CompanyProposalCardProps) {
  const [expanded, setExpanded] = useState(false);
  const completedCount = proposal.courses.filter((c) => c.is_completed).length;
  const totalCourses = proposal.courses.length;
  const progressPercent = totalCourses > 0 ? (completedCount / totalCourses) * 100 : 0;
  const budget = formatBudget(proposal.budget_range);

  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 hover:shadow-lg transition-all duration-300">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-heading font-semibold text-black-950">
            {proposal.talent_name}
          </h3>
        </div>
        <span className={`inline-flex items-center px-3 py-1 text-xs font-medium rounded-full border shrink-0 ${statusBadgeStyle(proposal.status)}`}>
          {tStatus(proposal.status as Parameters<typeof tStatus>[0])}
        </span>
      </div>

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
            <div className="mt-2 space-y-2">
              {[...proposal.courses]
                .sort((a, b) => a.order - b.order)
                .map((course) => (
                  <div
                    key={course.id}
                    className="flex items-center gap-2 p-3 bg-neutral-50 rounded-xl border border-neutral-100"
                  >
                    <div className={`w-5 h-5 rounded-full flex items-center justify-center shrink-0 ${
                      course.is_completed
                        ? 'bg-pastelgreen-500 text-white'
                        : 'border-2 border-neutral-300'
                    }`}>
                      {course.is_completed && <Check className="w-3 h-3" aria-hidden="true" />}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium ${course.is_completed ? 'text-neutral-400 line-through' : 'text-black-950'}`}>
                        {course.course_title}
                      </p>
                      <div className="flex items-center gap-2 mt-0.5">
                        {course.course_provider && (
                          <span className="text-xs text-neutral-500">{course.course_provider}</span>
                        )}
                        {course.course_level && (
                          <span className="text-xs text-neutral-400">{course.course_level}</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
