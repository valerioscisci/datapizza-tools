import type { useTranslations } from 'next-intl';
import type { SelectedCourse } from '../_utils/constants';

export interface SelectedCoursesListProps {
  selectedCourses: SelectedCourse[];
  moveCourse: (index: number, direction: 'up' | 'down') => void;
  removeCourse: (courseId: string) => void;
  t: ReturnType<typeof useTranslations>;
}
