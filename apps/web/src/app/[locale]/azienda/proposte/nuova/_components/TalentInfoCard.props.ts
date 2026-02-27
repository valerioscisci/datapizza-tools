import type { useTranslations } from 'next-intl';
import type { TalentInfo } from '../_utils/constants';

export interface TalentInfoCardProps {
  talent: TalentInfo | null;
  loadingTalent: boolean;
  t: ReturnType<typeof useTranslations>;
  tTalents: ReturnType<typeof useTranslations>;
}
