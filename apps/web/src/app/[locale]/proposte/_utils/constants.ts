export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

export const STATUS_TABS = ['all', 'sent', 'accepted', 'rejected', 'completed'] as const;

export interface ProposalCourse {
  id: string;
  course_id: string;
  course_title: string;
  course_provider: string;
  course_level: string;
  is_completed: boolean;
  order: number;
  completed_at: string | null;
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
    default: return 'bg-neutral-100 text-neutral-600 border-neutral-200';
  }
}

export function formatBudget(budgetRange: string | null): string | null {
  if (!budgetRange) return null;
  return budgetRange;
}
