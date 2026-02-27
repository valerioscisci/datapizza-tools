'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import { Briefcase, ChevronDown } from 'lucide-react';
import { formatSalary, workModeLabel } from '@/lib/job-utils';
import { TechTag } from '@/components/ui/TechTag';
import { experienceLevelEmoji, matchBadgeStyle } from '../_utils/constants';
import { Badge } from './Badge';
import { JobCardProps } from './JobCard.props';

export function JobCard({ job, match, onClick }: JobCardProps) {
  const t = useTranslations('jobs');
  const salary = formatSalary(job.salary_min, job.salary_max, t);
  const [showTooltip, setShowTooltip] = useState(false);

  return (
    <div
      onClick={onClick}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick(); } }}
      tabIndex={0}
      role="button"
      className="relative p-6 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 hover:shadow-lg transition-all duration-300 cursor-pointer group"
    >
      {/* AI Match Score Badge */}
      {match && (
        <div
          className="absolute top-4 right-4 z-10"
          onMouseEnter={() => setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
          onFocus={() => setShowTooltip(true)}
          onBlur={() => setShowTooltip(false)}
          tabIndex={0}
          aria-describedby={showTooltip ? `match-tooltip-${job.id}` : undefined}
        >
          <span
            className={`inline-flex items-center gap-1 px-2.5 py-1 text-xs font-semibold rounded-full border ${matchBadgeStyle(match.score)}`}
          >
            {match.score}% {t('aiMatch.scoreLabel')}
          </span>

          {/* Tooltip with reasons */}
          {showTooltip && match.reasons.length > 0 && (
            <div
              id={`match-tooltip-${job.id}`}
              role="tooltip"
              className="absolute right-0 top-full mt-2 w-64 bg-white rounded-lg shadow-xl border border-neutral-200 p-3 z-20"
            >
              <p className="text-xs font-semibold text-neutral-700 mb-2">
                {t('aiMatch.reasons')}
              </p>
              <ul className="space-y-1">
                {match.reasons.map((reason) => (
                  <li key={reason} className="text-xs text-neutral-600 flex items-start gap-1.5">
                    <span className="text-azure-600 mt-0.5 shrink-0">&#8226;</span>
                    {reason}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}

      <div className="flex items-start gap-4">
        {/* Company Logo */}
        <div className="w-14 h-14 bg-neutral-100 rounded-full flex items-center justify-center shrink-0 border border-neutral-200">
          <Briefcase className="w-6 h-6 text-neutral-400" />
        </div>

        <div className="flex-1 min-w-0">
          {/* Title + Company */}
          <h3 className="text-lg font-semibold text-black-950 group-hover:text-azure-600 transition-colors">
            {experienceLevelEmoji(job.experience_level)} {job.title}
          </h3>
          <p className="text-sm text-azure-600 font-medium mt-0.5">{job.company}</p>
        </div>

        {/* Expand hint — shift left if match badge present */}
        {!match && (
          <ChevronDown className="w-5 h-5 text-neutral-300 group-hover:text-azure-400 transition-colors shrink-0 mt-1" />
        )}
      </div>

      {/* Info Badges */}
      <div className="flex flex-wrap gap-2 mt-4">
        {salary && <Badge variant="salary">{'\u{1F4B0}'} RAL {salary}</Badge>}
        {job.employment_type && <Badge variant="default">{job.employment_type === 'full-time' ? t('card.fullTime') : job.employment_type === 'part-time' ? t('card.partTime') : job.employment_type}</Badge>}
        {job.experience_years && <Badge variant="experience">{'\u{1F9D1}\u200D\u{1F4BC}'} {t('card.experienceLabel')} {job.experience_years}</Badge>}
        <Badge variant="work_mode">{'\u{1F465}'} {workModeLabel(job.work_mode, t)}</Badge>
      </div>

      <div className="flex flex-wrap gap-2 mt-2">
        <Badge variant="location">{'\u{1F4CD}'} {job.location}</Badge>
        {job.welfare && <Badge variant="welfare">{'\u{1F381}'} {job.welfare}</Badge>}
        {job.smart_working && <Badge variant="smart">{'\u{1F4BB}'} Smart {job.smart_working}</Badge>}
      </div>

      {job.language && (
        <div className="flex flex-wrap gap-2 mt-2">
          <Badge variant="language">{'\u{1F5E3}\uFE0F'} {job.language}</Badge>
        </div>
      )}

      {/* Tech Tags */}
      {job.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-4">
          {job.tags.map((tag, i) => (
            <TechTag key={tag} tag={tag} primary={i < 2} />
          ))}
        </div>
      )}

      {/* Description */}
      <p className="mt-4 text-sm text-neutral-500 line-clamp-3 leading-relaxed">
        {job.description}
      </p>
    </div>
  );
}
