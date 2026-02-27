import type { useTranslations } from 'next-intl';
import type { Education, EducationFormData } from '../_utils/constants';

export interface EducationFormProps {
  education: Education | null;
  onSave: (data: EducationFormData) => void;
  onCancel: () => void;
  saving: boolean;
  t: ReturnType<typeof useTranslations>;
}
