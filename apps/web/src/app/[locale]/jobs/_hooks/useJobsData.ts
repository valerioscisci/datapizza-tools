import { useState, useCallback } from 'react';
import { API_BASE } from '../_utils/constants';
import type { Job, JobListResponse } from '../_utils/types';

export function useJobsData() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchJobs = useCallback(async (page: number, filter: string) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: '10',
      });
      if (filter !== 'all') {
        params.set('work_mode', filter);
      }
      const res = await fetch(`${API_BASE}/api/v1/jobs?${params}`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: JobListResponse = await res.json();
      setJobs(data.items);
      setTotal(data.total);
    } catch {
      setJobs([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, []);

  return { jobs, total, loading, fetchJobs };
}
