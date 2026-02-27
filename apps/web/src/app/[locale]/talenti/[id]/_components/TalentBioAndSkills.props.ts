import type { useTranslations } from 'next-intl';
import type { TalentDetail } from '../_utils/constants';

export interface TalentBioAndSkillsProps {
  talent: TalentDetail;
  t: ReturnType<typeof useTranslations>;
}
