import { useState, useCallback } from 'react';
import { API_BASE } from '../_utils/constants';
import type { NewsItem, NewsListResponse } from '../_utils/types';

export function useNewsData() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchNews = useCallback(async (page: number, filter: string) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: '10',
      });
      if (filter !== 'all') {
        params.set('category', filter);
      }
      const res = await fetch(`${API_BASE}/api/v1/news?${params}`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: NewsListResponse = await res.json();
      setNews(data.items);
      setTotal(data.total);
    } catch {
      setNews([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, []);

  return { news, total, loading, fetchNews };
}
