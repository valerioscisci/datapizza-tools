export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

export const WORK_MODE_FILTERS = ['all', 'remote', 'hybrid', 'onsite'] as const;

export function experienceLevelEmoji(level: string): string {
  switch (level) {
    case 'junior': return '\u{1F331}';
    case 'mid': return '\u{1F468}\u200D\u{1F4BB}';
    case 'senior': return '\u{1F9D1}\u200D\u{1F4BB}';
    default: return '\u{1F464}';
  }
}

export function matchBadgeStyle(score: number): string {
  if (score >= 80) return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
  if (score >= 60) return 'bg-yellow-50 text-yellow-500 border-yellow-400/30';
  return 'bg-neutral-100 text-neutral-500 border-neutral-200';
}
