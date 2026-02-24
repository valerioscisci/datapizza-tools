'use client';

import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { ArrowRight } from 'lucide-react';

export function HeroSection() {
  const t = useTranslations();

  return (
    <section className="relative overflow-hidden bg-linear-to-b from-azure-25 to-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24 sm:py-32">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-4xl sm:text-5xl lg:text-6xl font-heading font-semibold text-black-950 leading-tight">
            {t('home.hero.title')}
          </h1>
          <p className="mt-6 text-lg sm:text-xl text-neutral-600 max-w-2xl mx-auto leading-relaxed">
            {t('home.hero.subtitle')}
          </p>
          <div className="mt-10 flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/it/jobs"
              className="inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors shadow-lg shadow-azure-600/25 cursor-pointer"
            >
              {t('home.hero.ctaTalents')}
              <ArrowRight className="w-5 h-5" />
            </Link>
            <Link
              href="/it/craft-your-developer"
              className="inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-white text-azure-600 font-medium rounded-xl border-2 border-azure-600 hover:bg-azure-25 transition-colors cursor-pointer"
            >
              {t('home.hero.ctaCompanies')}
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
