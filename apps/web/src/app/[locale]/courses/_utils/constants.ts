export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

export const CATEGORY_FILTERS = ['all', 'AI', 'ML', 'frontend', 'backend', 'devops'] as const;

export function levelBadgeColor(level: string): string {
  switch (level) {
    case 'beginner': return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
    case 'intermediate': return 'bg-azure-50 text-azure-700 border-azure-300/30';
    case 'advanced': return 'bg-red-50 text-red-600 border-red-500/30';
    default: return 'bg-neutral-100 text-neutral-600 border-neutral-200';
  }
}
