'use client';

import { useTranslations } from 'next-intl';
import { Sparkles } from 'lucide-react';
import type { SkillGapInsightsProps } from './SkillGapInsights.props';

export function SkillGapInsights({ insights, aiUnavailable }: SkillGapInsightsProps) {
  const t = useTranslations('skillGap.insights');

  return (
    <div className="border border-azure-200 rounded-lg bg-azure-50 p-6">
      <div className="flex items-center gap-2 mb-3">
        <Sparkles className="w-5 h-5 text-azure-600" aria-hidden="true" />
        <h3 className="text-lg font-semibold text-azure-700">{t('title')}</h3>
      </div>

      {aiUnavailable ? (
        <p className="text-sm text-azure-600/70 italic">{t('unavailable')}</p>
      ) : insights ? (
        <div className="space-y-3">
          {insights.split('\n').filter(Boolean).map((paragraph, i) => (
            <p key={i} className="text-sm text-azure-700 leading-relaxed">
              {paragraph}
            </p>
          ))}
        </div>
      ) : (
        <p className="text-sm text-azure-600/70 italic">{t('empty')}</p>
      )}
    </div>
  );
}
