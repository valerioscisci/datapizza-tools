export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

export const EXPERIENCE_LEVEL_FILTERS = ['all', 'junior', 'mid', 'senior'] as const;
export const AVAILABILITY_FILTERS = ['all', 'available', 'employed', 'reskilling'] as const;
export const AI_READINESS_FILTERS = ['all', 'beginner', 'intermediate', 'advanced', 'expert'] as const;

export interface Talent {
  id: string;
  full_name: string;
  current_role: string | null;
  location: string | null;
  skills: string[];
  experience_level: string | null;
  experience_years: string | null;
  availability_status: string;
  bio: string | null;
  ai_readiness_score: number | null;
  ai_readiness_level: string | null;
}

export interface TalentListResponse {
  items: Talent[];
  total: number;
  page: number;
  page_size: number;
}
