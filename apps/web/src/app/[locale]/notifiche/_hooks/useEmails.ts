'use client';

import { useState, useCallback } from 'react';
import { useAuth } from '@/lib/auth/use-auth';
import type { EmailLog, EmailListResponse, EmailType } from '../_utils/constants';
import { API_BASE } from '../_utils/constants';

interface FetchEmailsParams {
  page?: number;
  pageSize?: number;
  emailTypes?: EmailType[];
  isRead?: boolean;
}

interface UseEmailsReturn {
  emails: EmailLog[];
  total: number;
  unreadCount: number;
  page: number;
  pageSize: number;
  loading: boolean;
  error: string | null;
  fetchEmails: (params?: FetchEmailsParams) => Promise<void>;
  markAsRead: (emailId: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  fetchEmail: (emailId: string) => Promise<EmailLog | null>;
}

export function useEmails(): UseEmailsReturn {
  const { accessToken } = useAuth();
  const [emails, setEmails] = useState<EmailLog[]>([]);
  const [total, setTotal] = useState(0);
  const [unreadCount, setUnreadCount] = useState(0);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEmails = useCallback(async (params?: FetchEmailsParams) => {
    if (!accessToken) return;
    setLoading(true);
    setError(null);
    try {
      const searchParams = new URLSearchParams({
        page: String(params?.page ?? 1),
        page_size: String(params?.pageSize ?? 20),
      });

      if (params?.emailTypes && params.emailTypes.length > 0) {
        for (const t of params.emailTypes) {
          searchParams.append('email_type', t);
        }
      }

      if (params?.isRead !== undefined) {
        searchParams.set('is_read', String(params.isRead));
      }

      const res = await fetch(`${API_BASE}/api/v1/notifications/emails?${searchParams}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: EmailListResponse = await res.json();
      setEmails(data.items);
      setTotal(data.total);
      setUnreadCount(data.unread_count);
      setPage(data.page);
      setPageSize(data.page_size);
    } catch {
      setError('error');
      setEmails([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  const markAsRead = useCallback(async (emailId: string) => {
    if (!accessToken) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/notifications/emails/${emailId}/read`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      // Update local state
      setEmails((prev) =>
        prev.map((e) => (e.id === emailId ? { ...e, is_read: true } : e))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
    } catch {
      // Silently ignore mark-as-read errors
    }
  }, [accessToken]);

  const markAllAsRead = useCallback(async () => {
    if (!accessToken) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/notifications/emails/read-all`, {
        method: 'PATCH',
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      setEmails((prev) => prev.map((e) => ({ ...e, is_read: true })));
      setUnreadCount(0);
    } catch {
      // Silently ignore
    }
  }, [accessToken]);

  const fetchEmail = useCallback(async (emailId: string): Promise<EmailLog | null> => {
    if (!accessToken) return null;
    try {
      const res = await fetch(`${API_BASE}/api/v1/notifications/emails/${emailId}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: EmailLog = await res.json();
      // Update local state to mark as read
      setEmails((prev) =>
        prev.map((e) => (e.id === emailId ? { ...e, is_read: true } : e))
      );
      setUnreadCount((prev) => Math.max(0, prev - 1));
      return data;
    } catch {
      return null;
    }
  }, [accessToken]);

  return {
    emails,
    total,
    unreadCount,
    page,
    pageSize,
    loading,
    error,
    fetchEmails,
    markAsRead,
    markAllAsRead,
    fetchEmail,
  };
}
