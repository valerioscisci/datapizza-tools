import type { useTranslations } from 'next-intl';
import type { Proposal } from '../_utils/constants';

export interface ProposalCardProps {
  proposal: Proposal;
  onAccept: (id: string) => void;
  onReject: (id: string) => void;
  onMarkCourseComplete: (proposalId: string, courseId: string) => void;
  onStartCourse: (proposalId: string, courseId: string) => void;
  onSaveTalentNotes: (proposalId: string, courseId: string, notes: string) => void;
  t: ReturnType<typeof useTranslations>;
  tStatus: ReturnType<typeof useTranslations>;
  tMilestones: ReturnType<typeof useTranslations>;
  tHire: ReturnType<typeof useTranslations>;
}
