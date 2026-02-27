'use client';

import { useState, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { useSearchParams } from 'next/navigation';
import { Check, Loader2, BarChart3 } from 'lucide-react';
import Link from 'next/link';
import { useProfileData } from '../_hooks/useProfileData';
import { ProfileHeader } from './ProfileHeader';
import { PrivacyToggleSection } from './PrivacyToggleSection';
import { BioSection } from './BioSection';
import { SkillsSection } from './SkillsSection';
import { ExperienceSection } from './ExperienceSection';
import { EducationSection } from './EducationSection';
import { ProfileEditModal } from './ProfileEditModal';
import { AICareerAdvisor } from './AICareerAdvisor';
import { NotificationPreferencesSection } from './NotificationPreferencesSection';

export function ProfiloPage() {
  const t = useTranslations('profile');
  const searchParams = useSearchParams();
  const skillToAdd = searchParams.get('addSkill');
  const [addedSkillToast, setAddedSkillToast] = useState<string | null>(null);
  const {
    user,
    accessToken,
    loading,
    profile,
    fetching,
    showEditModal,
    setShowEditModal,
    saving,
    saveFeedback,
    fetchProfile,
    handleProfileSave,
    handleSkillsUpdate,
    handlePrivacyUpdate,
  } = useProfileData();

  const handleAutoAddComplete = useCallback((skill: string) => {
    setAddedSkillToast(skill);
    setTimeout(() => setAddedSkillToast(null), 3000);
  }, []);

  if (loading || !user || !accessToken) return null;

  if (fetching) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex items-center gap-2 text-neutral-500">
          <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
          <span>{t('loading')}</span>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-neutral-500">{t('error')}</p>
      </div>
    );
  }

  return (
    <>
      {/* Skill auto-added toast */}
      {addedSkillToast && (
        <div className="fixed top-20 right-4 z-50 animate-in fade-in slide-in-from-right-5">
          <div className="px-4 py-2 rounded-lg text-sm font-medium shadow-lg bg-pastelgreen-100 text-pastelgreen-600 border border-pastelgreen-500/30">
            <span className="flex items-center gap-1">
              <Check className="w-4 h-4" aria-hidden="true" /> {t('skillAdded', { skill: addedSkillToast })}
            </span>
          </div>
        </div>
      )}

      {/* Save feedback toast */}
      {saveFeedback && (
        <div className="fixed top-20 right-4 z-50 animate-in fade-in slide-in-from-right-5">
          <div
            className={`px-4 py-2 rounded-lg text-sm font-medium shadow-lg ${
              saveFeedback === 'saved'
                ? 'bg-pastelgreen-100 text-pastelgreen-600 border border-pastelgreen-500/30'
                : 'bg-red-50 text-red-600 border border-red-200'
            }`}
          >
            {saveFeedback === 'saved' ? (
              <span className="flex items-center gap-1">
                <Check className="w-4 h-4" aria-hidden="true" /> {t('saved')}
              </span>
            ) : (
              t('error')
            )}
          </div>
        </div>
      )}

      {/* Hero / Header */}
      <ProfileHeader profile={profile} onEdit={() => setShowEditModal(true)} t={t} />

      {/* Profile Content */}
      <section className="py-8 sm:py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          {/* Privacy Toggle */}
          <PrivacyToggleSection
            isPublic={profile.is_public}
            accessToken={accessToken}
            onUpdate={handlePrivacyUpdate}
            t={t}
          />

          {/* Bio */}
          <BioSection bio={profile.bio} t={t} />

          {/* Skills */}
          <SkillsSection
            skills={profile.skills}
            onUpdate={handleSkillsUpdate}
            accessToken={accessToken}
            t={t}
            skillToAdd={skillToAdd}
            onAutoAddComplete={handleAutoAddComplete}
          />

          {/* Experience */}
          <ExperienceSection
            experiences={profile.experiences}
            accessToken={accessToken}
            onUpdate={fetchProfile}
            t={t}
          />

          {/* Education */}
          <EducationSection
            educations={profile.educations}
            accessToken={accessToken}
            onUpdate={fetchProfile}
            t={t}
          />

          {/* AI Career Advisor */}
          <AICareerAdvisor profile={profile} />

          {/* Skill Gap Analyzer CTA */}
          <div className="border border-azure-200 rounded-lg bg-azure-50 p-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <BarChart3 className="w-5 h-5 text-azure-600" aria-hidden="true" />
              <div>
                <p className="text-sm font-semibold text-azure-700">{t('skillGapCta.title')}</p>
                <p className="text-xs text-azure-600">{t('skillGapCta.subtitle')}</p>
              </div>
            </div>
            <Link href="/it/skill-gap" className="text-sm font-medium text-azure-600 hover:text-azure-700">
              {t('skillGapCta.goTo')} &rarr;
            </Link>
          </div>

          {/* Notification Preferences */}
          <NotificationPreferencesSection />
        </div>
      </section>

      {/* Edit Profile Modal */}
      {showEditModal && (
        <ProfileEditModal
          profile={profile}
          onClose={() => setShowEditModal(false)}
          onSave={handleProfileSave}
          saving={saving}
          t={t}
        />
      )}
    </>
  );
}
