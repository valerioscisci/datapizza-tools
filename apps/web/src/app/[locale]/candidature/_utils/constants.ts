export const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

export const STATUS_TABS = ['proposta', 'da_completare', 'attiva', 'archiviata'] as const;

export const TAB_LABEL_MAP: Record<string, string> = {
  proposta: 'proposte',
  da_completare: 'da_completare',
  attiva: 'attive',
  archiviata: 'archiviate',
};

export function statusBadgeStyle(status: string): string {
  switch (status) {
    case 'attiva': return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
    case 'proposta': return 'bg-azure-50 text-azure-700 border-azure-300/30';
    case 'da_completare': return 'bg-yellow-50 text-yellow-500 border-yellow-400/30';
    case 'archiviata': return 'bg-neutral-100 text-neutral-500 border-neutral-300/30';
    default: return 'bg-neutral-100 text-neutral-600 border-neutral-200';
  }
}
