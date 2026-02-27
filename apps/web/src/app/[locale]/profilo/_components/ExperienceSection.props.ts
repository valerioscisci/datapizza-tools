import type { useTranslations } from 'next-intl';
import type { Experience } from '../_utils/constants';

export interface ExperienceSectionProps {
  experiences: Experience[];
  accessToken: string;
  onUpdate: () => void;
  t: ReturnType<typeof useTranslations>;
}
