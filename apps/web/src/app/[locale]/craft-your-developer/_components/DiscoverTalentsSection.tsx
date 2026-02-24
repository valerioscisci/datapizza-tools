'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { Users } from 'lucide-react';

export function DiscoverTalentsSection() {
  const t = useTranslations('craftYourDeveloper');

  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <h2 className="text-3xl sm:text-4xl font-heading font-semibold text-black-950">
          {t('talents.title')}
        </h2>
        <p className="mt-4 text-lg text-neutral-600 max-w-2xl mx-auto">
          {t('talents.description')}
        </p>
        <Link
          href="/it/talenti"
          className="mt-8 inline-flex items-center gap-2 px-8 py-3.5 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer"
        >
          {t('talents.button')}
          <Users className="w-5 h-5" aria-hidden="true" />
        </Link>
      </div>
    </section>
  );
}
