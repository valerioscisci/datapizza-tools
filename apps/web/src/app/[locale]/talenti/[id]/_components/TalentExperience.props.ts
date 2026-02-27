import type { useTranslations } from 'next-intl';
import type { Experience } from '../_utils/constants';

export interface TalentExperienceProps {
  experiences: Experience[];
  t: ReturnType<typeof useTranslations>;
  tProfile: ReturnType<typeof useTranslations>;
}
