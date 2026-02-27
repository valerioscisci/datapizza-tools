import type { useTranslations } from 'next-intl';

export interface BioSectionProps {
  bio: string | null;
  t: ReturnType<typeof useTranslations>;
}
