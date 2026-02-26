'use client';

import { useState, useEffect, useCallback } from 'react';
import { useAuth } from '@/lib/auth/use-auth';
import { API_BASE } from '@/app/[locale]/notifiche/_utils/constants';
import type { NotificationPreference } from '@/app/[locale]/notifiche/_utils/constants';

interface UseNotificationPreferencesReturn {
  preferences: NotificationPreference | null;
  loading: boolean;
  updatePreferences: (data: Partial<NotificationPreference>) => Promise<void>;
  generateDigest: () => Promise<boolean>;
  digestLoading: boolean;
  linkTelegram: (chatId: string) => Promise<void>;
  unlinkTelegram: () => Promise<void>;
  telegramLinking: boolean;
}

export function useNotificationPreferences(): UseNotificationPreferencesReturn {
  const { accessToken, isAuthenticated } = useAuth();
  const [preferences, setPreferences] = useState<NotificationPreference | null>(null);
  const [loading, setLoading] = useState(false);
  const [digestLoading, setDigestLoading] = useState(false);
  const [telegramLinking, setTelegramLinking] = useState(false);

  const fetchPreferences = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/notifications/preferences`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: NotificationPreference = await res.json();
      setPreferences(data);
    } catch {
      // Default preferences on error
      setPreferences({
        email_notifications: true,
        daily_digest: false,
        channel: 'email',
        telegram_notifications: false,
        telegram_chat_id: null,
      });
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  const updatePreferences = useCallback(async (data: Partial<NotificationPreference>) => {
    if (!accessToken) return;
    const res = await fetch(`${API_BASE}/api/v1/notifications/preferences`, {
      method: 'PATCH',
      headers: {
        Authorization: `Bearer ${accessToken}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    const updated: NotificationPreference = await res.json();
    setPreferences(updated);
  }, [accessToken]);

  const linkTelegram = useCallback(async (chatId: string) => {
    if (!accessToken) return;
    setTelegramLinking(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/notifications/telegram/link`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ chat_id: chatId }),
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      // Refresh preferences to get updated telegram_chat_id
      await fetchPreferences();
    } finally {
      setTelegramLinking(false);
    }
  }, [accessToken, fetchPreferences]);

  const unlinkTelegram = useCallback(async () => {
    if (!accessToken) return;
    setTelegramLinking(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/notifications/telegram/link`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      // Refresh preferences to get updated state
      await fetchPreferences();
    } finally {
      setTelegramLinking(false);
    }
  }, [accessToken, fetchPreferences]);

  const generateDigest = useCallback(async (): Promise<boolean> => {
    if (!accessToken) return false;
    setDigestLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/notifications/daily-digest`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      return true;
    } catch {
      return false;
    } finally {
      setDigestLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    if (isAuthenticated && accessToken) {
      fetchPreferences();
    }
  }, [isAuthenticated, accessToken, fetchPreferences]);

  return {
    preferences,
    loading,
    updatePreferences,
    generateDigest,
    digestLoading,
    linkTelegram,
    unlinkTelegram,
    telegramLinking,
  };
}
