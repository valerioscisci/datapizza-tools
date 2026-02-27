import type { useTranslations } from 'next-intl';
import type { Course } from '../_utils/constants';

export interface CourseSelectorProps {
  filteredCourses: Course[];
  courseSearch: string;
  setCourseSearch: (value: string) => void;
  isSelected: (courseId: string) => boolean;
  toggleCourse: (course: Course) => void;
  loadingCourses: boolean;
  t: ReturnType<typeof useTranslations>;
  tCourses: ReturnType<typeof useTranslations>;
}
