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
  MessageCircle,
  Unlink,
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
    linkTelegram,
    unlinkTelegram,
    telegramLinking,
  } = useNotificationPreferences();

  const [expanded, setExpanded] = useState(false);
  const [savedFeedback, setSavedFeedback] = useState(false);
  const [digestSuccess, setDigestSuccess] = useState(false);
  const [showTelegramSetup, setShowTelegramSetup] = useState(false);
  const [telegramChatId, setTelegramChatId] = useState('');
  const [telegramLinkSuccess, setTelegramLinkSuccess] = useState(false);
  const [telegramUnlinkSuccess, setTelegramUnlinkSuccess] = useState(false);

  async function handleToggle(field: 'email_notifications' | 'daily_digest' | 'telegram_notifications') {
    if (!preferences) return;
    const newValue = !preferences[field];
    try {
      await updatePreferences({ [field]: newValue });
      setSavedFeedback(true);
      setTimeout(() => setSavedFeedback(false), 2000);
    } catch {
      // Revert optimistic state — preferences will keep the old value since updatePreferences throws
    }
  }

  async function handleGenerateDigest() {
    const success = await generateDigest();
    if (success) {
      setDigestSuccess(true);
      setTimeout(() => setDigestSuccess(false), 3000);
    }
  }

  async function handleLinkTelegram() {
    if (!telegramChatId.trim()) return;
    try {
      await linkTelegram(telegramChatId.trim());
      setTelegramLinkSuccess(true);
      setShowTelegramSetup(false);
      setTelegramChatId('');
      setTimeout(() => setTelegramLinkSuccess(false), 3000);
    } catch {
      // Link failed — keep the form open
    }
  }

  async function handleUnlinkTelegram() {
    try {
      await unlinkTelegram();
      setTelegramUnlinkSuccess(true);
      setTimeout(() => setTelegramUnlinkSuccess(false), 3000);
    } catch {
      // Unlink failed
    }
  }

  function maskChatId(chatId: string): string {
    if (chatId.length <= 4) return chatId;
    return '****' + chatId.slice(-4);
  }

  if (loading || !preferences) return null;

  const isTelegramLinked = !!preferences.telegram_chat_id;

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
            {isTelegramLinked ? (
              <span className="inline-flex items-center gap-1 px-2 py-0.5 text-xs font-medium bg-pastelgreen-100 text-pastelgreen-600 rounded-full border border-pastelgreen-500/30">
                <MessageCircle className="w-3 h-3" aria-hidden="true" />
                {t('telegram')}
              </span>
            ) : (
              <button
                onClick={() => setShowTelegramSetup(true)}
                className="text-xs text-azure-600 hover:text-azure-700 hover:underline cursor-pointer"
              >
                {t('telegramLink')}
              </button>
            )}
          </div>

          {/* Divider before Telegram section */}
          <div className="border-t border-neutral-200" />

          {/* Telegram Section */}
          <div className="space-y-4">
            {isTelegramLinked ? (
              <>
                {/* Telegram linked status */}
                <div className="flex items-center justify-between gap-4 p-4 rounded-lg bg-pastelgreen-100/50 border border-pastelgreen-500/20">
                  <div className="flex items-center gap-3">
                    <div className="w-8 h-8 bg-pastelgreen-100 rounded-full flex items-center justify-center shrink-0">
                      <MessageCircle className="w-4 h-4 text-pastelgreen-600" aria-hidden="true" />
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-neutral-900 flex items-center gap-1.5">
                        {t('telegramLinked')}
                        <Check className="w-4 h-4 text-pastelgreen-600" aria-hidden="true" />
                      </p>
                      <p className="text-xs text-neutral-500 mt-0.5">
                        Chat ID: {maskChatId(preferences.telegram_chat_id!)}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={handleUnlinkTelegram}
                    disabled={telegramLinking}
                    className="inline-flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {telegramLinking ? (
                      <Loader2 className="w-3.5 h-3.5 animate-spin" aria-hidden="true" />
                    ) : (
                      <Unlink className="w-3.5 h-3.5" aria-hidden="true" />
                    )}
                    {t('telegramUnlink')}
                  </button>
                </div>

                {/* Telegram Notifications toggle */}
                <div className="flex items-center justify-between gap-4 p-4 rounded-lg bg-neutral-50">
                  <div>
                    <p className="text-sm font-semibold text-neutral-900">{t('telegramNotifications')}</p>
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

                {/* Telegram unlink success */}
                {telegramUnlinkSuccess && (
                  <p className="text-sm text-pastelgreen-600 font-medium flex items-center gap-1 px-4">
                    <Check className="w-4 h-4" aria-hidden="true" />
                    {t('telegramUnlinkSuccess')}
                  </p>
                )}
              </>
            ) : (
              <>
                {/* Telegram link prompt */}
                {!showTelegramSetup ? (
                  <div className="flex items-center justify-between gap-4 p-4 rounded-lg bg-neutral-50">
                    <div className="flex items-center gap-3">
                      <MessageCircle className="w-5 h-5 text-neutral-400" aria-hidden="true" />
                      <div>
                        <p className="text-sm font-semibold text-neutral-900">{t('telegram')}</p>
                        <p className="text-xs text-neutral-500 mt-0.5">{t('telegramNotificationsDescription')}</p>
                      </div>
                    </div>
                    <button
                      onClick={() => setShowTelegramSetup(true)}
                      className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg bg-azure-600 text-white hover:bg-azure-700 transition-colors cursor-pointer"
                    >
                      <MessageCircle className="w-4 h-4" aria-hidden="true" />
                      {t('telegramLink')}
                    </button>
                  </div>
                ) : (
                  <div className="p-4 rounded-lg bg-neutral-50 border border-neutral-200 space-y-4">
                    <p className="text-sm font-semibold text-neutral-900">{t('telegramInstructions')}</p>
                    <ol className="space-y-1.5 text-sm text-neutral-600">
                      <li>{t('telegramStep1')}</li>
                      <li>{t('telegramStep2')}</li>
                    </ol>
                    <div className="flex items-center gap-3">
                      <input
                        type="text"
                        value={telegramChatId}
                        onChange={(e) => setTelegramChatId(e.target.value)}
                        placeholder={t('telegramChatIdPlaceholder')}
                        className="flex-1 px-3 py-2 text-sm rounded-lg border border-neutral-300 focus:border-azure-400 focus:ring-1 focus:ring-azure-400 outline-none transition-colors"
                      />
                      <button
                        onClick={handleLinkTelegram}
                        disabled={telegramLinking || !telegramChatId.trim()}
                        className="inline-flex items-center gap-1.5 px-4 py-2 text-sm font-medium rounded-lg bg-azure-600 text-white hover:bg-azure-700 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        {telegramLinking ? (
                          <>
                            <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                            {t('telegramLinking')}
                          </>
                        ) : (
                          t('telegramLink')
                        )}
                      </button>
                    </div>
                    <button
                      onClick={() => {
                        setShowTelegramSetup(false);
                        setTelegramChatId('');
                      }}
                      className="text-xs text-neutral-500 hover:text-neutral-700 cursor-pointer"
                    >
                      {t('cancel')}
                    </button>
                  </div>
                )}

                {/* Telegram link success */}
                {telegramLinkSuccess && (
                  <p className="text-sm text-pastelgreen-600 font-medium flex items-center gap-1 px-4">
                    <Check className="w-4 h-4" aria-hidden="true" />
                    {t('telegramLinkSuccess')}
                  </p>
                )}
              </>
            )}
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
