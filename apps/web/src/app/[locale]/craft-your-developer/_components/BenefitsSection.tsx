'use client';

import { useTranslations } from 'next-intl';
import { Target, Wallet, ShieldCheck, Zap } from 'lucide-react';

const benefits = [
  {
    key: 'targeted',
    icon: Target,
  },
  {
    key: 'cost',
    icon: Wallet,
  },
  {
    key: 'quality',
    icon: ShieldCheck,
  },
  {
    key: 'speed',
    icon: Zap,
  },
];

export function BenefitsSection() {
  const t = useTranslations('craftYourDeveloper');

  return (
    <section className="py-20 sm:py-28">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl sm:text-4xl font-heading font-semibold text-black-950 text-center mb-16">
          {t('whyTitle')}
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {benefits.map(({ key, icon: Icon }) => (
            <div
              key={key}
              className="p-8 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 hover:shadow-lg transition-all duration-300"
            >
              <div className="w-12 h-12 bg-azure-50 rounded-xl flex items-center justify-center mb-5">
                <Icon className="w-6 h-6 text-azure-600" />
              </div>
              <h3 className="text-xl font-semibold text-black-950">
                {t(`benefits.${key}.title`)}
              </h3>
              <p className="mt-3 text-neutral-600 leading-relaxed">
                {t(`benefits.${key}.description`)}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
