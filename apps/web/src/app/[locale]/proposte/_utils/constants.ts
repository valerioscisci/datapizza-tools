export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

export const STATUS_TABS = ['all', 'sent', 'accepted', 'rejected', 'completed', 'hired'] as const;

export interface ProposalCourse {
  id: string;
  course_id: string;
  course_title: string;
  course_provider: string;
  course_level: string;
  is_completed: boolean;
  order: number;
  completed_at: string | null;
  started_at: string | null;
  talent_notes: string | null;
  company_notes: string | null;
  deadline: string | null;
  xp_earned: number;
  course_url: string;
  course_duration: string | null;
  course_category: string | null;
  is_overdue: boolean;
  days_remaining: number | null;
}

export interface Milestone {
  id: string;
  milestone_type: string;
  title: string;
  description: string | null;
  xp_reward: number;
  achieved_at: string;
}

export interface Proposal {
  id: string;
  company_id: string;
  company_name: string;
  talent_id: string;
  talent_name: string;
  message: string | null;
  budget_range: string | null;
  status: string;
  courses: ProposalCourse[];
  progress: number;
  created_at: string;
  updated_at: string;
  total_xp: number;
  milestones: Milestone[];
  hired_at: string | null;
  hiring_notes: string | null;
}

export interface ChatMessage {
  id: string;
  proposal_id: string;
  sender_id: string;
  sender_name: string;
  sender_type: string;
  content: string;
  created_at: string;
}

export interface ChatMessagesResponse {
  items: ChatMessage[];
  total: number;
  page: number;
  page_size: number;
}

export interface ProposalListResponse {
  items: Proposal[];
  total: number;
  page: number;
  page_size: number;
}

export function statusBadgeStyle(status: string): string {
  switch (status) {
    case 'sent': return 'bg-azure-50 text-azure-700 border-azure-300/30';
    case 'accepted': return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
    case 'rejected': return 'bg-red-50 text-red-600 border-red-200';
    case 'completed': return 'bg-fuchsia-50 text-fuchsia-600 border-fuchsia-200';
    case 'hired': return 'bg-emerald-50 text-emerald-600 border-emerald-200';
    default: return 'bg-neutral-100 text-neutral-600 border-neutral-200';
  }
}

export function formatDate(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit', year: 'numeric' });
}

export function milestoneColor(milestoneType: string): string {
  switch (milestoneType) {
    case 'first_course': return 'bg-yellow-50 text-yellow-500 border-yellow-400/30';
    case '25_percent': return 'bg-azure-50 text-azure-600 border-azure-300/30';
    case '50_percent': return 'bg-azure-50 text-azure-600 border-azure-300/30';
    case '75_percent': return 'bg-fuchsia-50 text-fuchsia-600 border-fuchsia-200';
    case 'all_complete': return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
    case 'streak_3': return 'bg-yellow-50 text-yellow-500 border-yellow-400/30';
    default: return 'bg-neutral-100 text-neutral-600 border-neutral-200';
  }
}
