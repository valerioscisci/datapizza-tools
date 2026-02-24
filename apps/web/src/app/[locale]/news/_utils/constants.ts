export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

export const CATEGORY_FILTERS = ['all', 'AI', 'tech', 'careers'] as const;

export function categoryBadgeColor(category: string): string {
  switch (category) {
    case 'AI': return 'bg-azure-50 text-azure-700 border-azure-300/30';
    case 'tech': return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
    case 'careers': return 'bg-yellow-50 text-yellow-500 border-yellow-400/30';
    default: return 'bg-neutral-100 text-neutral-600 border-neutral-200';
  }
}
