import type { useTranslations } from 'next-intl';
import type { Experience, ExperienceFormData } from '../_utils/constants';

export interface ExperienceFormProps {
  experience: Experience | null;
  onSave: (data: ExperienceFormData) => void;
  onCancel: () => void;
  saving: boolean;
  t: ReturnType<typeof useTranslations>;
}
