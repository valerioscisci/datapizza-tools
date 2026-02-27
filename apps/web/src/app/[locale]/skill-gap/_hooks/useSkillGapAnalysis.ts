'use client';

import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '@/lib/auth/use-auth';
import { API_BASE } from '../_utils/constants';
import type { SkillGapAnalysisResponse, CourseDetail } from '../_utils/constants';

export function useSkillGapAnalysis() {
  const { accessToken, isAuthenticated } = useAuth();
  const [analysis, setAnalysis] = useState<SkillGapAnalysisResponse | null>(null);
  const [courseDetails, setCourseDetails] = useState<Record<string, CourseDetail>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Enrich: fetch course details for recommended courses
  const enrichCourses = useCallback(async (data: SkillGapAnalysisResponse) => {
    const courseIds = new Set<string>();
    data.missing_skills.forEach(ms => ms.recommended_courses.forEach(id => courseIds.add(id)));

    const details: Record<string, CourseDetail> = {};
    await Promise.all(
      Array.from(courseIds).map(async (id) => {
        try {
          const res = await fetch(`${API_BASE}/api/v1/courses/${id}`);
          if (res.ok) {
            const course = await res.json();
            details[id] = { id, title: course.title, provider: course.provider, level: course.level, url: course.url };
          }
        } catch { /* ignore */ }
      })
    );
    setCourseDetails(details);
  }, []);

  const loadCached = useCallback(async () => {
    if (!accessToken) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/ai/skill-gap-analysis`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) return;
      const data: SkillGapAnalysisResponse = await res.json();
      setAnalysis(data);
      await enrichCourses(data);
    } catch { /* silently ignore */ }
  }, [accessToken, enrichCourses]);

  const generate = useCallback(async () => {
    if (!accessToken) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/ai/skill-gap-analysis`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: SkillGapAnalysisResponse = await res.json();
      setAnalysis(data);
      await enrichCourses(data);
    } catch {
      setError('error');
    } finally {
      setLoading(false);
    }
  }, [accessToken, enrichCourses]);

  // On mount: try cached
  useEffect(() => {
    if (isAuthenticated && accessToken) {
      loadCached();
    }
  }, [isAuthenticated, accessToken, loadCached]);

  return { analysis, courseDetails, loading, error, generate };
}
