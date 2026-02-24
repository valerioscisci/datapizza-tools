'use client';

import { useTranslations } from 'next-intl';
import { Check, Loader2 } from 'lucide-react';
import { useProfileData } from '../_hooks/useProfileData';
import { ProfileHeader } from './ProfileHeader';
import { PrivacyToggleSection } from './PrivacyToggleSection';
import { BioSection } from './BioSection';
import { SkillsSection } from './SkillsSection';
import { ExperienceSection } from './ExperienceSection';
import { EducationSection } from './EducationSection';
import { ProfileEditModal } from './ProfileEditModal';

export function ProfiloPage() {
  const t = useTranslations('profile');
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
