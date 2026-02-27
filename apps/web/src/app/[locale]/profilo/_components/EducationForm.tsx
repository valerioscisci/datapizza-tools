'use client';

import { useState } from 'react';
import { Loader2 } from 'lucide-react';
import {
  EducationFormData,
  DEGREE_TYPES,
  YEARS,
} from '../_utils/constants';
import { EducationFormProps } from './EducationForm.props';

export function EducationForm({
  education,
  onSave,
  onCancel,
  saving,
  t,
}: EducationFormProps) {
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
