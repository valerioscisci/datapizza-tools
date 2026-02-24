'use client';

import { useTranslations } from 'next-intl';

export function StatsSection() {
  const t = useTranslations();

  return (
    <section className="bg-black-950 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 text-center">
          <div>
            <p className="text-4xl sm:text-5xl font-heading font-semibold text-azure-400">
              150+
            </p>
            <p className="mt-2 text-neutral-300 font-medium">
              {t('home.stats.jobsAvailable')}
            </p>
          </div>
          <div>
            <p className="text-4xl sm:text-5xl font-heading font-semibold text-azure-400">
              100+
            </p>
            <p className="mt-2 text-neutral-300 font-medium">
              {t('home.stats.companiesActive')}
            </p>
          </div>
          <div>
            <p className="text-4xl sm:text-5xl font-heading font-semibold text-azure-400">
              50k+
            </p>
            <p className="mt-2 text-neutral-300 font-medium">
              {t('home.stats.developersHelped')}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}
