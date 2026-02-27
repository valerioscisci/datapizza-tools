import type { useTranslations } from 'next-intl';
import type { Proposal } from '../_utils/constants';

export interface CompanyProposalCardProps {
  proposal: Proposal;
  onSaveCompanyUpdate: (proposalId: string, courseId: string, companyNotes: string, deadline: string | null) => void;
  onHire: (proposal: Proposal) => void;
  t: ReturnType<typeof useTranslations>;
  tStatus: ReturnType<typeof useTranslations>;
  tMilestones: ReturnType<typeof useTranslations>;
  tHire: ReturnType<typeof useTranslations>;
}
