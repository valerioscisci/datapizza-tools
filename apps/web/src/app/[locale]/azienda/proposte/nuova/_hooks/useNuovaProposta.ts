'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useAuth } from '@/lib/auth/use-auth';
import {
  API_BASE,
  TalentInfo,
  Course,
  CourseListResponse,
  SelectedCourse,
} from '../_utils/constants';

export function useNuovaProposta() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { user, accessToken, loading, isCompany } = useAuth();

  const talentId = searchParams.get('talent_id');

  const [talent, setTalent] = useState<TalentInfo | null>(null);
  const [courses, setCourses] = useState<Course[]>([]);
  const [selectedCourses, setSelectedCourses] = useState<SelectedCourse[]>([]);
  const [courseSearch, setCourseSearch] = useState('');
  const [message, setMessage] = useState('');
  const [budgetRange, setBudgetRange] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  const [loadingTalent, setLoadingTalent] = useState(true);
  const [loadingCourses, setLoadingCourses] = useState(true);

  // Auth guard
  useEffect(() => {
    if (!loading && !user) {
      router.push('/it/login');
    }
    if (!loading && user && !isCompany) {
      router.push('/it/proposte');
    }
  }, [user, loading, router, isCompany]);

  // Fetch talent info
  const fetchTalent = useCallback(async () => {
    if (!talentId) {
      setLoadingTalent(false);
      return;
    }
    setLoadingTalent(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/talents/${talentId}`);
      if (!res.ok) throw new Error('Not found');
      const data: TalentInfo = await res.json();
      setTalent(data);
    } catch {
      setTalent(null);
    } finally {
      setLoadingTalent(false);
    }
  }, [talentId]);

  // Fetch courses
  const fetchCourses = useCallback(async () => {
    setLoadingCourses(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/courses?page_size=50`);
      if (!res.ok) throw new Error('Failed to fetch');
      const data: CourseListResponse = await res.json();
      setCourses(data.items);
    } catch {
      setCourses([]);
    } finally {
      setLoadingCourses(false);
    }
  }, []);

  useEffect(() => {
    fetchTalent();
    fetchCourses();
  }, [fetchTalent, fetchCourses]);

  // Filter courses by search
  const filteredCourses = courses.filter((course) => {
    if (!courseSearch.trim()) return true;
    const search = courseSearch.toLowerCase();
    return (
      course.title.toLowerCase().includes(search) ||
      (course.provider?.toLowerCase().includes(search) ?? false) ||
      (course.category?.toLowerCase().includes(search) ?? false)
    );
  });

  const isSelected = (courseId: string) =>
    selectedCourses.some((sc) => sc.course.id === courseId);

  const toggleCourse = (course: Course) => {
    if (isSelected(course.id)) {
      setSelectedCourses((prev) =>
        prev
          .filter((sc) => sc.course.id !== course.id)
          .map((sc, i) => ({ ...sc, order: i }))
      );
    } else {
      setSelectedCourses((prev) => [
        ...prev,
        { course, order: prev.length },
      ]);
    }
  };

  const moveCourse = (index: number, direction: 'up' | 'down') => {
    setSelectedCourses((prev) => {
      const newIndex = direction === 'up' ? index - 1 : index + 1;
      if (newIndex < 0 || newIndex >= prev.length) return prev;
      const itemAtIndex = prev[index];
      const itemAtNewIndex = prev[newIndex];
      if (!itemAtIndex || !itemAtNewIndex) return prev;
      const next = prev.map((sc, i) => {
        if (i === index) return { ...itemAtNewIndex, order: i };
        if (i === newIndex) return { ...itemAtIndex, order: i };
        return { ...sc, order: i };
      });
      return next;
    });
  };

  const removeCourse = (courseId: string) => {
    setSelectedCourses((prev) =>
      prev
        .filter((sc) => sc.course.id !== courseId)
        .map((sc, i) => ({ ...sc, order: i }))
    );
  };

  const handleSubmit = async (e: React.FormEvent, errorMessage: string) => {
    e.preventDefault();
    setError('');

    if (selectedCourses.length === 0) {
      setError(errorMessage);
      return;
    }

    if (!talentId) return;

    setSubmitting(true);
    try {
      const payload = {
        talent_id: talentId,
        message: message.trim() || null,
        budget_range: budgetRange.trim() || null,
        course_ids: selectedCourses.map((sc) => sc.course.id),
      };

      const res = await fetch(`${API_BASE}/api/v1/proposals`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Error' }));
        throw new Error(err.detail || 'Error');
      }

      setSuccess(true);
      setTimeout(() => {
        router.push('/it/azienda/proposte');
      }, 1500);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    } finally {
      setSubmitting(false);
    }
  };

  return {
    user,
    loading,
    isCompany,
    talent,
    loadingTalent,
    courses,
    filteredCourses,
    selectedCourses,
    courseSearch,
    setCourseSearch,
    message,
    setMessage,
    budgetRange,
    setBudgetRange,
    submitting,
    error,
    success,
    loadingCourses,
    isSelected,
    toggleCourse,
    moveCourse,
    removeCourse,
    handleSubmit,
  };
}
