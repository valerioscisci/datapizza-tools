export function formatSalary(
  min: number | null,
  max: number | null,
  t: (key: string, values?: Record<string, string>) => string
): string | null {
  if (min === null && max === null) return null;
  const fmt = (n: number) => `${(n / 1000).toFixed(0)}k`;
  if (min !== null && max !== null) return `${fmt(min)}-${fmt(max)}`;
  if (min !== null) return t('salary.from', { amount: fmt(min) });
  return t('salary.upTo', { amount: fmt(max!) });
}

export function formatDate(dateStr: string, style: 'short' | 'long' = 'long'): string {
  return new Date(dateStr).toLocaleDateString('it-IT', {
    day: 'numeric',
    month: style === 'short' ? 'short' : 'long',
    year: 'numeric',
  });
}

export function workModeLabel(
  mode: string,
  t: (key: string) => string
): string {
  return t(`workModes.${mode}`);
}
