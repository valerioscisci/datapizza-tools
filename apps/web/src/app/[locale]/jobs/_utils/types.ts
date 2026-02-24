export interface Job {
  id: string;
  title: string;
  company: string;
  company_logo_url: string | null;
  location: string;
  work_mode: string;
  description: string;
  salary_min: number | null;
  salary_max: number | null;
  tags: string[];
  experience_level: string;
  experience_years: string | null;
  employment_type: string;
  smart_working: string | null;
  welfare: string | null;
  language: string | null;
  apply_url: string | null;
  created_at: string;
}

export interface JobListResponse {
  items: Job[];
  total: number;
  page: number;
  page_size: number;
}
