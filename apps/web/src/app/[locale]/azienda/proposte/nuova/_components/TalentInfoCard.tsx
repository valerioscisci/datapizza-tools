'use client';

import { User, Briefcase, MapPin, Loader2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { TalentInfo } from '../_utils/constants';

interface TalentInfoCardProps {
  talent: TalentInfo | null;
  loadingTalent: boolean;
  t: ReturnType<typeof useTranslations>;
  tTalents: ReturnType<typeof useTranslations>;
}

export function TalentInfoCard({ talent, loadingTalent, t, tTalents }: TalentInfoCardProps) {
  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200">
      <h2 className="text-xl font-heading font-semibold text-black-950 flex items-center gap-2 mb-4">
        <User className="w-5 h-5 text-azure-600" aria-hidden="true" />
        {t('talentInfo')}
      </h2>
      {loadingTalent ? (
        <div className="flex items-center gap-2 text-neutral-500">
          <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
          <span>{tTalents('loading')}</span>
        </div>
      ) : talent ? (
        <div className="flex items-start gap-4">
          <div className="w-14 h-14 bg-azure-100 rounded-full flex items-center justify-center text-xl font-heading font-semibold text-azure-700 shrink-0">
            {talent.full_name.charAt(0).toUpperCase()}
          </div>
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-black-950">{talent.full_name}</h3>
            {talent.current_role && (
              <p className="text-sm text-azure-600 font-medium mt-0.5 flex items-center gap-1">
                <Briefcase className="w-3.5 h-3.5" aria-hidden="true" />
                {talent.current_role}
              </p>
            )}
            {talent.location && (
              <p className="text-sm text-neutral-500 mt-0.5 flex items-center gap-1">
                <MapPin className="w-3.5 h-3.5" aria-hidden="true" />
                {talent.location}
              </p>
            )}
            {talent.skills.length > 0 && (
              <div className="flex flex-wrap gap-1.5 mt-3">
                {talent.skills.map((skill) => (
                  <span
                    key={skill}
                    className="inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full border bg-azure-50 text-azure-700 border-azure-300/30"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            )}
          </div>
        </div>
      ) : (
        <p className="text-sm text-neutral-400">{tTalents('notFound')}</p>
      )}
    </div>
  );
}
