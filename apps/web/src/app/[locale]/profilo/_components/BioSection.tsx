'use client';

import { User } from 'lucide-react';
import { BioSectionProps } from './BioSection.props';

export function BioSection({ bio, t }: BioSectionProps) {
  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200">
      <h2 className="text-xl font-heading font-semibold text-black-950 flex items-center gap-2 mb-3">
        <User className="w-5 h-5 text-azure-600" aria-hidden="true" />
        {t('bio')}
      </h2>
      {bio ? (
        <p className="text-sm text-neutral-600 whitespace-pre-line">{bio}</p>
      ) : (
        <p className="text-sm text-neutral-400">{t('noBio')}</p>
      )}
    </div>
  );
}
