'use client';

import { useTranslations } from 'next-intl';
import { useAuth } from '@/lib/auth/use-auth';
import { signIn } from 'next-auth/react';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { API_BASE, INDUSTRY_OPTIONS } from '../_utils/constants';

export function SignupPage() {
  const t = useTranslations('auth');
  const tIndustry = useTranslations('industry');
  const router = useRouter();
  const { user, loading, isCompany } = useAuth();

  const [userType, setUserType] = useState<'talent' | 'company'>('talent');
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [companyWebsite, setCompanyWebsite] = useState('');
  const [industry, setIndustry] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && user) {
      if (isCompany) {
        router.push('/it/talenti');
      } else {
        router.push('/it/jobs');
      }
    }
  }, [user, loading, router, isCompany]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');

    if (password !== confirmPassword) {
      setError(t('passwordMismatch'));
      return;
    }

    if (password.length < 6) {
      setError(t('passwordTooShort'));
      return;
    }

    if (userType === 'company' && !companyName.trim()) {
      setError(t('companyNameRequired'));
      return;
    }

    setSubmitting(true);
    try {
      // Step 1: Register via backend API
      const payload: Record<string, string> = {
        email,
        password,
        full_name: fullName,
        user_type: userType,
      };

      if (userType === 'company') {
        payload.company_name = companyName;
        if (companyWebsite.trim()) {
          payload.company_website = companyWebsite;
        }
        if (industry) {
          payload.industry = industry;
        }
      }

      const res = await fetch(`${API_BASE}/api/v1/auth/signup`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: t('signupError') }));
        throw new Error(err.detail || t('signupError'));
      }

      // Step 2: Sign in via NextAuth to establish session
      const result = await signIn('credentials', {
        email,
        password,
        redirect: false,
      });

      if (result?.error) {
        setError(t('signupError'));
      } else {
        if (userType === 'company') {
          router.push('/it/talenti');
        } else {
          router.push('/it/jobs');
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : t('signupError'));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return null;

  const inputClass =
    'w-full px-4 py-2.5 rounded-lg border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-azure-500 focus:border-azure-500 transition-colors';

  return (
    <section className="min-h-[calc(100vh-4rem)] flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl border border-neutral-200 shadow-sm p-8">
          <h1 className="text-2xl font-heading font-semibold text-black-950 text-center mb-2">
            {t('signup')}
          </h1>
          <p className="text-sm text-neutral-500 text-center mb-6">
            {t('signupSubtitle')}
          </p>

          {/* User Type Toggle */}
          <div className="flex rounded-xl border border-neutral-200 p-1 mb-6">
            <button
              type="button"
              onClick={() => setUserType('talent')}
              className={`flex-1 py-2.5 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                userType === 'talent'
                  ? 'bg-azure-600 text-white'
                  : 'text-neutral-600 hover:text-azure-600'
              }`}
            >
              {t('talentTab')}
            </button>
            <button
              type="button"
              onClick={() => setUserType('company')}
              className={`flex-1 py-2.5 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                userType === 'company'
                  ? 'bg-azure-600 text-white'
                  : 'text-neutral-600 hover:text-azure-600'
              }`}
            >
              {t('companyTab')}
            </button>
          </div>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-600">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {userType === 'company' && (
              <div>
                <label htmlFor="companyName" className="block text-sm font-medium text-neutral-700 mb-1.5">
                  {t('companyName')}
                </label>
                <input
                  id="companyName"
                  type="text"
                  required
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className={inputClass}
                  placeholder="Acme S.r.l."
                />
              </div>
            )}

            <div>
              <label htmlFor="fullName" className="block text-sm font-medium text-neutral-700 mb-1.5">
                {userType === 'company' ? t('contactName') : t('fullName')}
              </label>
              <input
                id="fullName"
                type="text"
                required
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className={inputClass}
                placeholder="Mario Rossi"
              />
            </div>

            <div>
              <label htmlFor="email" className="block text-sm font-medium text-neutral-700 mb-1.5">
                {userType === 'company' ? t('companyEmail') : t('email')}
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className={inputClass}
                placeholder="email@esempio.it"
              />
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-neutral-700 mb-1.5">
                {t('password')}
              </label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className={inputClass}
                placeholder="••••••••"
              />
            </div>

            <div>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-neutral-700 mb-1.5">
                {t('confirmPassword')}
              </label>
              <input
                id="confirmPassword"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                className={inputClass}
                placeholder="••••••••"
              />
            </div>

            {userType === 'company' && (
              <>
                <div>
                  <label htmlFor="companyWebsite" className="block text-sm font-medium text-neutral-700 mb-1.5">
                    {t('companyWebsite')}
                  </label>
                  <input
                    id="companyWebsite"
                    type="url"
                    value={companyWebsite}
                    onChange={(e) => setCompanyWebsite(e.target.value)}
                    className={inputClass}
                    placeholder="https://www.esempio.it"
                  />
                </div>

                <div>
                  <label htmlFor="industry" className="block text-sm font-medium text-neutral-700 mb-1.5">
                    {t('industry')}
                  </label>
                  <select
                    id="industry"
                    value={industry}
                    onChange={(e) => setIndustry(e.target.value)}
                    className={`${inputClass} cursor-pointer`}
                  >
                    <option value="">{t('selectIndustry')}</option>
                    {INDUSTRY_OPTIONS.map((ind) => (
                      <option key={ind} value={ind}>
                        {tIndustry(ind)}
                      </option>
                    ))}
                  </select>
                </div>
              </>
            )}

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? '...' : t('signupButton')}
            </button>
          </form>

          <p className="mt-6 text-sm text-neutral-500 text-center">
            {t('hasAccount')}{' '}
            <Link href="/it/login" className="text-azure-600 hover:text-azure-700 font-medium cursor-pointer">
              {t('loginButton')}
            </Link>
          </p>
        </div>
      </div>
    </section>
  );
}
