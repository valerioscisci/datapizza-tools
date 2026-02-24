'use client';

import { useTranslations } from 'next-intl';
import { Search, PenTool, BookOpen, UserCheck } from 'lucide-react';

const steps = [
  { key: 'step1', icon: Search, number: '01' },
  { key: 'step2', icon: PenTool, number: '02' },
  { key: 'step3', icon: BookOpen, number: '03' },
  { key: 'step4', icon: UserCheck, number: '04' },
];

export function HowItWorksSection() {
  const t = useTranslations('craftYourDeveloper');

  return (
    <section className="py-20 bg-azure-25">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-3xl sm:text-4xl font-heading font-semibold text-black-950 text-center mb-16">
          {t('howItWorks.title')}
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {steps.map(({ key, icon: Icon, number }) => (
            <div key={key} className="relative p-8 bg-white rounded-2xl border border-neutral-200">
              <span className="text-5xl font-heading font-semibold text-azure-100">
                {number}
              </span>
              <div className="mt-4 w-10 h-10 bg-azure-600 rounded-lg flex items-center justify-center">
                <Icon className="w-5 h-5 text-white" />
              </div>
              <h3 className="mt-4 text-lg font-semibold text-black-950">
                {t(`howItWorks.${key}.title`)}
              </h3>
              <p className="mt-2 text-sm text-neutral-600 leading-relaxed">
                {t(`howItWorks.${key}.description`)}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
