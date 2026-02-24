'use client';

import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '@/lib/auth/use-auth';
import { API_BASE } from '../_utils/constants';
import type { JobMatchResult, JobMatchResponse } from '../_utils/types';

export function useAIJobMatch() {
  const { accessToken, isAuthenticated } = useAuth();
  const [matches, setMatches] = useState<Map<string, JobMatchResult>>(new Map());
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [generatedAt, setGeneratedAt] = useState<string | null>(null);

  const storeMatches = useCallback((response: JobMatchResponse) => {
    const map = new Map<string, JobMatchResult>();
    for (const match of response.matches) {
      map.set(match.job_id, match);
    }
    setMatches(map);
    setGeneratedAt(response.generated_at);
  }, []);

  const loadCachedMatches = useCallback(async () => {
    if (!accessToken) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/ai/job-matches`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) return; // silently ignore 404 or other errors for cached
      const data: JobMatchResponse = await res.json();
      storeMatches(data);
    } catch {
      // Silently ignore cache load failures
    }
  }, [accessToken, storeMatches]);

  const generateMatches = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/ai/job-matches`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });
      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }
      const data: JobMatchResponse = await res.json();
      storeMatches(data);
    } catch {
      setError('error');
    } finally {
      setLoading(false);
    }
  }, [accessToken, storeMatches]);

  const getMatchForJob = useCallback(
    (jobId: string): JobMatchResult | undefined => {
      return matches.get(jobId);
    },
    [matches]
  );

  // On mount: try to load cached matches silently
  useEffect(() => {
    if (isAuthenticated && accessToken) {
      loadCachedMatches();
    }
  }, [isAuthenticated, accessToken, loadCachedMatches]);

  return {
    matches,
    loading,
    error,
    generatedAt,
    generateMatches,
    getMatchForJob,
    hasMatches: matches.size > 0,
  };
}
