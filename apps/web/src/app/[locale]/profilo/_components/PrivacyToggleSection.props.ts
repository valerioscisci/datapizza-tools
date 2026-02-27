import type { useTranslations } from 'next-intl';

export interface PrivacyToggleSectionProps {
  isPublic: boolean;
  accessToken: string;
  onUpdate: (value: boolean) => void;
  t: ReturnType<typeof useTranslations>;
}
