'use client';

import { BadgeProps } from './Badge.props';

export function Badge({ children, className }: BadgeProps) {
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full border ${className}`}>
      {children}
    </span>
  );
}
