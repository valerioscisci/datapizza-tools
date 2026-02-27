import type { useTranslations } from 'next-intl';
import type { Education } from '../_utils/constants';

export interface EducationSectionProps {
  educations: Education[];
  accessToken: string;
  onUpdate: () => void;
  t: ReturnType<typeof useTranslations>;
}
