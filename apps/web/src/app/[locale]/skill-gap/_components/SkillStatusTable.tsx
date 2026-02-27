'use client';

import { useTranslations } from 'next-intl';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { SkillStatusTableProps } from './SkillStatusTable.props';

function statusDot(status: 'green' | 'yellow' | 'red'): string {
  switch (status) {
    case 'green':
      return 'bg-emerald-500';
    case 'yellow':
      return 'bg-amber-500';
    case 'red':
      return 'bg-red-500';
  }
}

function statusLabel(status: 'green' | 'yellow' | 'red', t: (key: string) => string): string {
  switch (status) {
    case 'green':
      return t('statusGreen');
    case 'yellow':
      return t('statusYellow');
    case 'red':
      return t('statusRed');
  }
}

export function SkillStatusTable({ skills }: SkillStatusTableProps) {
  const t = useTranslations('skillGap.userSkills');

  if (skills.length === 0) {
    return (
      <div className="border border-neutral-200 rounded-lg bg-white p-6">
        <h3 className="text-lg font-semibold text-black-950 mb-1">{t('title')}</h3>
        <p className="text-sm text-neutral-500 mb-4">{t('subtitle')}</p>
        <p className="text-sm text-neutral-400 text-center py-8">{t('empty')}</p>
      </div>
    );
  }

  return (
    <div className="border border-neutral-200 rounded-lg bg-white p-6">
      <h3 className="text-lg font-semibold text-black-950 mb-1">{t('title')}</h3>
      <p className="text-sm text-neutral-500 mb-4">{t('subtitle')}</p>

      <div className="space-y-3">
        {skills.map((skill) => (
          <div
            key={skill.skill}
            className="flex items-center justify-between py-2.5 px-3 rounded-lg hover:bg-neutral-50 transition-colors"
          >
            {/* Skill name + status */}
            <div className="flex items-center gap-3 min-w-0 flex-1">
              <span className={`w-2.5 h-2.5 rounded-full shrink-0 ${statusDot(skill.demand_status)}`} />
              <span className="text-sm font-medium text-neutral-900 truncate">{skill.skill}</span>
              <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${
                skill.demand_status === 'green'
                  ? 'bg-emerald-50 text-emerald-700'
                  : skill.demand_status === 'yellow'
                    ? 'bg-amber-50 text-amber-700'
                    : 'bg-red-50 text-red-700'
              }`}>
                {statusLabel(skill.demand_status, t)}
              </span>
            </div>

            {/* Trend + job count */}
            <div className="flex items-center gap-4 shrink-0">
              <div className="flex items-center gap-1">
                {skill.trend_direction === 'up' ? (
                  <TrendingUp className="w-4 h-4 text-emerald-600" aria-hidden="true" />
                ) : skill.trend_direction === 'down' ? (
                  <TrendingDown className="w-4 h-4 text-red-600" aria-hidden="true" />
                ) : (
                  <Minus className="w-4 h-4 text-neutral-400" aria-hidden="true" />
                )}
                <span className={`text-xs font-medium ${
                  skill.trend_direction === 'up'
                    ? 'text-emerald-600'
                    : skill.trend_direction === 'down'
                      ? 'text-red-600'
                      : 'text-neutral-500'
                }`}>
                  {skill.trend_direction === 'up' ? '+' : ''}{skill.trend_percentage}%
                </span>
              </div>
              <span className="text-xs text-neutral-400">
                {t('inJobs', { count: String(skill.job_count) })}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
