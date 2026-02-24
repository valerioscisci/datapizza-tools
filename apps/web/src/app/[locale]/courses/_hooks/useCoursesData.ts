import { useState, useCallback } from 'react';
import { API_BASE } from '../_utils/constants';
import type { Course, CourseListResponse } from '../_utils/types';

export function useCoursesData() {
  const [courses, setCourses] = useState<Course[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const fetchCourses = useCallback(async (page: number, filter: string) => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: '10',
      });
      if (filter !== 'all') {
        params.set('category', filter);
      }
      const res = await fetch(`${API_BASE}/api/v1/courses?${params}`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: CourseListResponse = await res.json();
      setCourses(data.items);
      setTotal(data.total);
    } catch {
      setCourses([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, []);

  return { courses, total, loading, fetchCourses };
}
