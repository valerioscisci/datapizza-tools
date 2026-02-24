'use client';

import { useState } from 'react';
import { Eye, Info } from 'lucide-react';
import { useTranslations } from 'next-intl';
import { API_BASE, ProfileResponse } from '../_utils/constants';

interface PrivacyToggleSectionProps {
  isPublic: boolean;
  accessToken: string;
  onUpdate: (value: boolean) => void;
  t: ReturnType<typeof useTranslations>;
}

export function PrivacyToggleSection({
  isPublic,
  accessToken,
  onUpdate,
  t,
}: PrivacyToggleSectionProps) {
  const [toggling, setToggling] = useState(false);
  const [feedback, setFeedback] = useState<'error' | null>(null);

  const handleToggle = async () => {
    setToggling(true);
    setFeedback(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/profile`, {
        method: 'PATCH',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ is_public: !isPublic }),
      });
      if (!res.ok) throw new Error('Failed to toggle');
      const data: ProfileResponse = await res.json();
      onUpdate(data.is_public);
    } catch {
      setFeedback('error');
      setTimeout(() => setFeedback(null), 3000);
    } finally {
      setToggling(false);
    }
  };

  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200">
      <div className="flex items-center justify-between">
        <div className="flex items-start gap-3 flex-1 min-w-0">
          <Eye className="w-5 h-5 text-azure-600 mt-0.5 shrink-0" aria-hidden="true" />
          <div>
            <h2 className="text-lg font-heading font-semibold text-black-950">
              {t('privacyToggle.title')}
            </h2>
            <p className="text-sm text-neutral-500 mt-0.5">
              {t('privacyToggle.description')}
            </p>
            {feedback === 'error' && (
              <span className="text-xs text-red-500 mt-1 block">{t('error')}</span>
            )}
          </div>
        </div>

        {/* Toggle switch */}
        <button
          role="switch"
          aria-checked={isPublic}
          aria-label={t('privacyToggle.title')}
          onClick={handleToggle}
          disabled={toggling}
          className={`relative inline-flex h-7 w-12 items-center rounded-full transition-colors duration-300 ease-in-out cursor-pointer shrink-0 ml-4 disabled:opacity-60 ${
            isPublic ? 'bg-pastelgreen-500' : 'bg-neutral-300'
          }`}
        >
          <span
            className={`inline-block h-5 w-5 transform rounded-full bg-white shadow-sm transition-transform duration-300 ease-in-out ${
              isPublic ? 'translate-x-6' : 'translate-x-1'
            }`}
          />
        </button>
      </div>

      {/* Info box */}
      <div className="mt-4 p-4 bg-azure-25 rounded-xl border border-azure-200">
        <div className="flex gap-2">
          <Info className="w-4 h-4 text-azure-600 mt-0.5 shrink-0" aria-hidden="true" />
          <p className="text-xs text-azure-700 leading-relaxed">
            {t('privacyToggle.info')}
          </p>
        </div>
      </div>
    </div>
  );
}
