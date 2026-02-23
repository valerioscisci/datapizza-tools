'use client';

import { useTranslations } from 'next-intl';
import { useAuth } from '@/lib/auth/use-auth';
import { signIn } from 'next-auth/react';
import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
  const t = useTranslations('auth');
  const router = useRouter();
  const { user, loading } = useAuth();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (!loading && user) {
      router.push('/it/jobs');
    }
  }, [user, loading, router]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError('');
    setSubmitting(true);
    try {
      const result = await signIn('credentials', {
        email,
        password,
        redirect: false,
      });
      if (result?.error) {
        setError(t('loginError'));
      } else {
        router.push('/it/jobs');
      }
    } catch {
      setError(t('loginError'));
    } finally {
      setSubmitting(false);
    }
  }

  if (loading) return null;

  return (
    <section className="min-h-[calc(100vh-4rem)] flex items-center justify-center py-12 px-4">
      <div className="w-full max-w-md">
        <div className="bg-white rounded-2xl border border-neutral-200 shadow-sm p-8">
          <h1 className="text-2xl font-heading font-semibold text-black-950 text-center mb-2">
            {t('login')}
          </h1>
          <p className="text-sm text-neutral-500 text-center mb-8">
            {t('loginSubtitle')}
          </p>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-50 border border-red-200 text-sm text-red-600">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-neutral-700 mb-1.5">
                {t('email')}
              </label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-2.5 rounded-lg border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-azure-500 focus:border-azure-500 transition-colors"
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
                className="w-full px-4 py-2.5 rounded-lg border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-azure-500 focus:border-azure-500 transition-colors"
                placeholder="••••••••"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-3 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submitting ? '...' : t('loginButton')}
            </button>
          </form>

          <p className="mt-6 text-sm text-neutral-500 text-center">
            {t('noAccount')}{' '}
            <Link href="/it/signup" className="text-azure-600 hover:text-azure-700 font-medium cursor-pointer">
              {t('signupButton')}
            </Link>
          </p>
        </div>
      </div>
    </section>
  );
}
