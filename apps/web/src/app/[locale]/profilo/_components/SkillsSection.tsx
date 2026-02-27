'use client';

import { useState, useCallback } from 'react';
import { Plus, Pencil, X, Check, Loader2 } from 'lucide-react';
import { API_BASE } from '../_utils/constants';
import { SkillsSectionProps } from './SkillsSection.props';

export function SkillsSection({
  skills,
  onUpdate,
  accessToken,
  t,
}: SkillsSectionProps) {
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
