import type { useTranslations } from 'next-intl';

export interface SkillsSectionProps {
  skills: string[];
  onUpdate: (skills: string[]) => void;
  accessToken: string;
  t: ReturnType<typeof useTranslations>;
  skillToAdd?: string | null;
  onAutoAddComplete?: (skill: string) => void;
}
