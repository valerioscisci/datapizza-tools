'use client';

import { useTranslations } from 'next-intl';
import { useAuth } from '@/lib/auth/use-auth';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';
import { Briefcase, ExternalLink, X, Check } from 'lucide-react';
import { formatSalary, formatDate, workModeLabel } from '@/lib/job-utils';
import { TechTag } from '@/components/ui/TechTag';
import { API_BASE, experienceLevelEmoji } from '../_utils/constants';
import type { Job } from '../_utils/types';
import { Badge } from './Badge';

export interface JobDetailDialogProps {
  job: Job;
  onClose: () => void;
}

export function JobDetailDialog({ job, onClose }: JobDetailDialogProps) {
  const tApps = useTranslations('applications');
  const tJobs = useTranslations('jobs');
  const { user, accessToken } = useAuth();
  const router = useRouter();
  const salary = formatSalary(job.salary_min, job.salary_max);
  const [applyState, setApplyState] = useState<'idle' | 'loading' | 'success' | 'duplicate'>('idle');

  // Lock body scroll while dialog is open
  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  // Close on Escape
  useEffect(() => {
    function handleEsc(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
    }
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  async function handleApply() {
    if (!user || !accessToken) {
      router.push('/it/login');
      return;
    }
    setApplyState('loading');
    try {
      const res = await fetch(`${API_BASE}/api/v1/applications`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ job_id: job.id }),
      });
      if (res.status === 409) {
        setApplyState('duplicate');
      } else if (res.ok) {
        setApplyState('success');
      } else {
        setApplyState('idle');
      }
    } catch {
      setApplyState('idle');
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose} role="presentation">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />

      {/* Dialog */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="job-dialog-title"
        className="relative bg-white rounded-3xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 bg-neutral-100 rounded-full flex items-center justify-center hover:bg-neutral-200 transition-colors cursor-pointer z-10"
          aria-label={tJobs('dialog.closeLabel')}
        >
          <X className="w-4 h-4 text-neutral-600" />
        </button>

        <div className="p-8">
          {/* Header */}
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center shrink-0 border border-neutral-200">
              <Briefcase className="w-7 h-7 text-neutral-400" />
            </div>
            <div>
              <h2 id="job-dialog-title" className="text-2xl font-heading font-semibold text-black-950">
                {experienceLevelEmoji(job.experience_level)} {job.title}
              </h2>
              <p className="text-azure-600 font-medium mt-1">{job.company}</p>
              <p className="text-xs text-neutral-400 mt-1">
                {tJobs('card.postedAt')} {formatDate(job.created_at, 'short')}
              </p>
            </div>
          </div>

          {/* Badges */}
          <div className="flex flex-wrap gap-2 mt-6">
            {salary && <Badge variant="salary">{'\u{1F4B0}'} RAL {salary}</Badge>}
            {job.employment_type && <Badge variant="default">{job.employment_type === 'full-time' ? 'Full Time' : job.employment_type}</Badge>}
            {job.experience_years && <Badge variant="experience">{'\u{1F9D1}\u200D\u{1F4BC}'} Esperienza: {job.experience_years}</Badge>}
            <Badge variant="work_mode">{'\u{1F465}'} {workModeLabel(job.work_mode)}</Badge>
          </div>

          <div className="flex flex-wrap gap-2 mt-2">
            <Badge variant="location">{'\u{1F4CD}'} {job.location}</Badge>
            {job.welfare && <Badge variant="welfare">{'\u{1F381}'} {job.welfare}</Badge>}
            {job.smart_working && <Badge variant="smart">{'\u{1F4BB}'} Smart {job.smart_working}</Badge>}
            {job.language && <Badge variant="language">{'\u{1F5E3}\uFE0F'} {job.language}</Badge>}
          </div>

          {/* Tech Tags */}
          {job.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-5">
              {job.tags.map((tag, i) => (
                <TechTag key={tag} tag={tag} primary={i < 2} />
              ))}
            </div>
          )}

          {/* Description */}
          <div className="mt-6 pt-6 border-t border-neutral-200">
            <h3 className="text-sm font-semibold text-neutral-900 mb-3">{tJobs('dialog.description')}</h3>
            <p className="text-sm text-neutral-600 leading-relaxed whitespace-pre-line">
              {job.description}
            </p>
          </div>

          {/* CTA */}
          <div className="mt-8 flex gap-3">
            {applyState === 'success' ? (
              <span className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-pastelgreen-100 text-pastelgreen-600 font-medium rounded-xl">
                <Check className="w-4 h-4" />
                {tApps('applied')}
              </span>
            ) : applyState === 'duplicate' ? (
              <span className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-yellow-50 text-yellow-500 font-medium rounded-xl">
                {tApps('alreadyApplied')}
              </span>
            ) : job.apply_url ? (
              <a
                href={job.apply_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer"
              >
                {tJobs('card.apply')}
                <ExternalLink className="w-4 h-4" />
              </a>
            ) : (
              <button
                onClick={handleApply}
                disabled={applyState === 'loading'}
                className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {applyState === 'loading' ? '...' : tJobs('card.apply')}
              </button>
            )}
            <button
              onClick={onClose}
              className="px-6 py-3 bg-neutral-100 text-neutral-700 font-medium rounded-xl hover:bg-neutral-200 transition-colors cursor-pointer"
            >
              {tJobs('dialog.close')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
