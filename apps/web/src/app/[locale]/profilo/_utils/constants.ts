export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

// --- Types ---

export interface Experience {
  id: string;
  title: string;
  company: string;
  employment_type: string | null;
  location: string | null;
  start_month: number | null;
  start_year: number;
  end_month: number | null;
  end_year: number | null;
  is_current: boolean;
  description: string | null;
  created_at: string;
}

export interface Education {
  id: string;
  institution: string;
  degree: string | null;
  degree_type: string | null;
  field_of_study: string | null;
  start_year: number;
  end_year: number | null;
  is_current: boolean;
  description: string | null;
  created_at: string;
}

export interface ProfileResponse {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  bio: string | null;
  location: string | null;
  experience_level: string | null;
  experience_years: string | null;
  current_role: string | null;
  skills: string[];
  availability_status: string;
  reskilling_status: string | null;
  adopted_by_company: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
  user_type: string;
  ai_readiness_score: number | null;
  ai_readiness_level: string | null;
  is_public: boolean;
  experiences: Experience[];
  educations: Education[];
  created_at: string;
}

export interface ExperienceFormData {
  title: string;
  company: string;
  employment_type: string;
  location: string;
  start_month: string;
  start_year: string;
  end_month: string;
  end_year: string;
  is_current: boolean;
  description: string;
}

export interface EducationFormData {
  institution: string;
  degree: string;
  degree_type: string;
  field_of_study: string;
  start_year: string;
  end_year: string;
  is_current: boolean;
  description: string;
}

// --- AI Career Advice Types ---

export interface RecommendedCourse {
  course_id: string;
  reason: string;
  title?: string;
  provider?: string;
  level?: string;
}

export interface RecommendedArticle {
  news_id: string;
  reason: string;
  title?: string;
  source?: string;
  source_url?: string;
}

export interface CareerAdviceResponse {
  career_direction: string;
  recommended_courses: RecommendedCourse[];
  recommended_articles: RecommendedArticle[];
  skill_gaps: string[];
  generated_at: string;
  model_used: string;
}

// --- AI Readiness Types ---

export interface QuizQuestion {
  id: string;
}

export interface QuizMeta {
  questions: QuizQuestion[];
  version: number;
}

export interface AIReadinessResult {
  id: string;
  total_score: number;
  readiness_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
  answers: Record<string, number>;
  quiz_version: number;
  created_at: string;
}

export interface CourseSuggestion {
  id: string;
  title: string;
  provider: string | null;
  level: string;
  url: string | null;
  category: string;
}

export interface SuggestionsResult {
  suggestions: CourseSuggestion[];
  weak_categories: string[];
}

// --- Helpers ---

export function formatMonthYear(month: number | null, year: number): string {
  if (month) {
    const monthName = new Date(year, month - 1).toLocaleDateString('it-IT', { month: 'long' });
    return `${monthName.charAt(0).toUpperCase() + monthName.slice(1)} ${year}`;
  }
  return `${year}`;
}

export function availabilityBadgeStyle(status: string): string {
  switch (status) {
    case 'available':
      return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
    case 'employed':
      return 'bg-azure-50 text-azure-700 border-azure-300/30';
    case 'reskilling':
      return 'bg-yellow-50 text-yellow-500 border-yellow-400/30';
    default:
      return 'bg-neutral-100 text-neutral-600 border-neutral-200';
  }
}

// --- Constants ---

export const EMPLOYMENT_TYPES = ['full-time', 'part-time', 'contract', 'freelance'] as const;
export const DEGREE_TYPES = ['diploma', 'bachelor', 'master', 'phd', 'certificate'] as const;
export const EXPERIENCE_LEVELS = ['junior', 'mid', 'senior'] as const;
export const AVAILABILITY_OPTIONS = ['available', 'employed', 'reskilling'] as const;

export const MONTHS = Array.from({ length: 12 }, (_, i) => {
  const name = new Date(2024, i).toLocaleDateString('it-IT', { month: 'long' });
  return { value: String(i + 1), label: name.charAt(0).toUpperCase() + name.slice(1) };
});

const currentYear = new Date().getFullYear();
export const YEARS = Array.from({ length: 50 }, (_, i) => String(currentYear - i));
