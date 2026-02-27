import type { Course } from '../_utils/types';

export interface CourseDetailDialogProps {
  course: Course;
  onClose: () => void;
}
