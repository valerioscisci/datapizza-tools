import type { useTranslations } from 'next-intl';
import type { ProfileResponse } from '../_utils/constants';

export interface ProfileEditModalProps {
  profile: ProfileResponse;
  onClose: () => void;
  onSave: (data: Partial<ProfileResponse>) => void;
  saving: boolean;
  t: ReturnType<typeof useTranslations>;
}
