'use client';

export function CommunitySection() {
  return (
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
  );
}
