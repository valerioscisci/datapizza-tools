'use client';

import { useEffect } from 'react';
import { useTranslations } from 'next-intl';
import { X, ExternalLink } from 'lucide-react';
import type { EmailLog } from '../_utils/constants';
import { emailTypeBadgeStyle } from '../_utils/constants';

interface EmailDetailDialogProps {
  email: EmailLog;
  onClose: () => void;
}

export function EmailDetailDialog({ email, onClose }: EmailDetailDialogProps) {
  const t = useTranslations('notifications');

  // Lock body scroll while dialog is open
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  // Close on Escape
  useEffect(() => {
    function handleEsc(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
    }
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  const receivedDate = new Date(email.created_at).toLocaleDateString('it-IT', {
    day: 'numeric',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose} role="presentation">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />

      {/* Dialog */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="email-dialog-title"
        className="relative bg-white rounded-3xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 bg-neutral-100 rounded-full flex items-center justify-center hover:bg-neutral-200 transition-colors cursor-pointer z-10"
          aria-label={t('detail.close')}
        >
          <X className="w-4 h-4 text-neutral-600" />
        </button>

        <div className="p-8">
          {/* Header */}
          <h2 id="email-dialog-title" className="text-2xl font-heading font-semibold text-black-950 pr-10">
            {email.subject}
          </h2>

          {/* Meta row */}
          <div className="flex flex-wrap items-center gap-3 mt-4">
            <div className="flex items-center gap-1.5">
              <span className="text-xs text-neutral-500">{t('detail.from')}:</span>
              <span className="text-sm font-medium text-neutral-700">{email.sender_label}</span>
            </div>
            <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full border ${emailTypeBadgeStyle(email.email_type)}`}>
              {t(`emailTypes.${email.email_type}`)}
            </span>
            <span className="text-xs text-neutral-400">
              {t('detail.receivedAt')} {receivedDate}
            </span>
          </div>

          {/* Body */}
          <div className="mt-6 pt-6 border-t border-neutral-200">
            <div
              className="prose prose-sm max-w-none text-neutral-700 leading-relaxed"
              dangerouslySetInnerHTML={{ __html: email.body_html }}
            />
          </div>

          {/* Actions */}
          <div className="mt-8 flex gap-3">
            {email.related_proposal_id && (
              <a
                href={`/it/proposte`}
                className="inline-flex items-center gap-2 px-6 py-3 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer"
              >
                {t('detail.goToProposal')}
                <ExternalLink className="w-4 h-4" aria-hidden="true" />
              </a>
            )}
            <button
              onClick={onClose}
              className="px-6 py-3 bg-neutral-100 text-neutral-700 font-medium rounded-xl hover:bg-neutral-200 transition-colors cursor-pointer"
            >
              {t('detail.close')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
