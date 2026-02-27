import type { EmailLog } from '../_utils/constants';

export interface EmailDetailDialogProps {
  email: EmailLog;
  onClose: () => void;
}
