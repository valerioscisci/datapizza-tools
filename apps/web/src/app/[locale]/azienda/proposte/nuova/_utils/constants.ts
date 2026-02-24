export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

// --- Types ---

export interface TalentInfo {
  id: string;
  full_name: string;
  current_role: string | null;
  location: string | null;
  skills: string[];
  experience_level: string | null;
  availability_status: string;
}

export interface Course {
  id: string;
  title: string;
  provider: string | null;
  level: string | null;
  duration: string | null;
  category: string | null;
}

export interface CourseListResponse {
  items: Course[];
  total: number;
}

export interface SelectedCourse {
  course: Course;
  order: number;
}

// --- Helpers ---

export function levelBadgeStyle(level: string | null): string {
  switch (level) {
    case 'beginner': return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
    case 'intermediate': return 'bg-azure-50 text-azure-700 border-azure-300/30';
    case 'advanced': return 'bg-red-50 text-red-600 border-red-200';
    default: return 'bg-neutral-100 text-neutral-600 border-neutral-200';
  }
}
