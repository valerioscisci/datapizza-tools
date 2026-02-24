'use client';

import Link from 'next/link';
import { Briefcase, Building2 } from 'lucide-react';

export function HomeCtaSection() {
  return (
    <section className="py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="bg-linear-to-r from-azure-600 to-azure-700 rounded-3xl p-12 sm:p-16 text-center">
          <h2 className="text-3xl sm:text-4xl font-heading font-semibold text-white">
            Pronto a fare il prossimo passo?
          </h2>
          <p className="mt-4 text-azure-100 text-lg max-w-2xl mx-auto">
            Che tu sia un&apos;azienda in cerca di talenti o un developer in cerca di nuove opportunita&apos;, Datapizza e&apos; qui per te.
          </p>
          <div className="mt-8 flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/it/jobs"
              className="inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-white text-azure-600 font-medium rounded-xl hover:bg-azure-50 transition-colors cursor-pointer"
            >
              <Briefcase className="w-5 h-5" />
              Cerca Lavoro
            </Link>
            <Link
              href="/it/craft-your-developer"
              className="inline-flex items-center justify-center gap-2 px-8 py-3.5 bg-azure-500 text-white font-medium rounded-xl border-2 border-azure-400 hover:bg-azure-400 transition-colors cursor-pointer"
            >
              <Building2 className="w-5 h-5" />
              Per le Aziende
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
