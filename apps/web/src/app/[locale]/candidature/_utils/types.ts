export interface ApplicationJob {
  id: string;
  title: string;
  company: string;
  location: string;
  work_mode: string;
  salary_min: number | null;
  salary_max: number | null;
  tags: string[];
  experience_level: string;
  experience_years: string | null;
  smart_working: string | null;
  welfare: string | null;
}

export interface Application {
  id: string;
  job: ApplicationJob;
  status: string;
  status_detail: string | null;
  recruiter_name: string | null;
  recruiter_role: string | null;
  applied_at: string;
  updated_at: string | null;
}

export interface ApplicationListResponse {
  items: Application[];
  total: number;
  counts: Record<string, number>;
}
