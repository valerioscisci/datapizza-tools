'use client';

import { useTranslations } from 'next-intl';
import { ArrowRight } from 'lucide-react';

export function CraftCtaSection() {
  const t = useTranslations('craftYourDeveloper');

  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-linear-to-r from-azure-600 to-azure-700 rounded-3xl p-12 sm:p-16 text-center">
          <h2 className="text-3xl sm:text-4xl font-heading font-semibold text-white">
            {t('cta.title')}
          </h2>
          <p className="mt-4 text-azure-100 text-lg max-w-2xl mx-auto">
            {t('cta.description')}
          </p>
          <a
            href="https://datapizza.tech/it#contatti"
            target="_blank"
            rel="noopener noreferrer"
            className="mt-8 inline-flex items-center gap-2 px-8 py-3.5 bg-white text-azure-600 font-medium rounded-xl hover:bg-azure-50 transition-colors cursor-pointer"
          >
            {t('cta.button')}
            <ArrowRight className="w-5 h-5" />
          </a>
        </div>
      </div>
    </section>
  );
}
