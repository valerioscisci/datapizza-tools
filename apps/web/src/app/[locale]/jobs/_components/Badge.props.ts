import type React from 'react';

export interface BadgeProps {
  children: React.ReactNode;
  variant?: 'salary' | 'experience' | 'work_mode' | 'location' | 'welfare' | 'smart' | 'language' | 'default';
}
