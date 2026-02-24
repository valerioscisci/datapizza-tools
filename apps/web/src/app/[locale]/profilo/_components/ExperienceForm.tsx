'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import { useTranslations } from 'next-intl';
import {
  Experience,
  ExperienceFormData,
  EMPLOYMENT_TYPES,
  MONTHS,
  YEARS,
} from '../_utils/constants';

interface ExperienceFormProps {
  experience: Experience | null;
  onSave: (data: ExperienceFormData) => void;
  onCancel: () => void;
  saving: boolean;
  t: ReturnType<typeof useTranslations>;
}

export function ExperienceForm({
  experience,
  onSave,
  onCancel,
  saving,
  t,
}: ExperienceFormProps) {
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
