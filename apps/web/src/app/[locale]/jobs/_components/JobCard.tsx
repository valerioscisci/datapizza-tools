import { Briefcase, ChevronDown } from 'lucide-react';
import { formatSalary, workModeLabel } from '@/lib/job-utils';
import { TechTag } from '@/components/ui/TechTag';
import { experienceLevelEmoji } from '../_utils/constants';
import type { Job } from '../_utils/types';
import { Badge } from './Badge';

export interface JobCardProps {
  job: Job;
  onClick: () => void;
}

export function JobCard({ job, onClick }: JobCardProps) {
  const salary = formatSalary(job.salary_min, job.salary_max);

  return (
    <div
      onClick={onClick}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick(); } }}
      tabIndex={0}
      role="button"
      className="p-6 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 hover:shadow-lg transition-all duration-300 cursor-pointer group"
    >
      <div className="flex items-start gap-4">
        {/* Company Logo */}
        <div className="w-14 h-14 bg-neutral-100 rounded-full flex items-center justify-center shrink-0 border border-neutral-200">
          <Briefcase className="w-6 h-6 text-neutral-400" />
        </div>

        <div className="flex-1 min-w-0">
          {/* Title + Company */}
          <h3 className="text-lg font-semibold text-black-950 group-hover:text-azure-600 transition-colors">
            {experienceLevelEmoji(job.experience_level)} {job.title}
          </h3>
          <p className="text-sm text-azure-600 font-medium mt-0.5">{job.company}</p>
        </div>

        {/* Expand hint */}
        <ChevronDown className="w-5 h-5 text-neutral-300 group-hover:text-azure-400 transition-colors shrink-0 mt-1" />
      </div>

      {/* Info Badges */}
      <div className="flex flex-wrap gap-2 mt-4">
        {salary && <Badge variant="salary">{'\u{1F4B0}'} RAL {salary}</Badge>}
        {job.employment_type && <Badge variant="default">{job.employment_type === 'full-time' ? 'Full Time' : job.employment_type}</Badge>}
        {job.experience_years && <Badge variant="experience">{'\u{1F9D1}\u200D\u{1F4BC}'} Esperienza: {job.experience_years}</Badge>}
        <Badge variant="work_mode">{'\u{1F465}'} {workModeLabel(job.work_mode)}</Badge>
      </div>

      <div className="flex flex-wrap gap-2 mt-2">
        <Badge variant="location">{'\u{1F4CD}'} {job.location}</Badge>
        {job.welfare && <Badge variant="welfare">{'\u{1F381}'} {job.welfare}</Badge>}
        {job.smart_working && <Badge variant="smart">{'\u{1F4BB}'} Smart {job.smart_working}</Badge>}
      </div>

      {job.language && (
        <div className="flex flex-wrap gap-2 mt-2">
          <Badge variant="language">{'\u{1F5E3}\uFE0F'} {job.language}</Badge>
        </div>
      )}

      {/* Tech Tags */}
      {job.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-4">
          {job.tags.map((tag, i) => (
            <TechTag key={tag} tag={tag} primary={i < 2} />
          ))}
        </div>
      )}

      {/* Description */}
      <p className="mt-4 text-sm text-neutral-500 line-clamp-3 leading-relaxed">
        {job.description}
      </p>
    </div>
  );
}
