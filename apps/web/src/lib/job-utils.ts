export function formatSalary(min: number | null, max: number | null): string | null {
  if (min === null && max === null) return null;
  const fmt = (n: number) => `${(n / 1000).toFixed(0)}k`;
  if (min !== null && max !== null) return `${fmt(min)}-${fmt(max)}`;
  if (min !== null) return `da ${fmt(min)}`;
  return `fino a ${fmt(max!)}`;
}

export function formatDate(dateStr: string, style: 'short' | 'long' = 'long'): string {
  return new Date(dateStr).toLocaleDateString('it-IT', {
    day: 'numeric',
    month: style === 'short' ? 'short' : 'long',
    year: 'numeric',
  });
}

export function workModeLabel(mode: string): string {
  switch (mode) {
    case 'remote': return 'Full Remote';
    case 'hybrid': return 'Ibrido';
    case 'onsite': return 'In Sede';
    default: return mode;
  }
}
