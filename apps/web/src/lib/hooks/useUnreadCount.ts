'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '@/lib/auth/use-auth';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';
const POLL_INTERVAL_MS = 60_000;

interface UseUnreadCountReturn {
  count: number;
  loading: boolean;
  refetch: () => void;
}

export function useUnreadCount(): UseUnreadCountReturn {
  const { accessToken, isAuthenticated } = useAuth();
  const [count, setCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const fetchCount = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/notifications/unread-count`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: { count: number } = await res.json();
      setCount(data.count);
    } catch {
      // Silently ignore errors for unread count
    } finally {
      setLoading(false);
    }
  }, [accessToken]);

  useEffect(() => {
    if (!isAuthenticated || !accessToken) {
      setCount(0);
      return;
    }

    fetchCount();

    intervalRef.current = setInterval(fetchCount, POLL_INTERVAL_MS);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [isAuthenticated, accessToken, fetchCount]);

  return { count, loading, refetch: fetchCount };
}
