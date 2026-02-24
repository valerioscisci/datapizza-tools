'use client';

import { useTranslations } from 'next-intl';
import { Briefcase, Calendar } from 'lucide-react';
import { formatSalary, formatDate, workModeLabel } from '@/lib/job-utils';
import { statusBadgeStyle } from '../_utils/constants';
import type { Application } from '../_utils/types';

export function ApplicationCard({ app }: { app: Application }) {
  const t = useTranslations('applications');
  const salary = formatSalary(app.job.salary_min, app.job.salary_max);

  return (
    <div className="p-6 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 hover:shadow-lg transition-all duration-300">
      <div className="flex items-start gap-4">
        {/* Company Logo Placeholder */}
        <div className="w-14 h-14 bg-neutral-100 rounded-full flex items-center justify-center shrink-0 border border-neutral-200">
          <Briefcase className="w-6 h-6 text-neutral-400" />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <div>
              <h3 className="text-lg font-semibold text-black-950">{app.job.title}</h3>
              <p className="text-sm text-azure-600 font-medium mt-0.5">{app.job.company}</p>
            </div>
            {/* Status Badge */}
            <span className={`inline-flex items-center px-3 py-1 text-xs font-medium rounded-full border shrink-0 ${statusBadgeStyle(app.status)}`}>
              {app.status_detail || app.status}
            </span>
          </div>
        </div>
      </div>

      {/* Info Badges */}
      <div className="flex flex-wrap gap-2 mt-4">
        {salary && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full border bg-yellow-50 text-yellow-500 border-yellow-400/30">
            RAL {salary}
          </span>
        )}
        {app.job.experience_years && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full border bg-azure-50 text-azure-700 border-azure-300/30">
            {app.job.experience_years}
          </span>
        )}
        <span className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full border bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30">
          {workModeLabel(app.job.work_mode)}
        </span>
      </div>

      {/* Tech Tags */}
      {app.job.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {app.job.tags.map((tag, i) => (
            <span
              key={tag}
              className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full border ${
                i < 2
                  ? 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30'
                  : 'bg-neutral-100 text-neutral-600 border-neutral-200'
              }`}
            >
              {tag}
            </span>
          ))}
        </div>
      )}

      {/* Status Detail Box */}
      <div className="mt-4 pt-4 border-t border-neutral-100">
        <div className="flex items-center justify-between">
          <div>
            {app.recruiter_name && (
              <p className="text-sm text-neutral-700">
                <span className="font-medium">{app.recruiter_name}</span>
                {app.recruiter_role && (
                  <span className="text-neutral-400 ml-1">- {app.recruiter_role}</span>
                )}
              </p>
            )}
          </div>
          <div className="flex items-center gap-1 text-xs text-neutral-400">
            <Calendar className="w-3.5 h-3.5" />
            {formatDate(app.applied_at)}
          </div>
        </div>
      </div>
    </div>
  );
}
