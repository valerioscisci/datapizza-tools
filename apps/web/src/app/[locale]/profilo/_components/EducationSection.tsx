'use client';

import { useState } from 'react';
import {
  GraduationCap,
  Plus,
  Pencil,
  Trash2,
  Loader2,
} from 'lucide-react';
import {
  API_BASE,
  EducationFormData,
} from '../_utils/constants';
import { EducationForm } from './EducationForm';
import { EducationSectionProps } from './EducationSection.props';

export function EducationSection({
  educations,
  accessToken,
  onUpdate,
  t,
}: EducationSectionProps) {
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
