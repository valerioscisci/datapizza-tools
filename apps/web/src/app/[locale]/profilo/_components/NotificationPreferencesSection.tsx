'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import Link from 'next/link';
import { Bell, Check, MessageCircle } from 'lucide-react';
import { useNotificationPreferences } from '@/lib/hooks/useNotificationPreferences';

export function NotificationPreferencesSection() {
  const t = useTranslations('notifications.preferences');
  const {
    preferences,
    loading,
    updatePreferences,
  } = useNotificationPreferences();

  const [savedFeedback, setSavedFeedback] = useState(false);

  async function handleToggle(field: 'email_notifications' | 'daily_digest' | 'telegram_notifications') {
    if (!preferences) return;
    try {
      await updatePreferences({ [field]: !preferences[field] });
      setSavedFeedback(true);
      setTimeout(() => setSavedFeedback(false), 2000);
    } catch {
      // Preferences not updated — don't show "saved" feedback
    }
  }

  if (loading || !preferences) return null;

  const isTelegramLinked = !!preferences.telegram_chat_id;

  return (
    <div className="border border-neutral-200 rounded-lg bg-white overflow-hidden p-5">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-azure-50 rounded-full flex items-center justify-center shrink-0">
            <Bell className="w-5 h-5 text-azure-600" aria-hidden="true" />
          </div>
          <h3 className="text-lg font-semibold text-black-950">{t('title')}</h3>
        </div>

        {savedFeedback && (
          <span className="inline-flex items-center gap-1 text-sm text-pastelgreen-600 font-medium animate-in fade-in">
            <Check className="w-4 h-4" aria-hidden="true" />
            {t('saved')}
          </span>
        )}
      </div>

      <div className="space-y-4">
        {/* Email Notifications toggle */}
        <div className="flex items-center justify-between gap-4 p-3 rounded-lg bg-neutral-50">
          <div>
            <p className="text-sm font-semibold text-neutral-900">{t('emailNotifications')}</p>
            <p className="text-xs text-neutral-500 mt-0.5">{t('emailNotificationsDescription')}</p>
          </div>
          <button
            onClick={() => handleToggle('email_notifications')}
            role="switch"
            aria-checked={preferences.email_notifications}
            aria-label={t('emailNotifications')}
            className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors duration-300 cursor-pointer ${
              preferences.email_notifications ? 'bg-azure-600' : 'bg-neutral-300'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-300 ${
                preferences.email_notifications ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Daily Digest toggle */}
        <div className="flex items-center justify-between gap-4 p-3 rounded-lg bg-neutral-50">
          <div>
            <p className="text-sm font-semibold text-neutral-900">{t('dailyDigest')}</p>
            <p className="text-xs text-neutral-500 mt-0.5">{t('dailyDigestDescription')}</p>
          </div>
          <button
            onClick={() => handleToggle('daily_digest')}
            role="switch"
            aria-checked={preferences.daily_digest}
            aria-label={t('dailyDigest')}
            className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors duration-300 cursor-pointer ${
              preferences.daily_digest ? 'bg-azure-600' : 'bg-neutral-300'
            }`}
          >
            <span
              className={`inline-block h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-300 ${
                preferences.daily_digest ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>

        {/* Telegram section */}
        {isTelegramLinked ? (
          <div className="flex items-center justify-between gap-4 p-3 rounded-lg bg-neutral-50">
            <div>
              <p className="text-sm font-semibold text-neutral-900 flex items-center gap-1.5">
                <MessageCircle className="w-4 h-4 text-pastelgreen-600" aria-hidden="true" />
                {t('telegramNotifications')}
              </p>
              <p className="text-xs text-neutral-500 mt-0.5">{t('telegramNotificationsDescription')}</p>
            </div>
            <button
              onClick={() => handleToggle('telegram_notifications')}
              role="switch"
              aria-checked={preferences.telegram_notifications}
              aria-label={t('telegramNotifications')}
              className={`relative inline-flex h-6 w-11 shrink-0 items-center rounded-full transition-colors duration-300 cursor-pointer ${
                preferences.telegram_notifications ? 'bg-azure-600' : 'bg-neutral-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 rounded-full bg-white shadow-sm transition-transform duration-300 ${
                  preferences.telegram_notifications ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        ) : (
          <div className="flex items-center gap-2 p-3 rounded-lg bg-neutral-50">
            <MessageCircle className="w-4 h-4 text-neutral-400" aria-hidden="true" />
            <Link
              href="/it/notifiche"
              className="text-sm text-azure-600 hover:text-azure-700 hover:underline cursor-pointer"
            >
              {t('telegramLinkFromProfile')}
            </Link>
          </div>
        )}
      </div>
    </div>
  );
}
