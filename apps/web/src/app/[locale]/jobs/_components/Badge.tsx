import React from 'react';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'salary' | 'experience' | 'work_mode' | 'location' | 'welfare' | 'smart' | 'language' | 'default';
}

const colors: Record<string, string> = {
  salary: 'bg-yellow-50 text-yellow-500 border-yellow-400/30',
  experience: 'bg-azure-50 text-azure-700 border-azure-300/30',
  work_mode: 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30',
  location: 'bg-neutral-100 text-neutral-700 border-neutral-300/30',
  welfare: 'bg-red-50 text-red-600 border-red-500/30',
  smart: 'bg-neutral-100 text-neutral-600 border-neutral-300/30',
  language: 'bg-azure-50 text-azure-600 border-azure-300/30',
  default: 'bg-neutral-100 text-neutral-600 border-neutral-200',
};

export function Badge({ children, variant = 'default' }: BadgeProps) {
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full border ${colors[variant]}`}>
      {children}
    </span>
  );
}
