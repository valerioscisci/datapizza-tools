'use client';

import { useTranslations } from 'next-intl';
import { useEffect, useState } from 'react';
import { CATEGORY_FILTERS } from '../_utils/constants';
import { useCoursesData } from '../_hooks/useCoursesData';
import type { Course } from '../_utils/types';
import { CourseCard } from './CourseCard';
import { CourseDetailDialog } from './CourseDetailDialog';

export function CoursesPage() {
  const t = useTranslations('courses');
  const [page, setPage] = useState(1);
  const [filter, setFilter] = useState<string>('all');
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);
  const { courses, total, loading, fetchCourses } = useCoursesData();

  useEffect(() => {
    fetchCourses(page, filter);
  }, [page, filter, fetchCourses]);

  return (
    <>
      {/* Header */}
      <section className="bg-linear-to-b from-azure-25 to-white py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-heading font-semibold text-black-950">
            {t('title')}
          </h1>
          <p className="mt-4 text-lg text-neutral-600 max-w-2xl mx-auto">
            {t('subtitle')}
          </p>
        </div>
      </section>

      {/* Filters + Courses */}
      <section className="py-8 sm:py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Filters */}
          <div className="flex flex-wrap gap-2 mb-8">
            {CATEGORY_FILTERS.map((cat) => (
              <button
                key={cat}
                onClick={() => { setFilter(cat); setPage(1); }}
                aria-pressed={filter === cat}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                  filter === cat
                    ? 'bg-azure-600 text-white'
                    : 'bg-white text-neutral-600 border border-neutral-200 hover:border-azure-300 hover:text-azure-600'
                }`}
              >
                {t(`filters.${cat}`)}
              </button>
            ))}
          </div>

          {/* Course Cards */}
          <div aria-live="polite">
          {loading ? (
            <div className="text-center py-16">
              <p className="text-neutral-500">{t('loading')}</p>
            </div>
          ) : courses.length === 0 ? (
            <div className="text-center py-16">
              <p className="text-neutral-500">{t('empty')}</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {courses.map((course) => (
                <CourseCard
                  key={course.id}
                  course={course}
                  onClick={() => setSelectedCourse(course)}
                />
              ))}
            </div>
          )}
          </div>

          {/* Pagination */}
          {total > 10 && (
            <div className="flex justify-center gap-2 mt-8">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 text-sm font-medium rounded-lg bg-white border border-neutral-200 text-neutral-600 hover:border-azure-300 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {t('pagination.previous')}
              </button>
              <span className="px-4 py-2 text-sm text-neutral-500">
                {t('pagination.page', { current: page, total: Math.ceil(total / 10) })}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(total / 10)}
                className="px-4 py-2 text-sm font-medium rounded-lg bg-white border border-neutral-200 text-neutral-600 hover:border-azure-300 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {t('pagination.next')}
              </button>
            </div>
          )}
        </div>
      </section>

      {/* Course Detail Dialog */}
      {selectedCourse && (
        <CourseDetailDialog
          course={selectedCourse}
          onClose={() => setSelectedCourse(null)}
        />
      )}
    </>
  );
}
