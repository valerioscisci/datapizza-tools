'use client';

import { useTranslations } from 'next-intl';
import { useAuth } from '@/lib/auth/use-auth';
import { useRouter } from 'next/navigation';
import { useEffect, useState, useCallback } from 'react';
import {
  User,
  Briefcase,
  GraduationCap,
  MapPin,
  Linkedin,
  Github,
  Globe,
  Plus,
  Pencil,
  Trash2,
  X,
  Check,
  Loader2,
} from 'lucide-react';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

// --- Types ---

interface Experience {
  id: string;
  title: string;
  company: string;
  employment_type: string | null;
  location: string | null;
  start_month: number | null;
  start_year: number;
  end_month: number | null;
  end_year: number | null;
  is_current: boolean;
  description: string | null;
  created_at: string;
}

interface Education {
  id: string;
  institution: string;
  degree: string | null;
  degree_type: string | null;
  field_of_study: string | null;
  start_year: number;
  end_year: number | null;
  is_current: boolean;
  description: string | null;
  created_at: string;
}

interface ProfileResponse {
  id: string;
  email: string;
  full_name: string;
  phone: string | null;
  bio: string | null;
  location: string | null;
  experience_level: string | null;
  experience_years: string | null;
  current_role: string | null;
  skills: string[];
  availability_status: string;
  reskilling_status: string | null;
  adopted_by_company: string | null;
  linkedin_url: string | null;
  github_url: string | null;
  portfolio_url: string | null;
  experiences: Experience[];
  educations: Education[];
  created_at: string;
}

interface ExperienceFormData {
  title: string;
  company: string;
  employment_type: string;
  location: string;
  start_month: string;
  start_year: string;
  end_month: string;
  end_year: string;
  is_current: boolean;
  description: string;
}

interface EducationFormData {
  institution: string;
  degree: string;
  degree_type: string;
  field_of_study: string;
  start_year: string;
  end_year: string;
  is_current: boolean;
  description: string;
}

// --- Helpers ---

function formatMonthYear(month: number | null, year: number): string {
  if (month) {
    const monthName = new Date(year, month - 1).toLocaleDateString('it-IT', { month: 'long' });
    return `${monthName.charAt(0).toUpperCase() + monthName.slice(1)} ${year}`;
  }
  return `${year}`;
}

function availabilityBadgeStyle(status: string): string {
  switch (status) {
    case 'available':
      return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
    case 'employed':
      return 'bg-azure-50 text-azure-700 border-azure-300/30';
    case 'reskilling':
      return 'bg-yellow-50 text-yellow-500 border-yellow-400/30';
    default:
      return 'bg-neutral-100 text-neutral-600 border-neutral-200';
  }
}

const EMPLOYMENT_TYPES = ['full-time', 'part-time', 'contract', 'freelance'] as const;
const DEGREE_TYPES = ['diploma', 'bachelor', 'master', 'phd', 'certificate'] as const;
const EXPERIENCE_LEVELS = ['junior', 'mid', 'senior'] as const;
const AVAILABILITY_OPTIONS = ['available', 'employed', 'reskilling'] as const;

const MONTHS = Array.from({ length: 12 }, (_, i) => {
  const name = new Date(2024, i).toLocaleDateString('it-IT', { month: 'long' });
  return { value: String(i + 1), label: name.charAt(0).toUpperCase() + name.slice(1) };
});

const currentYear = new Date().getFullYear();
const YEARS = Array.from({ length: 50 }, (_, i) => String(currentYear - i));

// --- Inline Components ---

