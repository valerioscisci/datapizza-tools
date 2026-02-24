'use client';

import { useState, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { useParams } from 'next/navigation';
import { useAuth } from '@/lib/auth/use-auth';
import Link from 'next/link';
import { ArrowLeft, Loader2, User } from 'lucide-react';
import { API_BASE, TalentDetail } from '../_utils/constants';
import { TalentHero } from './TalentHero';
import { TalentBioAndSkills } from './TalentBioAndSkills';
import { TalentExperience } from './TalentExperience';
import { TalentEducation } from './TalentEducation';
import { TalentCta } from './TalentCta';

export function TalentDetailPage() {
  const t = useTranslations('talents');
  const tProfile = useTranslations('profile');
  const params = useParams();
  const { isAuthenticated, isCompany } = useAuth();
  const talentId = params.id as string;

  const [talent, setTalent] = useState<TalentDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [notFound, setNotFound] = useState(false);

  const fetchTalent = useCallback(async () => {
    setLoading(true);
    setNotFound(false);
    try {
      const res = await fetch(`${API_BASE}/api/v1/talents/${talentId}`);
      if (res.status === 404) {
        setNotFound(true);
        return;
      }
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: TalentDetail = await res.json();
      setTalent(data);
    } catch {
      setNotFound(true);
    } finally {
      setLoading(false);
    }
  }, [talentId]);

  useEffect(() => {
    fetchTalent();
  }, [fetchTalent]);

  // Loading state
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center gap-2 text-neutral-500">
          <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
          <span>{t('loading')}</span>
        </div>
      </div>
    );
  }

  // Not found state
  if (notFound || !talent) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md px-4">
          <User className="w-16 h-16 text-neutral-300 mx-auto mb-4" aria-hidden="true" />
          <h1 className="text-2xl font-heading font-semibold text-black-950 mb-2">
            {t('notFound')}
          </h1>
          <p className="text-neutral-500 mb-6">
            {t('notFoundDescription')}
          </p>
          <Link
            href="/it/talenti"
            className="inline-flex items-center gap-2 px-6 py-3 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer"
          >
            <ArrowLeft className="w-4 h-4" aria-hidden="true" />
            {t('detail.backToList')}
          </Link>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Back link */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        <Link
          href="/it/talenti"
          className="inline-flex items-center gap-1 text-sm text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          {t('detail.backToList')}
        </Link>
      </div>

      {/* Hero / Header */}
      <TalentHero talent={talent} tProfile={tProfile} />

      {/* Content */}
      <section className="py-8 sm:py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          {/* Bio & Skills */}
          <TalentBioAndSkills talent={talent} t={t} />

          {/* Experience */}
          <TalentExperience
            experiences={talent.experiences}
            t={t}
            tProfile={tProfile}
          />

          {/* Education */}
          <TalentEducation
            educations={talent.educations}
            t={t}
            tProfile={tProfile}
          />

          {/* CTA Section */}
          <TalentCta
            talentId={talent.id}
            isCompany={isCompany}
            isAuthenticated={isAuthenticated}
            t={t}
          />
        </div>
      </section>
    </>
  );
}
