'use client';

import { useTranslations } from 'next-intl';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import type { MarketTrendsSectionProps } from './MarketTrendsSection.props';

function barColor(direction: 'up' | 'down' | 'stable'): string {
  switch (direction) {
    case 'up':
      return 'bg-emerald-500';
    case 'down':
      return 'bg-red-400';
    case 'stable':
      return 'bg-neutral-300';
  }
}

export function MarketTrendsSection({ trends }: MarketTrendsSectionProps) {
  const t = useTranslations('skillGap.marketTrends');

  const maxJobCount = trends.length > 0 ? Math.max(...trends.map(tr => tr.job_count)) : 1;
  const totalJobs = trends.reduce((sum, tr) => sum + tr.job_count, 0);

  return (
    <div className="border border-neutral-200 rounded-lg bg-white p-6">
      <div className="flex items-center justify-between mb-1">
        <h3 className="text-lg font-semibold text-black-950">{t('title')}</h3>
      </div>
      <p className="text-sm text-neutral-500 mb-1">{t('subtitle')}</p>
      <p className="text-xs text-neutral-400 mb-4">
        {t('totalJobs', { count: String(totalJobs) })}
      </p>

      <div className="space-y-2.5">
        {trends.length === 0 && (
          <p className="text-sm text-neutral-400 py-4 text-center">{t('empty')}</p>
        )}
        {trends.map((trend, index) => {
          const barWidth = Math.max((trend.job_count / maxJobCount) * 100, 4);
          return (
            <div key={trend.skill} className="flex items-center gap-3">
              {/* Rank */}
              <span className="text-xs font-medium text-neutral-400 w-6 text-right shrink-0">
                {t('rank', { rank: String(index + 1) })}
              </span>

              {/* Skill name */}
              <span className="text-sm font-medium text-neutral-900 w-28 truncate shrink-0">
                {trend.skill}
              </span>

              {/* Bar indicator */}
              <div className="flex-1 h-5 bg-neutral-100 rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all ${barColor(trend.direction)}`}
                  style={{ width: `${barWidth}%` }}
                />
              </div>

              {/* Trend direction + percentage */}
              <div className="flex items-center gap-1 shrink-0 w-16 justify-end">
                {trend.direction === 'up' ? (
                  <TrendingUp className="w-3.5 h-3.5 text-emerald-600" aria-hidden="true" />
                ) : trend.direction === 'down' ? (
                  <TrendingDown className="w-3.5 h-3.5 text-red-600" aria-hidden="true" />
                ) : (
                  <Minus className="w-3.5 h-3.5 text-neutral-400" aria-hidden="true" />
                )}
                <span className={`text-xs font-medium ${
                  trend.direction === 'up'
                    ? 'text-emerald-600'
                    : trend.direction === 'down'
                      ? 'text-red-600'
                      : 'text-neutral-500'
                }`}>
                  {trend.direction === 'up' ? '+' : ''}{trend.change_percentage}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
