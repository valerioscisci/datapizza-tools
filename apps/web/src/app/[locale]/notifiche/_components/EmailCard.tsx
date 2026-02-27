'use client';

import { useTranslations } from 'next-intl';
import { Mail, MailOpen } from 'lucide-react';
import { emailTypeBadgeStyle, formatRelativeTime } from '../_utils/constants';
import { EmailCardProps } from './EmailCard.props';

export function EmailCard({ email, onClick }: EmailCardProps) {
  const t = useTranslations('notifications');

  return (
    <button
      onClick={onClick}
      className={`w-full text-left p-4 rounded-lg border transition-all duration-300 cursor-pointer ${
        email.is_read
          ? 'bg-white border-neutral-200 hover:border-azure-300'
          : 'bg-azure-25 border-azure-200 hover:border-azure-400'
      }`}
    >
      <div className="flex items-start gap-3">
        {/* Unread indicator */}
        <div className="pt-1.5 shrink-0">
          {email.is_read ? (
            <MailOpen className="w-5 h-5 text-neutral-400" aria-hidden="true" />
          ) : (
            <div className="relative">
              <Mail className="w-5 h-5 text-azure-600" aria-hidden="true" />
              <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-azure-600 rounded-full" />
            </div>
          )}
        </div>

        {/* Content */}
        <div className="min-w-0 flex-1">
          <div className="flex items-center justify-between gap-2 mb-1">
            <span className={`text-sm ${email.is_read ? 'text-neutral-600' : 'font-semibold text-black-950'}`}>
              {email.sender_label}
            </span>
            <span className="text-xs text-neutral-400 shrink-0">
              {formatRelativeTime(email.created_at, t)}
            </span>
          </div>

          <p className={`text-sm mb-2 line-clamp-1 ${email.is_read ? 'text-neutral-700' : 'font-medium text-black-950'}`}>
            {email.subject}
          </p>

          <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full border ${emailTypeBadgeStyle(email.email_type)}`}>
            {t(`emailTypes.${email.email_type}`)}
          </span>
        </div>
      </div>
    </button>
  );
}
