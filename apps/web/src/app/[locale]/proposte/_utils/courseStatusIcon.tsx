import { Check, Clock, Play } from 'lucide-react';
import type { ProposalCourse } from './constants';

export function courseStatusIcon(course: ProposalCourse): {
  bgClass: string;
  icon: React.ReactNode;
} {
  if (course.is_completed) {
    return {
      bgClass: 'bg-pastelgreen-500 text-white',
      icon: <Check className="w-3.5 h-3.5" aria-hidden="true" />,
    };
  }
  if (course.is_overdue) {
    return {
      bgClass: 'bg-red-500 text-white',
      icon: <Clock className="w-3.5 h-3.5" aria-hidden="true" />,
    };
  }
  if (course.started_at) {
    return {
      bgClass: 'bg-azure-500 text-white animate-pulse',
      icon: <Play className="w-3 h-3" aria-hidden="true" />,
    };
  }
  return {
    bgClass: 'bg-neutral-300',
    icon: null,
  };
}
