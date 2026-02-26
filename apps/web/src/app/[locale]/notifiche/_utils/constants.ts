export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

export type EmailType =
  | 'proposal_received' | 'proposal_accepted' | 'proposal_rejected'
  | 'course_started' | 'course_completed' | 'milestone_reached'
  | 'hiring_confirmation' | 'daily_digest';

export interface EmailLog {
  id: string;
  recipient_email: string;
  sender_label: string;
  email_type: EmailType;
  subject: string;
  body_html: string;
  body_text: string | null;
  related_proposal_id: string | null;
  is_read: boolean;
  created_at: string;
}

export interface EmailListResponse {
  items: EmailLog[];
  total: number;
  page: number;
  page_size: number;
  unread_count: number;
}

export interface NotificationPreference {
  email_notifications: boolean;
  daily_digest: boolean;
  channel: string;
  telegram_notifications: boolean;
  telegram_chat_id: string | null;
}

export const EMAIL_TYPE_FILTERS: Array<{ key: string; types: EmailType[] }> = [
  { key: 'all', types: [] },
  { key: 'unread', types: [] },
  { key: 'proposals', types: ['proposal_received', 'proposal_accepted', 'proposal_rejected'] },
  { key: 'courses', types: ['course_started', 'course_completed'] },
  { key: 'milestones', types: ['milestone_reached'] },
  { key: 'hiring', types: ['hiring_confirmation'] },
  { key: 'digest', types: ['daily_digest'] },
];

export function emailTypeBadgeStyle(type: EmailType): string {
  switch (type) {
    case 'proposal_received': return 'bg-azure-100 text-azure-700 border-azure-200';
    case 'proposal_accepted': return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
    case 'proposal_rejected': return 'bg-red-50 text-red-600 border-red-200';
    case 'course_started': return 'bg-yellow-50 text-yellow-600 border-yellow-200';
    case 'course_completed': return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
    case 'milestone_reached': return 'bg-fuchsia-50 text-fuchsia-600 border-fuchsia-200';
    case 'hiring_confirmation': return 'bg-emerald-50 text-emerald-600 border-emerald-200';
    case 'daily_digest': return 'bg-azure-50 text-azure-600 border-azure-200';
    default: return 'bg-neutral-100 text-neutral-500 border-neutral-200';
  }
}

export function formatRelativeTime(
  dateStr: string,
  t: (key: string, values?: Record<string, string | number>) => string
): string {
  const now = new Date();
  const date = new Date(dateStr);
  const diffMs = now.getTime() - date.getTime();
  const diffMin = Math.floor(diffMs / 60000);
  const diffHr = Math.floor(diffMin / 60);
  const diffDays = Math.floor(diffHr / 24);

  if (diffMin < 0) return t('time.now');
  if (diffMin < 1) return t('time.now');
  if (diffMin < 60) return t('time.minutesAgo', { count: diffMin });
  if (diffHr < 24) return t('time.hoursAgo', { count: diffHr });
  if (diffDays < 7) return t('time.daysAgo', { count: diffDays });
  return date.toLocaleDateString('it-IT', { day: 'numeric', month: 'short', year: 'numeric' });
}
