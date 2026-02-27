import type { MissingSkill, CourseDetail } from '../_utils/constants';

export interface MissingSkillsSectionProps {
  skills: MissingSkill[];
  courseDetails: Record<string, CourseDetail>;
  userSkills?: string[];
}
