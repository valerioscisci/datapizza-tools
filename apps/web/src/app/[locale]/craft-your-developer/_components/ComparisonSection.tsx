'use client';

export function ComparisonSection() {
  return (
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
  );
}
