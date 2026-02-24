'use client';

import { useTranslations } from 'next-intl';
import { useEffect } from 'react';
import { GraduationCap, ExternalLink, X, Star } from 'lucide-react';
import { TechTag } from '@/components/ui/TechTag';
import { levelBadgeColor } from '../_utils/constants';
import type { Course } from '../_utils/types';
import { Badge } from './Badge';

export interface CourseDetailDialogProps {
  course: Course;
  onClose: () => void;
}

export function CourseDetailDialog({ course, onClose }: CourseDetailDialogProps) {
  const t = useTranslations('courses');

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  // Close on Escape
  useEffect(() => {
    function handleEsc(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
    }
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose} role="presentation">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="course-dialog-title"
        className="relative bg-white rounded-3xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 bg-neutral-100 rounded-full flex items-center justify-center hover:bg-neutral-200 transition-colors cursor-pointer z-10"
          aria-label={t('dialog.closeLabel')}
        >
          <X className="w-4 h-4 text-neutral-600" />
        </button>

        <div className="p-8">
          {/* Header */}
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center shrink-0 border border-neutral-200">
              <GraduationCap className="w-7 h-7 text-neutral-400" />
            </div>
            <div>
              <h2 id="course-dialog-title" className="text-2xl font-heading font-semibold text-black-950">
                {course.title}
              </h2>
              <p className="text-azure-600 font-medium mt-1">{course.provider}</p>
              {course.instructor && (
                <p className="text-xs text-neutral-400 mt-1">
                  {t('card.instructor')}: {course.instructor}
                </p>
              )}
            </div>
          </div>

          {/* Badges */}
          <div className="flex flex-wrap gap-2 mt-6">
            <Badge className={levelBadgeColor(course.level)}>
              {t(`levels.${course.level}` as 'levels.beginner' | 'levels.intermediate' | 'levels.advanced')}
            </Badge>
            {course.duration && (
              <Badge className="bg-neutral-100 text-neutral-600 border-neutral-200">
                {course.duration}
              </Badge>
            )}
            {course.price !== null && (
              <Badge className="bg-yellow-50 text-yellow-500 border-yellow-400/30">
                {course.price === '0' || course.price === 'free' ? t('card.free') : course.price}
              </Badge>
            )}
            {course.rating && (
              <Badge className="bg-yellow-50 text-yellow-500 border-yellow-400/30">
                <Star className="w-3 h-3" aria-hidden="true" /> {course.rating}
              </Badge>
            )}
            {course.students_count !== null && (
              <Badge className="bg-azure-50 text-azure-700 border-azure-300/30">
                {t('card.students')}: {course.students_count.toLocaleString('it-IT')}
              </Badge>
            )}
          </div>

          {/* Tags */}
          {course.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-5">
              {course.tags.map((tag, i) => (
                <TechTag key={tag} tag={tag} primary={i < 2} />
              ))}
            </div>
          )}

          {/* Description */}
          <div className="mt-6 pt-6 border-t border-neutral-200">
            <h3 className="text-sm font-semibold text-neutral-900 mb-3">{t('dialog.description')}</h3>
            <p className="text-sm text-neutral-600 leading-relaxed whitespace-pre-line">
              {course.description}
            </p>
          </div>

          {/* CTA */}
          <div className="mt-8 flex gap-3">
            <a
              href={course.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer"
            >
              {t('dialog.goToCourse')}
              <ExternalLink className="w-4 h-4" />
            </a>
            <button
              onClick={onClose}
              className="px-6 py-3 bg-neutral-100 text-neutral-700 font-medium rounded-xl hover:bg-neutral-200 transition-colors cursor-pointer"
            >
              {t('dialog.close')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
