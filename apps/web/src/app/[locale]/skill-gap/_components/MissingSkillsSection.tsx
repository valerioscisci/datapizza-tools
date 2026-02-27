'use client';

import { useTranslations } from 'next-intl';
import { GraduationCap } from 'lucide-react';
import Link from 'next/link';
import type { MissingSkillsSectionProps } from './MissingSkillsSection.props';

function demandBadgeStyle(level: 'high' | 'medium' | 'low'): string {
  switch (level) {
    case 'high':
      return 'bg-emerald-50 text-emerald-700 border-emerald-200';
    case 'medium':
      return 'bg-amber-50 text-amber-700 border-amber-200';
    case 'low':
      return 'bg-neutral-100 text-neutral-600 border-neutral-200';
  }
}

function demandLabel(level: 'high' | 'medium' | 'low', t: (key: string) => string): string {
  switch (level) {
    case 'high':
      return t('demandHigh');
    case 'medium':
      return t('demandMedium');
    case 'low':
      return t('demandLow');
  }
}

export function MissingSkillsSection({ skills, courseDetails, userSkills = [] }: MissingSkillsSectionProps) {
  const t = useTranslations('skillGap.missingSkills');

  return (
    <div className="border border-neutral-200 rounded-lg bg-white p-6">
      <h3 className="text-lg font-semibold text-black-950 mb-1">{t('title')}</h3>
      <p className="text-sm text-neutral-500 mb-4">{t('subtitle')}</p>

      {skills.length === 0 ? (
        <p className="text-sm text-neutral-400 text-center py-8">{t('noCourses')}</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {skills.map((skill) => (
            <div
              key={skill.skill}
              className="p-4 rounded-lg border border-neutral-200 bg-white hover:border-azure-300 transition-colors"
            >
              {/* Skill name + demand badge */}
              <div className="flex items-start justify-between gap-2 mb-2">
                <h4 className="text-sm font-semibold text-neutral-900">{skill.skill}</h4>
                <span className={`text-xs px-2 py-0.5 rounded-full border shrink-0 ${demandBadgeStyle(skill.demand_level)}`}>
                  {demandLabel(skill.demand_level, t)}
                </span>
              </div>

              {/* Job count */}
              <p className="text-xs text-neutral-500 mb-2">
                {t('inJobs', { count: String(skill.job_count) })}
              </p>

              {/* AI reason */}
              {skill.reason && (
                <p className="text-xs text-neutral-600 italic leading-relaxed mb-3">
                  {skill.reason}
                </p>
              )}

              {/* Recommended courses */}
              {skill.recommended_courses.length > 0 && (
                <div className="mb-3">
                  <p className="text-xs font-medium text-neutral-500 mb-1.5">{t('courses')}</p>
                  <div className="space-y-1.5">
                    {skill.recommended_courses.map((courseId) => {
                      const course = courseDetails[courseId];
                      if (!course) return null;
                      return (
                        <div key={courseId} className="flex items-start gap-1.5">
                          <GraduationCap className="w-3.5 h-3.5 text-azure-600 mt-0.5 shrink-0" aria-hidden="true" />
                          <div className="min-w-0">
                            <p className="text-xs font-medium text-neutral-900 line-clamp-1">{course.title}</p>
                            {course.provider && (
                              <p className="text-xs text-neutral-400">{course.provider}</p>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                  <Link
                    href="/it/courses"
                    className="inline-flex items-center gap-1.5 mt-2 text-xs font-medium text-azure-600 hover:text-azure-700"
                  >
                    {t('goToCourse')}
                    <GraduationCap className="w-3 h-3" aria-hidden="true" />
                  </Link>
                </div>
              )}

              {/* Add to profile CTA — hidden if skill already in profile */}
              {!userSkills.includes(skill.skill) && (
                <Link
                  href={`/it/profilo?addSkill=${encodeURIComponent(skill.skill)}`}
                  className="text-xs font-medium text-azure-600 hover:text-azure-700"
                >
                  {t('addToProfile')}
                </Link>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
