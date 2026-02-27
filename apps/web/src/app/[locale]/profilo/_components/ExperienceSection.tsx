'use client';

import { useState } from 'react';
import {
  Briefcase,
  MapPin,
  Plus,
  Pencil,
  Trash2,
  Loader2,
} from 'lucide-react';
import {
  API_BASE,
  ExperienceFormData,
  formatMonthYear,
} from '../_utils/constants';
import { ExperienceForm } from './ExperienceForm';
import { ExperienceSectionProps } from './ExperienceSection.props';

export function ExperienceSection({
  experiences,
  accessToken,
  onUpdate,
  t,
}: ExperienceSectionProps) {
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
