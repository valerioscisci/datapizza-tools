import type { EmailLog } from '../_utils/constants';

export interface EmailCardProps {
  email: EmailLog;
  onClick: () => void;
}
