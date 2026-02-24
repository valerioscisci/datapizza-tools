'use client';

import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '@/lib/auth/use-auth';
import { API_BASE } from '../_utils/constants';
import type { CareerAdviceResponse } from '../_utils/constants';

export function useAICareerAdvice() {
  const { accessToken, isAuthenticated } = useAuth();
  const [advice, setAdvice] = useState<CareerAdviceResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const enrichAdvice = useCallback(
    async (data: CareerAdviceResponse): Promise<CareerAdviceResponse> => {
      if (!accessToken) return data;

      const enriched = { ...data };

      // Enrich recommended courses
      const enrichedCourses = await Promise.all(
        data.recommended_courses.map(async (course) => {
          try {
            const res = await fetch(
              `${API_BASE}/api/v1/courses/${course.course_id}`
            );
            if (!res.ok) return course;
            const courseData = await res.json();
            return {
              ...course,
              title: courseData.title,
              provider: courseData.provider,
              level: courseData.level,
            };
          } catch {
            return course;
          }
        })
      );
      enriched.recommended_courses = enrichedCourses;

      // Enrich recommended articles
      const enrichedArticles = await Promise.all(
        data.recommended_articles.map(async (article) => {
          try {
            const res = await fetch(
              `${API_BASE}/api/v1/news/${article.news_id}`
            );
            if (!res.ok) return article;
            const newsData = await res.json();
            return {
              ...article,
              title: newsData.title,
              source: newsData.source,
              source_url: newsData.source_url,
            };
          } catch {
            return article;
          }
        })
      );
      enriched.recommended_articles = enrichedArticles;

      return enriched;
    },
    [accessToken]
  );

  const loadCachedAdvice = useCallback(async () => {
    if (!accessToken) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/ai/career-advice`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) return; // silently ignore 404 for missing cache
      const data: CareerAdviceResponse = await res.json();
      const enrichedData = await enrichAdvice(data);
      setAdvice(enrichedData);
    } catch {
      // Silently ignore cache load failures
    }
  }, [accessToken, enrichAdvice]);

  const generateAdvice = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/ai/career-advice`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });
      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }
      const data: CareerAdviceResponse = await res.json();
      const enrichedData = await enrichAdvice(data);
      setAdvice(enrichedData);
    } catch {
      setError('error');
    } finally {
      setLoading(false);
    }
  }, [accessToken, enrichAdvice]);

  // On mount: try to load cached advice silently
  useEffect(() => {
    if (isAuthenticated && accessToken) {
      loadCachedAdvice();
    }
  }, [isAuthenticated, accessToken, loadCachedAdvice]);

  return {
    advice,
    loading,
    error,
    generateAdvice,
  };
}
