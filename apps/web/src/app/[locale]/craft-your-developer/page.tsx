import { useTranslations } from 'next-intl';
import { Target, Wallet, ShieldCheck, Zap, Search, PenTool, BookOpen, UserCheck, ArrowRight } from 'lucide-react';

export default function CraftYourDeveloperPage() {
  const t = useTranslations('craftYourDeveloper');

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

  const steps = [
    { key: 'step1', icon: Search, number: '01' },
    { key: 'step2', icon: PenTool, number: '02' },
    { key: 'step3', icon: BookOpen, number: '03' },
    { key: 'step4', icon: UserCheck, number: '04' },
  ];

  return (
    <>
      {/* Hero Section */}
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

      {/* Problem / Context Section */}
      <section className="py-20 bg-neutral-950">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center">
            <h2 className="text-3xl sm:text-4xl font-heading font-semibold text-white">
              Il problema del recruiting tech oggi
            </h2>
            <p className="mt-6 text-lg text-neutral-300 leading-relaxed">
              Il 60-70% dei lavori digitali sara&apos; impattato dall&apos;introduzione dei workflow agentici nei prossimi 6-12 mesi.
              Le aziende faticano a trovare developer con competenze AI specifiche perche&apos; il mercato non ha ancora formato abbastanza professionisti.
            </p>
            <p className="mt-4 text-lg text-neutral-300 leading-relaxed">
              <strong className="text-azure-400">Craft Your Developer</strong> ribalta il paradigma: invece di cercare un candidato impossibile,
              prendi un developer gia&apos; esperto e formalo esattamente sulle competenze che ti servono.
            </p>
          </div>
        </div>
      </section>

      {/* Benefits Section */}
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

      {/* How It Works Section */}
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

      {/* Comparison Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-3xl sm:text-4xl font-heading font-semibold text-black-950 text-center mb-12">
            Hiring Tradizionale vs Craft Your Developer
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* Traditional */}
            <div className="p-8 bg-neutral-50 rounded-2xl border border-neutral-200">
              <h3 className="text-lg font-semibold text-neutral-700 mb-6">Hiring Tradizionale</h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3 text-neutral-600">
                  <span className="mt-1 w-2 h-2 bg-red-500 rounded-full shrink-0" />
                  Mesi di ricerca per trovare profili rari
                </li>
                <li className="flex items-start gap-3 text-neutral-600">
                  <span className="mt-1 w-2 h-2 bg-red-500 rounded-full shrink-0" />
                  Costi elevati di recruiting e headhunting
                </li>
                <li className="flex items-start gap-3 text-neutral-600">
                  <span className="mt-1 w-2 h-2 bg-red-500 rounded-full shrink-0" />
                  Candidati generici, non formati sulle tue esigenze
                </li>
                <li className="flex items-start gap-3 text-neutral-600">
                  <span className="mt-1 w-2 h-2 bg-red-500 rounded-full shrink-0" />
                  Alto rischio di mismatch culturale e tecnico
                </li>
              </ul>
            </div>

            {/* Craft Your Developer */}
            <div className="p-8 bg-azure-25 rounded-2xl border-2 border-azure-300">
              <h3 className="text-lg font-semibold text-azure-700 mb-6">Craft Your Developer</h3>
              <ul className="space-y-4">
                <li className="flex items-start gap-3 text-neutral-700">
                  <span className="mt-1 w-2 h-2 bg-pastelgreen-500 rounded-full shrink-0" />
                  Developer mid/senior gia&apos; disponibili nel marketplace
                </li>
                <li className="flex items-start gap-3 text-neutral-700">
                  <span className="mt-1 w-2 h-2 bg-pastelgreen-500 rounded-full shrink-0" />
                  Investimento mirato nella formazione specifica
                </li>
                <li className="flex items-start gap-3 text-neutral-700">
                  <span className="mt-1 w-2 h-2 bg-pastelgreen-500 rounded-full shrink-0" />
                  Percorso personalizzato sulle competenze AI che servono a te
                </li>
                <li className="flex items-start gap-3 text-neutral-700">
                  <span className="mt-1 w-2 h-2 bg-pastelgreen-500 rounded-full shrink-0" />
                  Developer pronto dal giorno uno, formato per il tuo team
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
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
    </>
  );
}
