'use client';

import { useState } from 'react';
import { useTranslations } from 'next-intl';
import {
  ChevronDown,
  ChevronUp,
  Bell,
  Loader2,
  Check,
  Mail,
  Sparkles,
} from 'lucide-react';
import { useNotificationPreferences } from '@/lib/hooks/useNotificationPreferences';

export function NotificationPreferences() {
  const t = useTranslations('notifications.preferences');
  const {
    preferences,
    loading,
    updatePreferences,
    generateDigest,
    digestLoading,
  } = useNotificationPreferences();

  const [expanded, setExpanded] = useState(false);
  const [savedFeedback, setSavedFeedback] = useState(false);
  const [digestSuccess, setDigestSuccess] = useState(false);

  async function handleToggle(field: 'email_notifications' | 'daily_digest') {
    if (!preferences) return;
    const newValue = !preferences[field];
    // Optimistic update
    await updatePreferences({ [field]: newValue });
    setSavedFeedback(true);
    setTimeout(() => setSavedFeedback(false), 2000);
  }

  async function handleGenerateDigest() {
    const success = await generateDigest();
    if (success) {
      setDigestSuccess(true);
      setTimeout(() => setDigestSuccess(false), 3000);
    }
  }

  if (loading || !preferences) return null;

  return (
    <div className="border border-neutral-200 rounded-lg bg-white overflow-hidden">
      {/* Header -- expand/collapse */}
      <div className="flex items-center justify-between p-5">
        <button
          onClick={() => setExpanded((prev) => !prev)}
          aria-expanded={expanded}
          className="flex items-center gap-3 cursor-pointer hover:opacity-80 transition-opacity"
        >
          <div className="w-10 h-10 bg-azure-50 rounded-full flex items-center justify-center shrink-0">
            <Bell className="w-5 h-5 text-azure-600" aria-hidden="true" />
          </div>
          <div className="text-left">
            <h3 className="text-lg font-semibold text-black-950">{t('title')}</h3>
          </div>
          {expanded ? (
            <ChevronUp className="w-5 h-5 text-neutral-400 ml-2" aria-hidden="true" />
          ) : (
            <ChevronDown className="w-5 h-5 text-neutral-400 ml-2" aria-hidden="true" />
          )}
        </button>

        {/* Saved feedback */}
        {savedFeedback && (
          <span className="inline-flex items-center gap-1 text-sm text-pastelgreen-600 font-medium animate-in fade-in">
            <Check className="w-4 h-4" aria-hidden="true" />
            {t('saved')}
          </span>
        )}
      </div>

      {/* Collapsible content */}
      {expanded && (
        <div className="px-5 pb-5 space-y-5">
          {/* Email Notifications toggle */}
          <div className="flex items-center justify-between gap-4 p-4 rounded-lg bg-neutral-50">
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
          <div className="flex items-center justify-between gap-4 p-4 rounded-lg bg-neutral-50">
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

          {/* Channel display */}
          <div className="flex items-center gap-2 px-4">
            <span className="text-xs text-neutral-500">{t('channel')}:</span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-azure-50 text-azure-700 rounded-full border border-azure-200">
              <Mail className="w-3 h-3" aria-hidden="true" />
              {t('channelEmail')}
            </span>
            <span className="text-xs text-neutral-400 italic">{t('channelTelegram')}</span>
          </div>

          {/* Generate Digest button */}
          {preferences.daily_digest && (
            <div className="pt-2">
              <button
                onClick={handleGenerateDigest}
                disabled={digestLoading}
                className="inline-flex items-center gap-2 px-4 py-2 text-sm font-medium rounded-lg bg-azure-600 text-white hover:bg-azure-700 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {digestLoading ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                    {t('generateDigestLoading')}
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4" aria-hidden="true" />
                    {t('generateDigest')}
                  </>
                )}
              </button>

              {digestSuccess && (
                <p className="mt-2 text-sm text-pastelgreen-600 font-medium flex items-center gap-1">
                  <Check className="w-4 h-4" aria-hidden="true" />
                  {t('generateDigestSuccess')}
                </p>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
