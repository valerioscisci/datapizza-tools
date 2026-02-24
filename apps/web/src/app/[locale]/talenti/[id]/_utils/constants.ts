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

export interface TalentDetail {
  id: string;
  full_name: string;
  bio: string | null;
  current_role: string | null;
  location: string | null;
  experience_level: string | null;
  experience_years: string | null;
  skills: string[];
  availability_status: string;
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
  experiences: Experience[];
  educations: Education[];
  created_at: string;
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
