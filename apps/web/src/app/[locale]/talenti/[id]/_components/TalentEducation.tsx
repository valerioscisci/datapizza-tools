'use client';

import { GraduationCap } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { TalentEducationProps } from './TalentEducation.props';

export function TalentEducation({ educations, t, tProfile }: TalentEducationProps) {
  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200">
      <h2 className="text-xl font-heading font-semibold text-black-950 flex items-center gap-2 mb-4">
        <GraduationCap className="w-5 h-5 text-azure-600" aria-hidden="true" />
        {t('detail.education')}
      </h2>
      {educations.length > 0 ? (
        <div className="space-y-4">
          {educations.map((edu) => (
            <div
              key={edu.id}
              className="p-4 bg-neutral-50 rounded-xl border border-neutral-100"
            >
              <h3 className="text-base font-semibold text-black-950">
                {edu.institution}
              </h3>
              <div className="flex flex-wrap items-center gap-1 mt-1 text-sm text-neutral-500">
                {edu.degree_type && (
                  <span>{tProfile(`degree_types.${edu.degree_type}` as Parameters<typeof tProfile>[0])}</span>
                )}
                {edu.degree_type && (edu.degree || edu.field_of_study) && (
                  <span className="text-neutral-300">&middot;</span>
                )}
                {edu.degree && <span>{edu.degree}</span>}
                {edu.degree && edu.field_of_study && (
                  <span className="text-neutral-300">-</span>
                )}
                {edu.field_of_study && <span>{edu.field_of_study}</span>}
              </div>
              <p className="text-sm text-neutral-400 mt-1">
                {edu.start_year} -{' '}
                {edu.is_current ? t('detail.present') : edu.end_year || ''}
              </p>
              {edu.description && (
                <p className="text-sm text-neutral-600 mt-2 whitespace-pre-line">
                  {edu.description}
                </p>
              )}
            </div>
          ))}
        </div>
      ) : (
        <p className="text-sm text-neutral-400">{t('detail.noEducation')}</p>
      )}
    </div>
  );
}
