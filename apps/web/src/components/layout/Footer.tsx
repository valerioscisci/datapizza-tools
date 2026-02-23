'use client';

import Link from 'next/link';
import Image from 'next/image';
import { useTranslations } from 'next-intl';

function InstagramIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 100 12.324 6.162 6.162 0 000-12.324zM12 16a4 4 0 110-8 4 4 0 010 8zm6.406-11.845a1.44 1.44 0 100 2.881 1.44 1.44 0 000-2.881z" />
    </svg>
  );
}

function LinkedInIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z" />
    </svg>
  );
}

function YouTubeIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M23.498 6.186a3.016 3.016 0 00-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 00.502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 002.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 002.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z" />
    </svg>
  );
}

function TelegramIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M11.944 0A12 12 0 000 12a12 12 0 0012 12 12 12 0 0012-12A12 12 0 0012 0a12 12 0 00-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 01.171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.479.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z" />
    </svg>
  );
}

function SpotifyIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C5.4 0 0 5.4 0 12s5.4 12 12 12 12-5.4 12-12S18.66 0 12 0zm5.521 17.34c-.24.359-.66.48-1.021.24-2.82-1.74-6.36-2.101-10.561-1.141-.418.122-.779-.179-.899-.539-.12-.421.18-.78.54-.9 4.56-1.021 8.52-.6 11.64 1.32.42.18.479.659.301 1.02zm1.44-3.3c-.301.42-.841.6-1.262.3-3.239-1.98-8.159-2.58-11.939-1.38-.479.12-1.02-.12-1.14-.6-.12-.48.12-1.021.6-1.141C9.6 9.9 15 10.561 18.72 12.84c.361.181.54.78.241 1.2zm.12-3.36C15.24 8.4 8.82 8.16 5.16 9.301c-.6.179-1.2-.181-1.38-.721-.18-.601.18-1.2.72-1.381 4.26-1.26 11.28-1.02 15.721 1.621.539.3.719 1.02.419 1.56-.299.421-1.02.599-1.559.3z" />
    </svg>
  );
}

const socialLinks = [
  { name: 'Instagram', href: 'https://www.instagram.com/datapizza/', Icon: InstagramIcon },
  { name: 'LinkedIn', href: 'https://www.linkedin.com/company/datapizza/', Icon: LinkedInIcon },
  { name: 'YouTube', href: 'https://www.youtube.com/@datapizza', Icon: YouTubeIcon },
  { name: 'Telegram', href: 'https://t.me/datapizza', Icon: TelegramIcon },
  { name: 'Spotify', href: 'https://open.spotify.com/show/6TMBvIx2tWVA8AEPDU027j', Icon: SpotifyIcon },
];

export default function Footer() {
  const t = useTranslations();

  return (
    <footer className="bg-neutral-50 border-t border-neutral-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
          {/* Left: Logo + Description */}
          <div className="lg:col-span-5">
            <Link href="/it" className="cursor-pointer">
              <Image
                src="/datapizza-logo.svg"
                alt="Datapizza"
                width={140}
                height={28}
              />
            </Link>
            <p className="mt-5 text-sm text-neutral-500 max-w-sm leading-relaxed">
              Naviga il mercato del lavoro tech guidato dall&apos;AI. Acquisisci nuove competenze, trova il tuo prossimo ruolo.
            </p>
          </div>

          {/* Right columns */}
          <div className="lg:col-span-7 grid grid-cols-2 sm:grid-cols-3 gap-8">
            {/* Pagine */}
            <div>
              <h3 className="text-sm font-semibold text-neutral-900 mb-4">
                Pagine
              </h3>
              <ul className="space-y-3">
                <li>
                  <Link href="/it/craft-your-developer" className="text-sm text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer">
                    {t('nav.craftYourDeveloper')}
                  </Link>
                </li>
                <li>
                  <Link href="/it/jobs" className="text-sm text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer">
                    {t('nav.jobsMarket')}
                  </Link>
                </li>
              </ul>
            </div>

            {/* Azienda */}
            <div>
              <h3 className="text-sm font-semibold text-neutral-900 mb-4">
                Azienda
              </h3>
              <ul className="space-y-3">
                <li>
                  <a href="https://datapizza.tech/it#contatti" target="_blank" rel="noopener noreferrer" className="text-sm text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer">
                    Contatti
                  </a>
                </li>
              </ul>
            </div>

            {/* Canali */}
            <div>
              <h3 className="text-sm font-semibold text-neutral-900 mb-4">
                Canali
              </h3>
              <div className="flex flex-wrap gap-2.5">
                {socialLinks.map(({ name, href, Icon }) => (
                  <a
                    key={name}
                    href={href}
                    target="_blank"
                    rel="noopener noreferrer"
                    aria-label={name}
                    className="w-9 h-9 bg-neutral-900 rounded-full flex items-center justify-center hover:bg-azure-600 transition-colors cursor-pointer"
                  >
                    <Icon className="w-4 h-4 text-white" />
                  </a>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Bottom legal bar */}
      <div className="border-t border-neutral-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
            <p className="text-xs text-neutral-400 text-center sm:text-left">
              &copy; {new Date().getFullYear()} Datapizza S.r.l. &mdash; Tutti i diritti riservati.
            </p>
            <div className="flex items-center gap-4">
              <a
                href="https://jobs.datapizza.tech/terms"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-neutral-400 hover:text-neutral-600 transition-colors cursor-pointer"
              >
                Termini e Condizioni
              </a>
              <span className="text-xs text-neutral-300">|</span>
              <a
                href="https://jobs.datapizza.tech/privacy"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-neutral-400 hover:text-neutral-600 transition-colors cursor-pointer"
              >
                Privacy
              </a>
              <span className="text-xs text-neutral-300">|</span>
              <a
                href="https://jobs.datapizza.tech/cookies"
                target="_blank"
                rel="noopener noreferrer"
                className="text-xs text-neutral-400 hover:text-neutral-600 transition-colors cursor-pointer"
              >
                Cookie
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
