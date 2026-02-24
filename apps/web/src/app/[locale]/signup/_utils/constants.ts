export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

export const INDUSTRY_OPTIONS = [
  'fintech',
  'aiml',
  'saas',
  'ecommerce',
  'healthtech',
  'edtech',
  'cybersecurity',
  'dataAnalytics',
  'consulting',
  'other',
] as const;
