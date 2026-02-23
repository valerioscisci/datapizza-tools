import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { ArrowRight, Building2, Briefcase, Target, GraduationCap } from 'lucide-react';

export default function HomePage() {
  const t = useTranslations();

  return (
    <>
      {/* Hero Section */}
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

      {/* Stats Section */}
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

      {/* Services Section */}
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

      {/* Community Section */}
      <section className="py-20 bg-azure-25">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="max-w-3xl mx-auto">
            <h2 className="text-3xl sm:text-4xl font-heading font-semibold text-black-950">
              La community tech piu&apos; grande d&apos;Italia
            </h2>
            <p className="mt-4 text-lg text-neutral-600">
              Oltre 500.000 professionisti tech si affidano a Datapizza per restare aggiornati sulle ultime novita' del settore.
            </p>
          </div>
          <div className="mt-12 grid grid-cols-2 md:grid-cols-4 gap-6">
            <div className="bg-white rounded-2xl p-6 border border-neutral-200">
              <p className="text-3xl font-heading font-semibold text-azure-600">220k</p>
              <p className="mt-1 text-sm text-neutral-500">Instagram</p>
            </div>
            <div className="bg-white rounded-2xl p-6 border border-neutral-200">
              <p className="text-3xl font-heading font-semibold text-azure-600">160k</p>
              <p className="mt-1 text-sm text-neutral-500">LinkedIn</p>
            </div>
            <div className="bg-white rounded-2xl p-6 border border-neutral-200">
              <p className="text-3xl font-heading font-semibold text-azure-600">30k</p>
              <p className="mt-1 text-sm text-neutral-500">YouTube</p>
            </div>
            <div className="bg-white rounded-2xl p-6 border border-neutral-200">
              <p className="text-3xl font-heading font-semibold text-azure-600">20k</p>
              <p className="mt-1 text-sm text-neutral-500">Spotify</p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
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
    </>
  );
}
