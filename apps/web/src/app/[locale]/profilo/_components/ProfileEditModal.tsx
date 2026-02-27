'use client';

import { useState, useEffect } from 'react';
import { X, Loader2 } from 'lucide-react';
import {
  EXPERIENCE_LEVELS,
  AVAILABILITY_OPTIONS,
} from '../_utils/constants';
import { ProfileEditModalProps } from './ProfileEditModal.props';

export function ProfileEditModal({
  profile,
  onClose,
  onSave,
  saving,
  t,
}: ProfileEditModalProps) {
  const [formData, setFormData] = useState({
    full_name: profile.full_name,
    phone: profile.phone || '',
    bio: profile.bio || '',
    location: profile.location || '',
    current_role: profile.current_role || '',
    experience_level: profile.experience_level || '',
    experience_years: profile.experience_years || '',
    availability_status: profile.availability_status,
    linkedin_url: profile.linkedin_url || '',
    github_url: profile.github_url || '',
    portfolio_url: profile.portfolio_url || '',
  });

  const handleChange = (field: keyof typeof formData, value: string) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      full_name: formData.full_name,
      phone: formData.phone || null,
      bio: formData.bio || null,
      location: formData.location || null,
      current_role: formData.current_role || null,
      experience_level: formData.experience_level || null,
      experience_years: formData.experience_years || null,
      availability_status: formData.availability_status,
      linkedin_url: formData.linkedin_url || null,
      github_url: formData.github_url || null,
      portfolio_url: formData.portfolio_url || null,
    });
  };

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    document.addEventListener('keydown', handleEscape);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = '';
    };
  }, [onClose]);

  const inputClass =
    'w-full px-4 py-2.5 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-azure-500 focus:border-azure-500';
  const labelClass = 'block text-sm font-medium text-neutral-700 mb-1';

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={(e) => {
        if (e.target === e.currentTarget) onClose();
      }}
      role="dialog"
      aria-modal="true"
      aria-labelledby="edit-profile-title"
    >
      <div className="bg-white rounded-2xl shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b border-neutral-100">
          <h2 id="edit-profile-title" className="text-xl font-heading font-semibold text-black-950">
            {t('editProfile')}
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-neutral-400 hover:text-neutral-600 transition-colors cursor-pointer"
            aria-label={t('cancel')}
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          {/* Full Name */}
          <div>
            <label className={labelClass}>{t('fields.fullName')}</label>
            <input
              type="text"
              value={formData.full_name}
              onChange={(e) => handleChange('full_name', e.target.value)}
              className={inputClass}
              required
            />
          </div>

          {/* Phone */}
          <div>
            <label className={labelClass}>{t('fields.phone')}</label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => handleChange('phone', e.target.value)}
              className={inputClass}
            />
          </div>

          {/* Bio */}
          <div>
            <label className={labelClass}>{t('bio')}</label>
            <textarea
              value={formData.bio}
              onChange={(e) => handleChange('bio', e.target.value)}
              className={`${inputClass} min-h-[100px] resize-y`}
              placeholder={t('bioPlaceholder')}
            />
          </div>

          {/* Location */}
          <div>
            <label className={labelClass}>{t('fields.location')}</label>
            <input
              type="text"
              value={formData.location}
              onChange={(e) => handleChange('location', e.target.value)}
              className={inputClass}
            />
          </div>

          {/* Current Role */}
          <div>
            <label className={labelClass}>{t('fields.currentRole')}</label>
            <input
              type="text"
              value={formData.current_role}
              onChange={(e) => handleChange('current_role', e.target.value)}
              className={inputClass}
            />
          </div>

          {/* Experience Level + Years (side by side) */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className={labelClass}>{t('fields.experienceLevel')}</label>
              <select
                value={formData.experience_level}
                onChange={(e) => handleChange('experience_level', e.target.value)}
                className={`${inputClass} cursor-pointer`}
              >
                <option value="">-</option>
                {EXPERIENCE_LEVELS.map((level) => (
                  <option key={level} value={level}>
                    {t(`experience_levels.${level}` as Parameters<typeof t>[0])}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>{t('fields.experienceYears')}</label>
              <input
                type="text"
                value={formData.experience_years}
                onChange={(e) => handleChange('experience_years', e.target.value)}
                className={inputClass}
                placeholder={t('experienceYearsPlaceholder')}
              />
            </div>
          </div>

          {/* Availability */}
          <div>
            <label className={labelClass}>{t('fields.availability')}</label>
            <select
              value={formData.availability_status}
              onChange={(e) => handleChange('availability_status', e.target.value)}
              className={`${inputClass} cursor-pointer`}
            >
              {AVAILABILITY_OPTIONS.map((opt) => (
                <option key={opt} value={opt}>
                  {t(`availability_options.${opt}` as Parameters<typeof t>[0])}
                </option>
              ))}
            </select>
          </div>

          {/* Social URLs */}
          <div>
            <label className={labelClass}>{t('fields.linkedin')}</label>
            <input
              type="url"
              value={formData.linkedin_url}
              onChange={(e) => handleChange('linkedin_url', e.target.value)}
              className={inputClass}
              placeholder="https://linkedin.com/in/..."
            />
          </div>
          <div>
            <label className={labelClass}>{t('fields.github')}</label>
            <input
              type="url"
              value={formData.github_url}
              onChange={(e) => handleChange('github_url', e.target.value)}
              className={inputClass}
              placeholder="https://github.com/..."
            />
          </div>
          <div>
            <label className={labelClass}>{t('fields.portfolio')}</label>
            <input
              type="url"
              value={formData.portfolio_url}
              onChange={(e) => handleChange('portfolio_url', e.target.value)}
              className={inputClass}
              placeholder="https://..."
            />
          </div>

          {/* Actions */}
          <div className="flex justify-end gap-3 pt-4 border-t border-neutral-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 bg-white text-neutral-700 border border-neutral-200 rounded-lg hover:border-azure-300 hover:text-azure-600 transition-colors cursor-pointer text-sm font-medium"
            >
              {t('cancel')}
            </button>
            <button
              type="submit"
              disabled={saving}
              className="px-4 py-2 bg-azure-600 text-white rounded-lg hover:bg-azure-700 transition-colors cursor-pointer text-sm font-medium flex items-center gap-2 disabled:opacity-60"
            >
              {saving && <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />}
              {saving ? t('saving') : t('saveProfile')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
