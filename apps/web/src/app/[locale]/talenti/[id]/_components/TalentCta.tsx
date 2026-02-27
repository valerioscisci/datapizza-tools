'use client';

import { Users, Send } from 'lucide-react';
import Link from 'next/link';
import { TalentCtaProps } from './TalentCta.props';

export function TalentCta({ talentId, isCompany, isAuthenticated, t }: TalentCtaProps) {
  return (
    <div className="p-8 bg-azure-25 rounded-2xl border border-azure-200 text-center">
      {isCompany && isAuthenticated ? (
        <>
          <h2 className="text-2xl font-heading font-semibold text-black-950">
            {t('detail.proposeTraining')}
          </h2>
          <p className="mt-3 text-neutral-600 max-w-xl mx-auto">
            {t('detail.proposeTrainingDescription')}
          </p>
          <Link
            href={`/it/azienda/proposte/nuova?talent_id=${talentId}`}
            className="mt-6 inline-flex items-center gap-2 px-8 py-3.5 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer"
          >
            {t('detail.proposeTraining')}
            <Send className="w-5 h-5" aria-hidden="true" />
          </Link>
        </>
      ) : (
        <>
          <h2 className="text-2xl font-heading font-semibold text-black-950">
            {t('detail.interestedCta')}
          </h2>
          <p className="mt-3 text-neutral-600 max-w-xl mx-auto">
            {t('detail.interestedDescription')}
          </p>
          <Link
            href="/it/craft-your-developer"
            className="mt-6 inline-flex items-center gap-2 px-8 py-3.5 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer"
          >
            {t('detail.contactButton')}
            <Users className="w-5 h-5" aria-hidden="true" />
          </Link>
        </>
      )}
    </div>
  );
}
