'use client';

import { useTranslations } from 'next-intl';
import { useAuth } from '@/lib/auth/use-auth';
import { useRouter } from 'next/navigation';
import { useState, useEffect, useCallback } from 'react';
import { Loader2, AlertTriangle, RefreshCw } from 'lucide-react';
import { EMAIL_TYPE_FILTERS } from '../_utils/constants';
import type { EmailLog, EmailType } from '../_utils/constants';
import { useEmails } from '../_hooks/useEmails';
import { EmailList } from './EmailList';
import { EmailDetailDialog } from './EmailDetailDialog';
import { NotificationPreferences } from './NotificationPreferences';

export function NotifichePage() {
  const t = useTranslations('notifications');
  const { user, loading: authLoading, isAuthenticated } = useAuth();
  const router = useRouter();

  const [activeFilter, setActiveFilter] = useState('all');
  const [page, setPage] = useState(1);
  const [selectedEmail, setSelectedEmail] = useState<EmailLog | null>(null);

  const {
    emails,
    total,
    unreadCount,
    page: currentPage,
    pageSize,
    loading,
    error,
    fetchEmails,
    markAsRead,
    markAllAsRead,
    fetchEmail,
  } = useEmails();

  // Derive filter params from the active filter key
  const getFilterParams = useCallback((filterKey: string, pageNum: number) => {
    const filterDef = EMAIL_TYPE_FILTERS.find((f) => f.key === filterKey);
    const params: {
      page: number;
      pageSize: number;
      emailTypes?: EmailType[];
      isRead?: boolean;
    } = { page: pageNum, pageSize: 20 };

    if (filterKey === 'unread') {
      params.isRead = false;
    } else if (filterDef && filterDef.types.length > 0) {
      params.emailTypes = filterDef.types;
    }

    return params;
  }, []);

  // Fetch emails when filter or page changes
  useEffect(() => {
    if (isAuthenticated) {
      fetchEmails(getFilterParams(activeFilter, page));
    }
  }, [isAuthenticated, activeFilter, page, fetchEmails, getFilterParams]);

  // Handle email click: fetch full email (auto marks as read) and open dialog
  const handleEmailClick = useCallback(async (email: EmailLog) => {
    const fullEmail = await fetchEmail(email.id);
    if (fullEmail) {
      setSelectedEmail(fullEmail);
    } else {
      // Fallback: use the data we already have
      setSelectedEmail(email);
      if (!email.is_read) {
        markAsRead(email.id);
      }
    }
  }, [fetchEmail, markAsRead]);

  const handleFilterChange = useCallback((key: string) => {
    setActiveFilter(key);
    setPage(1);
  }, []);

  const handleMarkAllRead = useCallback(() => {
    markAllAsRead();
  }, [markAllAsRead]);

  const handlePageChange = useCallback((newPage: number) => {
    setPage(newPage);
  }, []);

  // Redirect unauthenticated users to login
  useEffect(() => {
    if (!authLoading && !user) {
      router.push('/it/login');
    }
  }, [user, authLoading, router]);

  if (authLoading || !user) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center gap-2 text-neutral-500">
          <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
          <span>{t('loading')}</span>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Header */}
      <section className="bg-linear-to-b from-azure-25 to-white py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-heading font-semibold text-black-950">
            {t('title')}
          </h1>
          <p className="mt-4 text-lg text-neutral-600 max-w-2xl mx-auto">
            {t('subtitle')}
          </p>
        </div>
      </section>

      {/* Filters + Email List */}
      <section className="py-8 sm:py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Error banner */}
          {error && (
            <div className="mb-6 p-4 rounded-lg bg-red-50 border border-red-200 flex items-center justify-between gap-4">
              <div className="flex items-center gap-3">
                <AlertTriangle className="w-5 h-5 text-red-500 shrink-0" aria-hidden="true" />
                <p className="text-sm text-red-700">{t('errorLoading')}</p>
              </div>
              <button
                onClick={() => fetchEmails(getFilterParams(activeFilter, page))}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-red-600 hover:text-red-700 hover:bg-red-100 rounded-lg transition-colors cursor-pointer"
              >
                <RefreshCw className="w-4 h-4" aria-hidden="true" />
                {t('retry')}
              </button>
            </div>
          )}

          {/* Tab bar */}
          <div className="flex flex-wrap items-center gap-2 mb-8">
            {EMAIL_TYPE_FILTERS.map((filter) => (
              <button
                key={filter.key}
                onClick={() => handleFilterChange(filter.key)}
                aria-pressed={activeFilter === filter.key}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                  activeFilter === filter.key
                    ? 'bg-azure-600 text-white'
                    : 'bg-white text-neutral-600 border border-neutral-200 hover:border-azure-300 hover:text-azure-600'
                }`}
              >
                {t(`tabs.${filter.key}`)}
              </button>
            ))}
          </div>

          {/* Email List */}
          <EmailList
            emails={emails}
            loading={loading}
            total={total}
            page={currentPage}
            pageSize={pageSize}
            unreadCount={unreadCount}
            onEmailClick={handleEmailClick}
            onMarkAllRead={handleMarkAllRead}
            onPageChange={handlePageChange}
          />

          {/* Notification Preferences */}
          <div className="mt-12">
            <NotificationPreferences />
          </div>
        </div>
      </section>

      {/* Email Detail Dialog */}
      {selectedEmail && (
        <EmailDetailDialog
          email={selectedEmail}
          onClose={() => setSelectedEmail(null)}
        />
      )}
    </>
  );
}
