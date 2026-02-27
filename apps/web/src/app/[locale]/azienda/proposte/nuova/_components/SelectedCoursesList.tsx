'use client';

import { ArrowUp, ArrowDown, X } from 'lucide-react';
import { SelectedCoursesListProps } from './SelectedCoursesList.props';

export function SelectedCoursesList({
  selectedCourses,
  moveCourse,
  removeCourse,
  t,
}: SelectedCoursesListProps) {
  if (selectedCourses.length === 0) return null;

  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200">
      <h2 className="text-xl font-heading font-semibold text-black-950 mb-4">
        {t('selectedCourses')} ({selectedCourses.length})
      </h2>
      <div className="space-y-2">
        {selectedCourses.map((sc, index) => (
          <div
            key={sc.course.id}
            className="flex items-center gap-2 p-3 bg-azure-50 rounded-xl border border-azure-300/30"
          >
            <span className="text-xs font-semibold text-azure-700 w-6 text-center shrink-0">
              {index + 1}
            </span>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-black-950">{sc.course.title}</p>
              {sc.course.provider && (
                <span className="text-xs text-neutral-500">{sc.course.provider}</span>
              )}
            </div>
            <div className="flex items-center gap-1 shrink-0">
              <button
                type="button"
                onClick={() => moveCourse(index, 'up')}
                disabled={index === 0}
                className="p-1 text-neutral-400 hover:text-azure-600 disabled:opacity-30 cursor-pointer disabled:cursor-not-allowed"
                aria-label={t('moveUp')}
              >
                <ArrowUp className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => moveCourse(index, 'down')}
                disabled={index === selectedCourses.length - 1}
                className="p-1 text-neutral-400 hover:text-azure-600 disabled:opacity-30 cursor-pointer disabled:cursor-not-allowed"
                aria-label={t('moveDown')}
              >
                <ArrowDown className="w-4 h-4" />
              </button>
              <button
                type="button"
                onClick={() => removeCourse(sc.course.id)}
                className="p-1 text-neutral-400 hover:text-red-500 cursor-pointer"
                aria-label={`${t('removeCourse')} ${sc.course.title}`}
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
