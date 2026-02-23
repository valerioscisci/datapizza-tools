'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import Image from 'next/image';
import { Menu, X, ChevronDown, LogOut } from 'lucide-react';
import { useAuth } from '@/lib/auth/use-auth';

export default function Navbar() {
  const t = useTranslations();
  const { user, logout, loading } = useAuth();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [companiesOpen, setCompaniesOpen] = useState(false);
  const [talentsOpen, setTalentsOpen] = useState(false);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/95 backdrop-blur-sm border-b border-neutral-200">
      <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/it" className="flex items-center duration-100 hover:scale-105">
            {/* Desktop: full logo */}
            <Image
              src="/datapizza-logo.svg"
              alt="Datapizza"
              width={158}
              height={32}
              className="hidden sm:block"
              priority
            />
            {/* Mobile: icon only */}
            <Image
              src="/datapizza-icon.svg"
              alt="Datapizza"
              width={32}
              height={32}
              className="block sm:hidden"
              priority
            />
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-1">
            {/* Companies Dropdown */}
            <div
              className="relative"
              onMouseEnter={() => setCompaniesOpen(true)}
              onMouseLeave={() => setCompaniesOpen(false)}
            >
              <button className="flex items-center gap-1 px-4 py-2 text-sm font-medium text-neutral-700 hover:text-azure-600 transition-colors rounded-lg hover:bg-azure-25 cursor-pointer">
                {t('common.companies')}
                <ChevronDown className="w-4 h-4" />
              </button>
              {companiesOpen && (
                <div className="absolute top-full left-0 mt-1 w-56 bg-white rounded-xl shadow-lg border border-neutral-100 py-2">
                  <Link
                    href="/it/craft-your-developer"
                    className="block px-4 py-2.5 text-sm text-neutral-700 hover:bg-azure-25 hover:text-azure-600 transition-colors"
                  >
                    {t('nav.craftYourDeveloper')}
                  </Link>
                </div>
              )}
            </div>

            {/* Talents Dropdown */}
            <div
              className="relative"
              onMouseEnter={() => setTalentsOpen(true)}
              onMouseLeave={() => setTalentsOpen(false)}
            >
              <button className="flex items-center gap-1 px-4 py-2 text-sm font-medium text-neutral-700 hover:text-azure-600 transition-colors rounded-lg hover:bg-azure-25 cursor-pointer">
                {t('common.talents')}
                <ChevronDown className="w-4 h-4" />
              </button>
              {talentsOpen && (
                <div className="absolute top-full left-0 mt-1 w-56 bg-white rounded-xl shadow-lg border border-neutral-100 py-2">
                  <Link
                    href="/it/jobs"
                    className="block px-4 py-2.5 text-sm text-neutral-700 hover:bg-azure-25 hover:text-azure-600 transition-colors"
                  >
                    {t('nav.jobsMarket')}
                  </Link>
                  <Link
                    href="/it/news"
                    className="block px-4 py-2.5 text-sm text-neutral-700 hover:bg-azure-25 hover:text-azure-600 transition-colors"
                  >
                    {t('nav.news')}
                  </Link>
                  <Link
                    href="/it/courses"
                    className="block px-4 py-2.5 text-sm text-neutral-700 hover:bg-azure-25 hover:text-azure-600 transition-colors"
                  >
                    {t('nav.courses')}
                  </Link>
                  {user && (
                    <Link
                      href="/it/candidature"
                      className="block px-4 py-2.5 text-sm text-neutral-700 hover:bg-azure-25 hover:text-azure-600 transition-colors"
                    >
                      {t('nav.myApplications')}
                    </Link>
                  )}
                </div>
              )}
            </div>
          </div>

          {/* Right side: Auth buttons (desktop) */}
          <div className="hidden md:flex items-center gap-2">
            {!loading && (
              <>
                {user ? (
                  <>
                    {/* User avatar */}
                    <div className="w-8 h-8 bg-azure-100 rounded-full flex items-center justify-center text-sm font-semibold text-azure-700">
                      {user.full_name.charAt(0).toUpperCase()}
                    </div>
                    <Link
                      href="/it/candidature"
                      className="px-3 py-2 text-sm font-medium text-neutral-700 hover:text-azure-600 transition-colors cursor-pointer"
                    >
                      {t('auth.myApplications')}
                    </Link>
                    <button
                      onClick={logout}
                      className="flex items-center gap-1 px-3 py-2 text-sm font-medium text-neutral-500 hover:text-red-600 transition-colors cursor-pointer"
                    >
                      <LogOut className="w-4 h-4" />
                      {t('auth.logout')}
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      href="/it/login"
                      className="px-4 py-2 text-sm font-medium text-neutral-700 hover:text-azure-600 transition-colors cursor-pointer"
                    >
                      {t('auth.login')}
                    </Link>
                    <Link
                      href="/it/signup"
                      className="px-4 py-2 text-sm font-medium bg-azure-600 text-white rounded-lg hover:bg-azure-700 transition-colors cursor-pointer"
                    >
                      {t('auth.signup')}
                    </Link>
                  </>
                )}
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="md:hidden p-2 text-neutral-700 hover:text-azure-600 cursor-pointer"
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {mobileOpen && (
          <div className="md:hidden border-t border-neutral-100 py-4 space-y-1">
            <p className="px-4 py-1 text-xs font-semibold text-neutral-400 uppercase tracking-wider">
              {t('common.companies')}
            </p>
            <Link
              href="/it/craft-your-developer"
              className="block px-4 py-2.5 text-sm text-neutral-700 hover:bg-azure-25 hover:text-azure-600 rounded-lg transition-colors"
              onClick={() => setMobileOpen(false)}
            >
              {t('nav.craftYourDeveloper')}
            </Link>

            <p className="px-4 py-1 pt-3 text-xs font-semibold text-neutral-400 uppercase tracking-wider">
              {t('common.talents')}
            </p>
            <Link
              href="/it/jobs"
              className="block px-4 py-2.5 text-sm text-neutral-700 hover:bg-azure-25 hover:text-azure-600 rounded-lg transition-colors"
              onClick={() => setMobileOpen(false)}
            >
              {t('nav.jobsMarket')}
            </Link>
            <Link
              href="/it/news"
              className="block px-4 py-2.5 text-sm text-neutral-700 hover:bg-azure-25 hover:text-azure-600 rounded-lg transition-colors"
              onClick={() => setMobileOpen(false)}
            >
              {t('nav.news')}
            </Link>
            <Link
              href="/it/courses"
              className="block px-4 py-2.5 text-sm text-neutral-700 hover:bg-azure-25 hover:text-azure-600 rounded-lg transition-colors"
              onClick={() => setMobileOpen(false)}
            >
              {t('nav.courses')}
            </Link>
            {user && (
              <Link
                href="/it/candidature"
                className="block px-4 py-2.5 text-sm text-neutral-700 hover:bg-azure-25 hover:text-azure-600 rounded-lg transition-colors"
                onClick={() => setMobileOpen(false)}
              >
                {t('nav.myApplications')}
              </Link>
            )}

            {/* Mobile Auth */}
            {!loading && (
              <div className="pt-4 border-t border-neutral-100 mt-3 space-y-1">
                {user ? (
                  <>
                    <div className="flex items-center gap-2 px-4 py-2">
                      <div className="w-8 h-8 bg-azure-100 rounded-full flex items-center justify-center text-sm font-semibold text-azure-700">
                        {user.full_name.charAt(0).toUpperCase()}
                      </div>
                      <span className="text-sm font-medium text-neutral-700">{user.full_name}</span>
                    </div>
                    <button
                      onClick={() => { logout(); setMobileOpen(false); }}
                      className="flex items-center gap-2 w-full px-4 py-2.5 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors cursor-pointer"
                    >
                      <LogOut className="w-4 h-4" />
                      {t('auth.logout')}
                    </button>
                  </>
                ) : (
                  <>
                    <Link
                      href="/it/login"
                      className="block px-4 py-2.5 text-sm text-neutral-700 hover:bg-azure-25 hover:text-azure-600 rounded-lg transition-colors"
                      onClick={() => setMobileOpen(false)}
                    >
                      {t('auth.login')}
                    </Link>
                    <Link
                      href="/it/signup"
                      className="block mx-4 py-2.5 text-sm text-center font-medium bg-azure-600 text-white rounded-lg hover:bg-azure-700 transition-colors"
                      onClick={() => setMobileOpen(false)}
                    >
                      {t('auth.signup')}
                    </Link>
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </nav>
    </header>
  );
}
