import type { useTranslations } from 'next-intl';
import type { TalentDetail } from '../_utils/constants';

export interface TalentHeroProps {
  talent: TalentDetail;
  tProfile: ReturnType<typeof useTranslations>;
}
