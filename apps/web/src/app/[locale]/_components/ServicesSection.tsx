'use client';

import Link from 'next/link';
import { ArrowRight, Target, Briefcase, GraduationCap } from 'lucide-react';

export function ServicesSection() {
  return (
    <section className="py-20 sm:py-28">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center max-w-3xl mx-auto mb-16">
          <h2 className="text-3xl sm:text-4xl font-heading font-semibold text-black-950">
            Generiamo impatto tramite Tecnologia, Persone e AI
          </h2>
          <p className="mt-4 text-lg text-neutral-600">
            Soluzioni concrete per navigare il mercato del lavoro tech nell&apos;era dell&apos;intelligenza artificiale.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {/* Craft Your Developer Card */}
          <Link
            href="/it/craft-your-developer"
            className="group p-8 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 hover:shadow-xl hover:shadow-azure-600/5 transition-all duration-300"
          >
            <div className="w-12 h-12 bg-azure-50 rounded-xl flex items-center justify-center mb-5">
              <Target className="w-6 h-6 text-azure-600" />
            </div>
            <h3 className="text-xl font-semibold text-black-950 group-hover:text-azure-600 transition-colors">
              Craft Your Developer
            </h3>
            <p className="mt-3 text-neutral-600 leading-relaxed">
              Non cercare il developer perfetto. Seleziona un professionista esperto e formalo sulle competenze AI specifiche di cui hai bisogno.
            </p>
            <span className="inline-flex items-center gap-1 mt-5 text-sm font-medium text-azure-600 group-hover:gap-2 transition-all">
              Scopri di piu&apos;
              <ArrowRight className="w-4 h-4" />
            </span>
          </Link>

          {/* Jobs Market Card */}
          <Link
            href="/it/jobs"
            className="group p-8 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 hover:shadow-xl hover:shadow-azure-600/5 transition-all duration-300"
          >
            <div className="w-12 h-12 bg-azure-50 rounded-xl flex items-center justify-center mb-5">
              <Briefcase className="w-6 h-6 text-azure-600" />
            </div>
            <h3 className="text-xl font-semibold text-black-950 group-hover:text-azure-600 transition-colors">
              Mercato del Lavoro
            </h3>
            <p className="mt-3 text-neutral-600 leading-relaxed">
              Trova la tua prossima opportunita' nel tech. Offerte selezionate dalle migliori aziende italiane e internazionali.
            </p>
            <span className="inline-flex items-center gap-1 mt-5 text-sm font-medium text-azure-600 group-hover:gap-2 transition-all">
              Cerca lavoro
              <ArrowRight className="w-4 h-4" />
            </span>
          </Link>

          {/* AI Reskilling Card */}
          <div className="group p-8 bg-white rounded-2xl border border-neutral-200">
            <div className="w-12 h-12 bg-azure-50 rounded-xl flex items-center justify-center mb-5">
              <GraduationCap className="w-6 h-6 text-azure-600" />
            </div>
            <h3 className="text-xl font-semibold text-black-950">
              AI Reskilling
            </h3>
            <p className="mt-3 text-neutral-600 leading-relaxed">
              Percorsi formativi personalizzati per acquisire le competenze AI piu' richieste dal mercato del lavoro.
            </p>
            <span className="inline-flex items-center gap-1 mt-5 text-sm font-medium text-neutral-400">
              Prossimamente
            </span>
          </div>
        </div>
      </div>
    </section>
  );
}
