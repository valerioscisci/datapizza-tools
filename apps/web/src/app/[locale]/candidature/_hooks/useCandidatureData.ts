import { useState, useCallback } from 'react';
import { API_BASE } from '../_utils/constants';
import type { Application, ApplicationListResponse } from '../_utils/types';

export function useCandidatureData() {
  const [applications, setApplications] = useState<Application[]>([]);
  const [counts, setCounts] = useState<Record<string, number>>({});
  const [fetching, setFetching] = useState(true);

  const fetchApplications = useCallback(async (status: string, accessToken: string) => {
    setFetching(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/applications?status=${status}`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error('Failed to fetch');
      const data: ApplicationListResponse = await res.json();
      setApplications(data.items);
      setCounts(data.counts);
    } catch {
      setApplications([]);
    } finally {
      setFetching(false);
    }
  }, []);

  return { applications, counts, fetching, fetchApplications };
}
