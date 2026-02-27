import type { Course } from '../_utils/types';

export interface CourseCardProps {
  course: Course;
  onClick: () => void;
}
