'use client';

import { useTranslations } from 'next-intl';
import { Bell, CheckCheck } from 'lucide-react';
import type { EmailLog } from '../_utils/constants';
import { EmailCard } from './EmailCard';

interface EmailListProps {
  emails: EmailLog[];
  loading: boolean;
  total: number;
  page: number;
  pageSize: number;
  unreadCount: number;
  onEmailClick: (email: EmailLog) => void;
  onMarkAllRead: () => void;
  onPageChange: (page: number) => void;
}

export function EmailList({
  emails,
  loading,
  total,
  page,
  pageSize,
  unreadCount,
  onEmailClick,
  onMarkAllRead,
  onPageChange,
}: EmailListProps) {
  const t = useTranslations('notifications');
  const totalPages = Math.ceil(total / pageSize);

  // Loading skeleton
  if (loading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <div key={i} className="animate-pulse rounded-lg bg-neutral-100 h-20" />
        ))}
      </div>
    );
  }

  // Empty state
  if (emails.length === 0) {
    return (
      <div className="text-center py-16">
        <Bell className="w-12 h-12 text-neutral-300 mx-auto mb-4" aria-hidden="true" />
        <p className="text-lg font-medium text-neutral-700">{t('empty')}</p>
        <p className="text-sm text-neutral-500 mt-1">{t('emptyDescription')}</p>
      </div>
    );
  }

  return (
    <div>
      {/* Mark all read header */}
      {unreadCount > 0 && (
        <div className="flex items-center justify-between mb-4">
          <span className="text-sm text-neutral-500">
            {t('unreadCount', { count: unreadCount })}
          </span>
          <button
            onClick={onMarkAllRead}
            className="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-azure-600 hover:text-azure-700 hover:bg-azure-50 rounded-lg transition-colors cursor-pointer"
          >
            <CheckCheck className="w-4 h-4" aria-hidden="true" />
            {t('markAllRead')}
          </button>
        </div>
      )}

      {/* Email cards */}
      <div className="space-y-2" aria-live="polite">
        {emails.map((email) => (
          <EmailCard
            key={email.id}
            email={email}
            onClick={() => onEmailClick(email)}
          />
        ))}
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex justify-center items-center gap-2 mt-8">
          <button
            onClick={() => onPageChange(Math.max(1, page - 1))}
            disabled={page === 1}
            className="px-4 py-2 text-sm font-medium rounded-lg bg-white border border-neutral-200 text-neutral-600 hover:border-azure-300 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {t('pagination.previous')}
          </button>
          <span className="px-4 py-2 text-sm text-neutral-500">
            {t('pagination.page', { current: page, total: totalPages })}
          </span>
          <button
            onClick={() => onPageChange(page + 1)}
            disabled={page >= totalPages}
            className="px-4 py-2 text-sm font-medium rounded-lg bg-white border border-neutral-200 text-neutral-600 hover:border-azure-300 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
          >
            {t('pagination.next')}
          </button>
        </div>
      )}
    </div>
  );
}
