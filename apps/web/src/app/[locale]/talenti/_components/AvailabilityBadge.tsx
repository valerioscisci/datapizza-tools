'use client';

import { AvailabilityBadgeProps } from './AvailabilityBadge.props';

export function AvailabilityBadge({ status, label }: AvailabilityBadgeProps) {
  const colors: Record<string, string> = {
    available: 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30',
    employed: 'bg-azure-50 text-azure-700 border-azure-300/30',
    reskilling: 'bg-yellow-50 text-yellow-500 border-yellow-400/30',
  };

  return (
    <span
      className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full border ${colors[status] || 'bg-neutral-100 text-neutral-600 border-neutral-200'}`}
    >
      {label}
    </span>
  );
}
