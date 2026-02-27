import type { useTranslations } from 'next-intl';
import type { Education } from '../_utils/constants';

export interface TalentEducationProps {
  educations: Education[];
  t: ReturnType<typeof useTranslations>;
  tProfile: ReturnType<typeof useTranslations>;
}
