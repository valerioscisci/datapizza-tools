'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/lib/auth/use-auth';
import { API_BASE, ProfileResponse } from '../_utils/constants';

export function useProfileData() {
  const router = useRouter();
  const { user, accessToken, loading } = useAuth();

  const [profile, setProfile] = useState<ProfileResponse | null>(null);
  const [fetching, setFetching] = useState(true);
  const [showEditModal, setShowEditModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [saveFeedback, setSaveFeedback] = useState<'saved' | 'error' | null>(null);

  const fetchProfile = useCallback(async () => {
    if (!accessToken) return;
    setFetching(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/profile`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error('Failed to fetch profile');
      const data: ProfileResponse = await res.json();
      setProfile(data);
    } catch {
      setProfile(null);
    } finally {
      setFetching(false);
    }
  }, [accessToken]);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/it/login');
    }
  }, [user, loading, router]);

  useEffect(() => {
    if (accessToken) {
      fetchProfile();
    }
  }, [accessToken, fetchProfile]);

  const handleProfileSave = async (data: Partial<ProfileResponse>) => {
    if (!accessToken) return;
    setSaving(true);
    setSaveFeedback(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/profile`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to save profile');
      setShowEditModal(false);
      setSaveFeedback('saved');
      setTimeout(() => setSaveFeedback(null), 2000);
      fetchProfile();
    } catch {
      setSaveFeedback('error');
      setTimeout(() => setSaveFeedback(null), 3000);
    } finally {
      setSaving(false);
    }
  };

  const handleSkillsUpdate = useCallback((updatedSkills: string[]) => {
    setProfile((prev) => (prev ? { ...prev, skills: updatedSkills } : prev));
  }, []);

  const handlePrivacyUpdate = useCallback((value: boolean) => {
    setProfile((prev) => (prev ? { ...prev, is_public: value } : prev));
  }, []);

  return {
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
  };
}
