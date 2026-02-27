import { useTranslations } from 'next-intl';
import { GraduationCap, ChevronDown, Star } from 'lucide-react';
import { TechTag } from '@/components/ui/TechTag';
import { levelBadgeColor } from '../_utils/constants';
import { Badge } from './Badge';
import { CourseCardProps } from './CourseCard.props';

export function CourseCard({ course, onClick }: CourseCardProps) {
  const t = useTranslations('courses');

  return (
    <div
      onClick={onClick}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick(); } }}
      tabIndex={0}
      role="button"
      className="p-6 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 hover:shadow-lg transition-all duration-300 cursor-pointer group"
    >
      <div className="flex items-start gap-4">
        {/* Icon placeholder */}
        <div className="w-14 h-14 bg-neutral-100 rounded-full flex items-center justify-center shrink-0 border border-neutral-200">
          <GraduationCap className="w-6 h-6 text-neutral-400" />
        </div>

        <div className="flex-1 min-w-0">
          {/* Title */}
          <h3 className="text-lg font-semibold text-black-950 group-hover:text-azure-600 transition-colors">
            {course.title}
          </h3>
          {/* Provider */}
          <p className="text-sm text-azure-600 font-medium mt-0.5">{course.provider}</p>
        </div>

        {/* Expand hint */}
        <ChevronDown className="w-5 h-5 text-neutral-300 group-hover:text-azure-400 transition-colors shrink-0 mt-1" />
      </div>

      {/* Badges row */}
      <div className="flex flex-wrap gap-2 mt-4">
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
      </div>

      {/* Tags */}
      {course.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {course.tags.map((tag, i) => (
            <TechTag key={tag} tag={tag} primary={i < 2} />
          ))}
        </div>
      )}

      {/* Description */}
      <p className="mt-4 text-sm text-neutral-500 line-clamp-3 leading-relaxed">
        {course.description}
      </p>
    </div>
  );
}
