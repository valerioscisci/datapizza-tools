export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

export interface SkillDemandStatus {
  skill: string;
  demand_status: 'green' | 'yellow' | 'red';
  trend_direction: 'up' | 'down' | 'stable';
  trend_percentage: number;
  job_count: number;
}

export interface MissingSkill {
  skill: string;
  demand_level: 'high' | 'medium' | 'low';
  job_count: number;
  recommended_courses: string[];
  reason: string;
}

export interface MarketTrend {
  skill: string;
  direction: 'up' | 'down' | 'stable';
  change_percentage: number;
  job_count: number;
}

export interface SkillGapAnalysisResponse {
  user_skills: SkillDemandStatus[];
  missing_skills: MissingSkill[];
  market_trends: MarketTrend[];
  personalized_insights: string | null;
  no_skills_warning: boolean;
  ai_unavailable: boolean;
  generated_at: string;
  model_used: string | null;
}

export interface CourseDetail {
  id: string;
  title: string;
  provider: string;
  level: string;
  url: string;
}
