import type { useTranslations } from 'next-intl';

export interface TalentCtaProps {
  talentId: string;
  isCompany: boolean;
  isAuthenticated: boolean;
  t: ReturnType<typeof useTranslations>;
}
