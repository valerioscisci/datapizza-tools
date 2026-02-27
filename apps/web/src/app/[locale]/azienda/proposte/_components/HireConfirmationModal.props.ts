import type { useTranslations } from 'next-intl';
import type { Proposal } from '../_utils/constants';

export interface HireConfirmationModalProps {
  proposal: Proposal;
  onConfirm: (hiringNotes: string) => void;
  onCancel: () => void;
  tHire: ReturnType<typeof useTranslations>;
}
