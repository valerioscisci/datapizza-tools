import type { EmailLog } from '../_utils/constants';

export interface EmailListProps {
  emails: EmailLog[];
  loading: boolean;
  total: number;
  page: number;
  pageSize: number;
  unreadCount: number;
  onEmailClick: (email: EmailLog) => void;
  onMarkAllRead: () => void;
  onPageChange: (page: number) => void;
}
