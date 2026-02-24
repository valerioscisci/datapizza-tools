'use client';

import { useTranslations } from 'next-intl';

export function CraftHeroSection() {
  const t = useTranslations('craftYourDeveloper');

  return (
    <section className="relative overflow-hidden bg-linear-to-b from-azure-25 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
        <div className="max-w-4xl mx-auto text-center">
          <span className="inline-block px-4 py-1.5 bg-azure-50 text-azure-600 text-sm font-medium rounded-full mb-6">
            Per le Aziende
          </span>
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-heading font-semibold text-black-950 leading-tight">
            {t('hero.title')}
          </h1>
          <p className="mt-4 text-xl sm:text-2xl text-neutral-600 font-medium">
            {t('hero.subtitle')}
          </p>
          <p className="mt-6 text-lg text-neutral-500 max-w-3xl mx-auto leading-relaxed">
            {t('hero.description')}
          </p>
        </div>
      </div>
    </section>
  );
}
