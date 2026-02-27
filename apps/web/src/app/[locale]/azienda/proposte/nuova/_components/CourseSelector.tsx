'use client';

import { Search, Check, Loader2, GraduationCap } from 'lucide-react';
import { levelBadgeStyle } from '../_utils/constants';
import { CourseSelectorProps } from './CourseSelector.props';

export function CourseSelector({
  filteredCourses,
  courseSearch,
  setCourseSearch,
  isSelected,
  toggleCourse,
  loadingCourses,
  t,
  tCourses,
}: CourseSelectorProps) {
  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200">
      <h2 className="text-xl font-heading font-semibold text-black-950 flex items-center gap-2 mb-4">
        <GraduationCap className="w-5 h-5 text-azure-600" aria-hidden="true" />
        {t('selectCourses')}
      </h2>

      {/* Course Search */}
      <div className="relative mb-4">
        <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-4 h-4 text-neutral-400" aria-hidden="true" />
        <input
          type="text"
          value={courseSearch}
          onChange={(e) => setCourseSearch(e.target.value)}
          placeholder={t('searchCourses')}
          className="w-full pl-10 pr-4 py-2.5 border border-neutral-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-azure-500 focus:border-azure-500"
        />
      </div>

      {/* Available Courses */}
      {loadingCourses ? (
        <div className="flex items-center gap-2 text-neutral-500 py-4">
          <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
          <span>{tCourses('loading')}</span>
        </div>
      ) : filteredCourses.length === 0 ? (
        <p className="text-sm text-neutral-400 py-4">{t('noCourses')}</p>
      ) : (
        <div className="max-h-64 overflow-y-auto space-y-2 border border-neutral-100 rounded-xl p-2">
          {filteredCourses.map((course) => {
            const selected = isSelected(course.id);
            return (
              <div
                key={course.id}
                onClick={() => toggleCourse(course)}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleCourse(course); } }}
                tabIndex={0}
                role="checkbox"
                aria-checked={selected}
                className={`flex items-center gap-3 p-3 rounded-xl cursor-pointer transition-colors ${
                  selected
                    ? 'bg-azure-50 border border-azure-300/30'
                    : 'bg-neutral-50 border border-neutral-100 hover:border-azure-200'
                }`}
              >
                <div className={`w-5 h-5 rounded flex items-center justify-center shrink-0 ${
                  selected
                    ? 'bg-azure-600 text-white'
                    : 'border-2 border-neutral-300'
                }`}>
                  {selected && <Check className="w-3 h-3" aria-hidden="true" />}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-black-950">{course.title}</p>
                  <div className="flex items-center gap-2 mt-0.5">
                    {course.provider && (
                      <span className="text-xs text-neutral-500">{course.provider}</span>
                    )}
                    {course.duration && (
                      <span className="text-xs text-neutral-400">{course.duration}</span>
                    )}
                  </div>
                </div>
                {course.level && (
                  <span className={`inline-flex items-center px-2 py-0.5 text-xs font-medium rounded-full border shrink-0 ${levelBadgeStyle(course.level)}`}>
                    {tCourses(`levels.${course.level}` as Parameters<typeof tCourses>[0])}
                  </span>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
