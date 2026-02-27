'use client';

import { User } from 'lucide-react';
import { TalentBioAndSkillsProps } from './TalentBioAndSkills.props';

export function TalentBioAndSkills({ talent, t }: TalentBioAndSkillsProps) {
  return (
    <>
      {/* Bio */}
      <div className="p-6 bg-white rounded-2xl border border-neutral-200">
        <h2 className="text-xl font-heading font-semibold text-black-950 flex items-center gap-2 mb-3">
          <User className="w-5 h-5 text-azure-600" aria-hidden="true" />
          {t('detail.bio')}
        </h2>
        {talent.bio ? (
          <p className="text-sm text-neutral-600 whitespace-pre-line">{talent.bio}</p>
        ) : (
          <p className="text-sm text-neutral-400">{t('detail.noBio')}</p>
        )}
      </div>

      {/* Skills */}
      <div className="p-6 bg-white rounded-2xl border border-neutral-200">
        <h2 className="text-xl font-heading font-semibold text-black-950 mb-4">
          {t('detail.skills')}
        </h2>
        {talent.skills.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {talent.skills.map((skill) => (
              <span
                key={skill}
                className="inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full border bg-azure-50 text-azure-700 border-azure-300/30"
              >
                {skill}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-neutral-400">{t('detail.noSkills')}</p>
        )}
      </div>
    </>
  );
}
