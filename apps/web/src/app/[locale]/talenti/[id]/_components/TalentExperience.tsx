'use client';

import { Briefcase, MapPin } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { Experience, formatMonthYear } from '../_utils/constants';

interface TalentExperienceProps {
  experiences: Experience[];
  t: ReturnType<typeof useTranslations>;
  tProfile: ReturnType<typeof useTranslations>;
}

export function TalentExperience({ experiences, t, tProfile }: TalentExperienceProps) {
  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200">
      <h2 className="text-xl font-heading font-semibold text-black-950 flex items-center gap-2 mb-4">
        <Briefcase className="w-5 h-5 text-azure-600" aria-hidden="true" />
        {t('detail.experience')}
      </h2>
      {experiences.length > 0 ? (
        <div className="space-y-4">
          {experiences.map((exp) => (
            <div
              key={exp.id}
              className="p-4 bg-neutral-50 rounded-xl border border-neutral-100"
            >
              <h3 className="text-base font-semibold text-black-950">
                {exp.company}{' '}
                <span className="font-normal text-neutral-500">&middot;</span>{' '}
                {exp.title}
              </h3>
              <div className="flex flex-wrap items-center gap-2 mt-1 text-sm text-neutral-500">
                {exp.employment_type && (
                  <span>{tProfile(`employment_types.${exp.employment_type}` as Parameters<typeof tProfile>[0])}</span>
                )}
                {exp.employment_type && exp.location && (
                  <span className="text-neutral-300">&middot;</span>
                )}
                {exp.location && (
                  <span className="flex items-center gap-1">
                    <MapPin className="w-3.5 h-3.5" aria-hidden="true" />
                    {exp.location}
                  </span>
                )}
              </div>
              <p className="text-sm text-neutral-400 mt-1">
                {formatMonthYear(exp.start_month, exp.start_year)} -{' '}
                {exp.is_current
                  ? t('detail.present')
                  : exp.end_year
                    ? formatMonthYear(exp.end_month, exp.end_year)
                    : ''}
              </p>
              {exp.description && (
                <p className="text-sm text-neutral-600 mt-2 whitespace-pre-line">
                  {exp.description}
                </p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-neutral-400">{t('detail.noExperience')}</p>
      )}
    </div>
  );
}
