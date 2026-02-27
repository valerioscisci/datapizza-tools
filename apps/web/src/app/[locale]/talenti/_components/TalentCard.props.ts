import type { useTranslations } from 'next-intl';
import type { Talent } from '../_utils/constants';

export interface TalentCardProps {
  talent: Talent;
  onClick: () => void;
  t: ReturnType<typeof useTranslations>;
}