function ProfileHeader({
  profile,
  onEdit,
  t,
}: {
  profile: ProfileResponse;
  onEdit: () => void;
  t: ReturnType<typeof useTranslations>;
}) {
  return (
    <section className="bg-linear-to-b from-azure-25 to-white py-16 sm:py-20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center">
          {/* Avatar */}
          <div className="w-24 h-24 bg-azure-100 rounded-full flex items-center justify-center text-3xl font-heading font-semibold text-azure-700 mb-4 border-4 border-white shadow-lg">
            {profile.full_name.charAt(0).toUpperCase()}
          </div>

          {/* Name */}
          <h1 className="text-3xl sm:text-4xl font-heading font-semibold text-black-950">
            {profile.full_name}
          </h1>

          {/* Role | Location */}
          <div className="flex items-center gap-2 mt-2 text-neutral-600 text-base">
            {profile.current_role && (
              <span className="flex items-center gap-1">
                <Briefcase className="w-4 h-4" aria-hidden="true" />
                {profile.current_role}
              </span>
            )}
            {profile.current_role && profile.location && (
              <span className="text-neutral-300">|</span>
            )}
            {profile.location && (
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4" aria-hidden="true" />
                {profile.location}
              </span>
            )}
          </div>

          {/* Availability badge */}
          <div className="mt-3">
            <span
              className={`inline-flex items-center px-3 py-1 text-sm font-medium rounded-full border ${availabilityBadgeStyle(profile.availability_status)}`}
            >
              {t(`availability_options.${profile.availability_status}` as Parameters<typeof t>[0])}
            </span>
          </div>

          {/* Social links */}
          <div className="flex items-center gap-3 mt-4">
            {profile.linkedin_url && (
              <a
                href={profile.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer"
                aria-label="LinkedIn"
              >
                <Linkedin className="w-5 h-5" />
              </a>
            )}
            {profile.github_url && (
              <a
                href={profile.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
            )}
            {profile.portfolio_url && (
              <a
                href={profile.portfolio_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer"
                aria-label="Portfolio"
              >
                <Globe className="w-5 h-5" />
              </a>
            )}
          </div>

          {/* Edit button */}
          <button
            onClick={onEdit}
            className="mt-4 px-4 py-2 bg-azure-600 text-white rounded-lg hover:bg-azure-700 transition-colors cursor-pointer flex items-center gap-2 text-sm font-medium"
          >
            <Pencil className="w-4 h-4" aria-hidden="true" />
            {t('editProfile')}
          </button>
        </div>
      </div>
    </section>
  );
}

function ProfileEditModal({
  profile,
  onClose,
  onSave,
  saving,
  t,
}: {
  profile: ProfileResponse;
  onClose: () => void;
  onSave: (data: Partial<ProfileResponse>) => void;
  saving: boolean;
  t: ReturnType<typeof useTranslations>;
}) {
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

function SkillsSection({
  skills,
  onUpdate,
  accessToken,
  t,
}: {
  skills: string[];
  onUpdate: (skills: string[]) => void;
  accessToken: string;
  t: ReturnType<typeof useTranslations>;
}) {
  const [editing, setEditing] = useState(false);
  const [newSkill, setNewSkill] = useState('');
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState<'saved' | 'error' | null>(null);

  const saveSkills = useCallback(
    async (updatedSkills: string[]) => {
      setSaving(true);
      setFeedback(null);
      try {
        const res = await fetch(`${API_BASE}/api/v1/profile`, {
          method: 'PATCH',
          headers: {
            Authorization: `Bearer ${accessToken}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ skills: updatedSkills }),
        });
        if (!res.ok) throw new Error('Failed to save');
        onUpdate(updatedSkills);
        setFeedback('saved');
        setTimeout(() => setFeedback(null), 2000);
      } catch {
        setFeedback('error');
        setTimeout(() => setFeedback(null), 3000);
      } finally {
        setSaving(false);
      }
    },
    [accessToken, onUpdate],
  );

  const addSkill = () => {
    const trimmed = newSkill.trim();
    if (trimmed && !skills.includes(trimmed)) {
      const updated = [...skills, trimmed];
      setNewSkill('');
      saveSkills(updated);
    }
  };

  const removeSkill = (skill: string) => {
    const updated = skills.filter((s) => s !== skill);
    saveSkills(updated);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addSkill();
    }
  };

  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-heading font-semibold text-black-950">{t('skills')}</h2>
        <div className="flex items-center gap-2">
          {feedback === 'saved' && (
            <span className="text-xs text-pastelgreen-600 flex items-center gap-1">
              <Check className="w-3.5 h-3.5" aria-hidden="true" /> {t('saved')}
            </span>
          )}
          {feedback === 'error' && (
            <span className="text-xs text-red-500">{t('error')}</span>
          )}
          {saving && <Loader2 className="w-4 h-4 animate-spin text-azure-600" aria-hidden="true" />}
          <button
            onClick={() => setEditing(!editing)}
            className="p-1.5 text-neutral-400 hover:text-azure-600 transition-colors cursor-pointer"
            aria-label={editing ? t('cancel') : t('edit')}
          >
            {editing ? <X className="w-4 h-4" /> : <Pencil className="w-4 h-4" />}
          </button>
        </div>
      </div>

      {/* Skills pills */}
      <div className="flex flex-wrap gap-2" aria-live="polite">
        {skills.length === 0 && !editing && (
          <p className="text-sm text-neutral-400">{t('noSkills')}</p>
        )}
        {skills.map((skill) => (
          <span
            key={skill}
            className="inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full border bg-azure-50 text-azure-700 border-azure-300/30 gap-1"
          >
            {skill}
            {editing && (
              <button
                onClick={() => removeSkill(skill)}
                className="ml-0.5 text-azure-400 hover:text-red-500 transition-colors cursor-pointer"
                aria-label={`${t('delete')} ${skill}`}
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </span>
        ))}
      </div>

      {/* Add skill input */}
      {editing && (
        <div className="flex items-center gap-2 mt-3">
          <input
            type="text"
            value={newSkill}
            onChange={(e) => setNewSkill(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 px-4 py-2.5 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-azure-500 focus:border-azure-500"
            placeholder={t('skillPlaceholder')}
          />
          <button
            onClick={addSkill}
            disabled={!newSkill.trim()}
            className="px-3 py-2.5 bg-azure-600 text-white rounded-lg hover:bg-azure-700 transition-colors cursor-pointer text-sm disabled:opacity-40"
            aria-label={t('addSkill')}
          >
            <Plus className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}

function ExperienceForm({
  experience,
  onSave,
  onCancel,
  saving,
  t,
}: {
  experience: Experience | null;
  onSave: (data: ExperienceFormData) => void;
  onCancel: () => void;
  saving: boolean;
  t: ReturnType<typeof useTranslations>;
}) {
  const [formData, setFormData] = useState<ExperienceFormData>({
    title: experience?.title || '',
    company: experience?.company || '',
    employment_type: experience?.employment_type || '',
    location: experience?.location || '',
    start_month: experience?.start_month ? String(experience.start_month) : '',
    start_year: experience?.start_year ? String(experience.start_year) : '',
    end_month: experience?.end_month ? String(experience.end_month) : '',
    end_year: experience?.end_year ? String(experience.end_year) : '',
    is_current: experience?.is_current || false,
    description: experience?.description || '',
  });

  const handleChange = (field: keyof ExperienceFormData, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  const inputClass =
    'w-full px-4 py-2.5 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-azure-500 focus:border-azure-500';
  const labelClass = 'block text-sm font-medium text-neutral-700 mb-1';

  return (
    <form
      onSubmit={handleSubmit}
      className="p-4 bg-neutral-50 rounded-xl border border-neutral-200 space-y-3"
    >
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>{t('fields.title')}</label>
          <input
            type="text"
            value={formData.title}
            onChange={(e) => handleChange('title', e.target.value)}
            className={inputClass}
            required
          />
        </div>
        <div>
          <label className={labelClass}>{t('fields.company')}</label>
          <input
            type="text"
            value={formData.company}
            onChange={(e) => handleChange('company', e.target.value)}
            className={inputClass}
            required
          />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>{t('fields.employmentType')}</label>
          <select
            value={formData.employment_type}
            onChange={(e) => handleChange('employment_type', e.target.value)}
            className={`${inputClass} cursor-pointer`}
          >
            <option value="">-</option>
            {EMPLOYMENT_TYPES.map((type) => (
              <option key={type} value={type}>
                {t(`employment_types.${type}` as Parameters<typeof t>[0])}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>{t('fields.location')}</label>
          <input
            type="text"
            value={formData.location}
            onChange={(e) => handleChange('location', e.target.value)}
            className={inputClass}
          />
        </div>
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <div>
          <label className={labelClass}>{t('fields.startMonth')}</label>
          <select
            value={formData.start_month}
            onChange={(e) => handleChange('start_month', e.target.value)}
            className={`${inputClass} cursor-pointer`}
          >
            <option value="">-</option>
            {MONTHS.map((m) => (
              <option key={m.value} value={m.value}>
                {m.label}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>{t('fields.startYear')}</label>
          <select
            value={formData.start_year}
            onChange={(e) => handleChange('start_year', e.target.value)}
            className={`${inputClass} cursor-pointer`}
            required
          >
            <option value="">-</option>
            {YEARS.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </div>
        {!formData.is_current && (
          <>
            <div>
              <label className={labelClass}>{t('fields.endMonth')}</label>
              <select
                value={formData.end_month}
                onChange={(e) => handleChange('end_month', e.target.value)}
                className={`${inputClass} cursor-pointer`}
              >
                <option value="">-</option>
                {MONTHS.map((m) => (
                  <option key={m.value} value={m.value}>
                    {m.label}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label className={labelClass}>{t('fields.endYear')}</label>
              <select
                value={formData.end_year}
                onChange={(e) => handleChange('end_year', e.target.value)}
                className={`${inputClass} cursor-pointer`}
              >
                <option value="">-</option>
                {YEARS.map((y) => (
                  <option key={y} value={y}>
                    {y}
                  </option>
                ))}
              </select>
            </div>
          </>
        )}
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="is_current_exp"
          checked={formData.is_current}
          onChange={(e) => handleChange('is_current', e.target.checked)}
          className="w-4 h-4 text-azure-600 border-neutral-300 rounded focus:ring-azure-500 cursor-pointer"
        />
        <label htmlFor="is_current_exp" className="text-sm text-neutral-700 cursor-pointer">
          {t('current')}
        </label>
      </div>

      <div>
        <label className={labelClass}>{t('fields.description')}</label>
        <textarea
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          className={`${inputClass} min-h-[80px] resize-y`}
        />
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <button
          type="button"
          onClick={onCancel}
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
  );
}

function ExperienceSection({
  experiences,
  accessToken,
  onUpdate,
  t,
}: {
  experiences: Experience[];
  accessToken: string;
  onUpdate: () => void;
  t: ReturnType<typeof useTranslations>;
}) {
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<'error' | null>(null);

  const handleSave = async (data: ExperienceFormData, existingId?: string) => {
    setSaving(true);
    setFeedback(null);
    try {
      const payload = {
        title: data.title,
        company: data.company,
        employment_type: data.employment_type || null,
        location: data.location || null,
        start_month: data.start_month ? Number(data.start_month) : null,
        start_year: Number(data.start_year),
        end_month: data.is_current ? null : data.end_month ? Number(data.end_month) : null,
        end_year: data.is_current ? null : data.end_year ? Number(data.end_year) : null,
        is_current: data.is_current,
        description: data.description || null,
      };

      const url = existingId
        ? `${API_BASE}/api/v1/profile/experiences/${existingId}`
        : `${API_BASE}/api/v1/profile/experiences`;
      const method = existingId ? 'PATCH' : 'POST';

      const res = await fetch(url, {
        method,
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error('Failed to save');
      setShowForm(false);
      setEditingId(null);
      onUpdate();
    } catch {
      setFeedback('error');
      setTimeout(() => setFeedback(null), 3000);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(t('confirmDelete'))) return;
    setDeletingId(id);
    setFeedback(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/profile/experiences/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error('Failed to delete');
      onUpdate();
    } catch {
      setFeedback('error');
      setTimeout(() => setFeedback(null), 3000);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-xl font-heading font-semibold text-black-950 flex items-center gap-2">
            <Briefcase className="w-5 h-5 text-azure-600" aria-hidden="true" />
            {t('experience')}
          </h2>
          {feedback === 'error' && (
            <span className="text-xs text-red-500">{t('error')}</span>
          )}
        </div>
        {!showForm && !editingId && (
          <button
            onClick={() => setShowForm(true)}
            className="p-1.5 text-azure-600 hover:bg-azure-50 rounded-lg transition-colors cursor-pointer"
            aria-label={t('addExperience')}
          >
            <Plus className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Add form */}
      {showForm && (
        <div className="mb-4">
          <ExperienceForm
            experience={null}
            onSave={(data) => handleSave(data)}
            onCancel={() => setShowForm(false)}
            saving={saving}
            t={t}
          />
        </div>
      )}

      {/* Experience list */}
      <div className="space-y-4" aria-live="polite">
        {experiences.length === 0 && !showForm && (
          <p className="text-sm text-neutral-400">{t('noExperience')}</p>
        )}
        {experiences.map((exp) =>
          editingId === exp.id ? (
            <ExperienceForm
              key={exp.id}
              experience={exp}
              onSave={(data) => handleSave(data, exp.id)}
              onCancel={() => setEditingId(null)}
              saving={saving}
              t={t}
            />
          ) : (
            <div
              key={exp.id}
              className="p-4 bg-neutral-50 rounded-xl border border-neutral-100 hover:border-azure-200 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-base font-semibold text-black-950">
                    {exp.company}{' '}
                    <span className="font-normal text-neutral-500">&middot;</span>{' '}
                    {exp.title}
                  </h3>
                  <div className="flex flex-wrap items-center gap-2 mt-1 text-sm text-neutral-500">
                    {exp.employment_type && (
                      <span>{t(`employment_types.${exp.employment_type}` as Parameters<typeof t>[0])}</span>
                    )}
                    {exp.employment_type && exp.location && (
                      <span className="text-neutral-300">&middot;</span>
                    )}
                    {exp.location && (
                      <span className="flex items-center gap-1">
                        <MapPin className="w-3.5 h-3.5" aria-hidden="true" />
                        {exp.location}
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-neutral-400 mt-1">
                    {formatMonthYear(exp.start_month, exp.start_year)} -{' '}
                    {exp.is_current
                      ? t('present')
                      : exp.end_year
                        ? formatMonthYear(exp.end_month, exp.end_year)
                        : ''}
                  </p>
                  {exp.description && (
                    <p className="text-sm text-neutral-600 mt-2 whitespace-pre-line">
                      {exp.description}
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-1 ml-2 shrink-0">
                  <button
                    onClick={() => setEditingId(exp.id)}
                    className="p-1.5 text-neutral-400 hover:text-azure-600 transition-colors cursor-pointer"
                    aria-label={`${t('edit')} ${exp.title}`}
                  >
                    <Pencil className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(exp.id)}
                    disabled={deletingId === exp.id}
                    className="p-1.5 text-neutral-400 hover:text-red-500 transition-colors cursor-pointer disabled:opacity-40"
                    aria-label={`${t('delete')} ${exp.title}`}
                  >
                    {deletingId === exp.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          ),
        )}
      </div>
    </div>
  );
}

function EducationForm({
  education,
  onSave,
  onCancel,
  saving,
  t,
}: {
  education: Education | null;
  onSave: (data: EducationFormData) => void;
  onCancel: () => void;
  saving: boolean;
  t: ReturnType<typeof useTranslations>;
}) {
  const [formData, setFormData] = useState<EducationFormData>({
    institution: education?.institution || '',
    degree: education?.degree || '',
    degree_type: education?.degree_type || '',
    field_of_study: education?.field_of_study || '',
    start_year: education?.start_year ? String(education.start_year) : '',
    end_year: education?.end_year ? String(education.end_year) : '',
    is_current: education?.is_current || false,
    description: education?.description || '',
  });

  const handleChange = (field: keyof EducationFormData, value: string | boolean) => {
    setFormData((prev) => ({ ...prev, [field]: value }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave(formData);
  };

  const inputClass =
    'w-full px-4 py-2.5 border border-neutral-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-azure-500 focus:border-azure-500';
  const labelClass = 'block text-sm font-medium text-neutral-700 mb-1';

  return (
    <form
      onSubmit={handleSubmit}
      className="p-4 bg-neutral-50 rounded-xl border border-neutral-200 space-y-3"
    >
      <div>
        <label className={labelClass}>{t('fields.institution')}</label>
        <input
          type="text"
          value={formData.institution}
          onChange={(e) => handleChange('institution', e.target.value)}
          className={inputClass}
          required
        />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>{t('fields.degreeType')}</label>
          <select
            value={formData.degree_type}
            onChange={(e) => handleChange('degree_type', e.target.value)}
            className={`${inputClass} cursor-pointer`}
          >
            <option value="">-</option>
            {DEGREE_TYPES.map((type) => (
              <option key={type} value={type}>
                {t(`degree_types.${type}` as Parameters<typeof t>[0])}
              </option>
            ))}
          </select>
        </div>
        <div>
          <label className={labelClass}>{t('fields.degree')}</label>
          <input
            type="text"
            value={formData.degree}
            onChange={(e) => handleChange('degree', e.target.value)}
            className={inputClass}
          />
        </div>
      </div>

      <div>
        <label className={labelClass}>{t('fields.fieldOfStudy')}</label>
        <input
          type="text"
          value={formData.field_of_study}
          onChange={(e) => handleChange('field_of_study', e.target.value)}
          className={inputClass}
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div>
          <label className={labelClass}>{t('fields.startYear')}</label>
          <select
            value={formData.start_year}
            onChange={(e) => handleChange('start_year', e.target.value)}
            className={`${inputClass} cursor-pointer`}
            required
          >
            <option value="">-</option>
            {YEARS.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </div>
        {!formData.is_current && (
          <div>
            <label className={labelClass}>{t('fields.endYear')}</label>
            <select
              value={formData.end_year}
              onChange={(e) => handleChange('end_year', e.target.value)}
              className={`${inputClass} cursor-pointer`}
            >
              <option value="">-</option>
              {YEARS.map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className="flex items-center gap-2">
        <input
          type="checkbox"
          id="is_current_edu"
          checked={formData.is_current}
          onChange={(e) => handleChange('is_current', e.target.checked)}
          className="w-4 h-4 text-azure-600 border-neutral-300 rounded focus:ring-azure-500 cursor-pointer"
        />
        <label htmlFor="is_current_edu" className="text-sm text-neutral-700 cursor-pointer">
          {t('current')}
        </label>
      </div>

      <div>
        <label className={labelClass}>{t('fields.description')}</label>
        <textarea
          value={formData.description}
          onChange={(e) => handleChange('description', e.target.value)}
          className={`${inputClass} min-h-[80px] resize-y`}
        />
      </div>

      <div className="flex justify-end gap-2 pt-2">
        <button
          type="button"
          onClick={onCancel}
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
  );
}

function EducationSection({
  educations,
  accessToken,
  onUpdate,
  t,
}: {
  educations: Education[];
  accessToken: string;
  onUpdate: () => void;
  t: ReturnType<typeof useTranslations>;
}) {
  const [showForm, setShowForm] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);
  const [deletingId, setDeletingId] = useState<string | null>(null);
  const [feedback, setFeedback] = useState<'error' | null>(null);

  const handleSave = async (data: EducationFormData, existingId?: string) => {
    setSaving(true);
    setFeedback(null);
    try {
      const payload = {
        institution: data.institution,
        degree: data.degree || null,
        degree_type: data.degree_type || null,
        field_of_study: data.field_of_study || null,
        start_year: Number(data.start_year),
        end_year: data.is_current ? null : data.end_year ? Number(data.end_year) : null,
        is_current: data.is_current,
        description: data.description || null,
      };

      const url = existingId
        ? `${API_BASE}/api/v1/profile/educations/${existingId}`
        : `${API_BASE}/api/v1/profile/educations`;
      const method = existingId ? 'PATCH' : 'POST';

      const res = await fetch(url, {
        method,
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error('Failed to save');
      setShowForm(false);
      setEditingId(null);
      onUpdate();
    } catch {
      setFeedback('error');
      setTimeout(() => setFeedback(null), 3000);
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm(t('confirmDelete'))) return;
    setDeletingId(id);
    setFeedback(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/profile/educations/${id}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) throw new Error('Failed to delete');
      onUpdate();
    } catch {
      setFeedback('error');
      setTimeout(() => setFeedback(null), 3000);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h2 className="text-xl font-heading font-semibold text-black-950 flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-azure-600" aria-hidden="true" />
            {t('education')}
          </h2>
          {feedback === 'error' && (
            <span className="text-xs text-red-500">{t('error')}</span>
          )}
        </div>
        {!showForm && !editingId && (
          <button
            onClick={() => setShowForm(true)}
            className="p-1.5 text-azure-600 hover:bg-azure-50 rounded-lg transition-colors cursor-pointer"
            aria-label={t('addEducation')}
          >
            <Plus className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Add form */}
      {showForm && (
        <div className="mb-4">
          <EducationForm
            education={null}
            onSave={(data) => handleSave(data)}
            onCancel={() => setShowForm(false)}
            saving={saving}
            t={t}
          />
        </div>
      )}

      {/* Education list */}
      <div className="space-y-4" aria-live="polite">
        {educations.length === 0 && !showForm && (
          <p className="text-sm text-neutral-400">{t('noEducation')}</p>
        )}
        {educations.map((edu) =>
          editingId === edu.id ? (
            <EducationForm
              key={edu.id}
              education={edu}
              onSave={(data) => handleSave(data, edu.id)}
              onCancel={() => setEditingId(null)}
              saving={saving}
              t={t}
            />
          ) : (
            <div
              key={edu.id}
              className="p-4 bg-neutral-50 rounded-xl border border-neutral-100 hover:border-azure-200 transition-colors"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <h3 className="text-base font-semibold text-black-950">
                    {edu.institution}
                  </h3>
                  <div className="flex flex-wrap items-center gap-1 mt-1 text-sm text-neutral-500">
                    {edu.degree_type && (
                      <span>{t(`degree_types.${edu.degree_type}` as Parameters<typeof t>[0])}</span>
                    )}
                    {edu.degree_type && (edu.degree || edu.field_of_study) && (
                      <span className="text-neutral-300">&middot;</span>
                    )}
                    {edu.degree && <span>{edu.degree}</span>}
                    {edu.degree && edu.field_of_study && (
                      <span className="text-neutral-300">-</span>
                    )}
                    {edu.field_of_study && <span>{edu.field_of_study}</span>}
                  </div>
                  <p className="text-sm text-neutral-400 mt-1">
                    {edu.start_year} -{' '}
                    {edu.is_current ? t('present') : edu.end_year || ''}
                  </p>
                  {edu.description && (
                    <p className="text-sm text-neutral-600 mt-2 whitespace-pre-line">
                      {edu.description}
                    </p>
                  )}
                </div>
                <div className="flex items-center gap-1 ml-2 shrink-0">
                  <button
                    onClick={() => setEditingId(edu.id)}
                    className="p-1.5 text-neutral-400 hover:text-azure-600 transition-colors cursor-pointer"
                    aria-label={`${t('edit')} ${edu.institution}`}
                  >
                    <Pencil className="w-4 h-4" />
                  </button>
                  <button
                    onClick={() => handleDelete(edu.id)}
                    disabled={deletingId === edu.id}
                    className="p-1.5 text-neutral-400 hover:text-red-500 transition-colors cursor-pointer disabled:opacity-40"
                    aria-label={`${t('delete')} ${edu.institution}`}
                  >
                    {deletingId === edu.id ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Trash2 className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>
            </div>
          ),
        )}
      </div>
    </div>
  );
}

// --- Main Page Component ---

export default function ProfiloPage() {
  const t = useTranslations('profile');
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
          {/* Bio */}
          <div className="p-6 bg-white rounded-2xl border border-neutral-200">
            <h2 className="text-xl font-heading font-semibold text-black-950 flex items-center gap-2 mb-3">
              <User className="w-5 h-5 text-azure-600" aria-hidden="true" />
              {t('bio')}
            </h2>
            {profile.bio ? (
              <p className="text-sm text-neutral-600 whitespace-pre-line">{profile.bio}</p>
            ) : (
              <p className="text-sm text-neutral-400">{t('noBio')}</p>
            )}
          </div>

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
