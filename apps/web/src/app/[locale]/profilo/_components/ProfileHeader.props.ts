import type { useTranslations } from 'next-intl';
import type { ProfileResponse } from '../_utils/constants';

export interface ProfileHeaderProps {
  profile: ProfileResponse;
  onEdit: () => void;
  t: ReturnType<typeof useTranslations>;
}
