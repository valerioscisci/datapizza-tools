'use client';

import { MapPin, Briefcase, Clock } from 'lucide-react';
import { AvailabilityBadge } from './AvailabilityBadge';
import { TalentCardProps } from './TalentCard.props';

const MAX_VISIBLE_SKILLS = 5;

export function TalentCard({ talent, onClick, t }: TalentCardProps) {
  const visibleSkills = talent.skills.slice(0, MAX_VISIBLE_SKILLS);
  const remainingCount = talent.skills.length - MAX_VISIBLE_SKILLS;

  return (
    <div
      onClick={onClick}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick(); } }}
      tabIndex={0}
      role="button"
      className="p-6 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 hover:shadow-lg transition-all duration-300 cursor-pointer group"
    >
      <div className="flex items-start gap-4">
        {/* Avatar Initial */}
        <div className="w-14 h-14 bg-azure-100 rounded-full flex items-center justify-center text-xl font-heading font-semibold text-azure-700 shrink-0">
          {talent.full_name.charAt(0).toUpperCase()}
        </div>

        <div className="flex-1 min-w-0">
          {/* Name */}
          <h3 className="text-lg font-heading font-semibold text-black-950 group-hover:text-azure-600 transition-colors">
            {talent.full_name}
          </h3>

          {/* Current Role */}
          {talent.current_role && (
            <p className="text-sm text-azure-600 font-medium mt-0.5 flex items-center gap-1">
              <Briefcase className="w-3.5 h-3.5" aria-hidden="true" />
              {talent.current_role}
            </p>
          )}

          {/* Location */}
          {talent.location && (
            <p className="text-sm text-neutral-500 mt-1 flex items-center gap-1">
              <MapPin className="w-3.5 h-3.5" aria-hidden="true" />
              {talent.location}
            </p>
          )}
        </div>
      </div>

      {/* Badges row */}
      <div className="flex flex-wrap gap-2 mt-4">
        {talent.experience_level && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full border bg-azure-50 text-azure-700 border-azure-300/30">
            {t(`filters.${talent.experience_level}` as Parameters<typeof t>[0])}
          </span>
        )}
        {talent.experience_years && (
          <span className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full border bg-neutral-100 text-neutral-600 border-neutral-200">
            <Clock className="w-3 h-3" aria-hidden="true" />
            {talent.experience_years}
          </span>
        )}
        <AvailabilityBadge
          status={talent.availability_status}
          label={t(`filters.${talent.availability_status}` as Parameters<typeof t>[0])}
        />
      </div>

      {/* Skills Pills */}
      {talent.skills.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-4">
          {visibleSkills.map((skill) => (
            <span
              key={skill}
              className="inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full border bg-azure-50 text-azure-700 border-azure-300/30"
            >
              {skill}
            </span>
          ))}
          {remainingCount > 0 && (
            <span className="inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full border bg-neutral-100 text-neutral-600 border-neutral-200">
              +{remainingCount}
            </span>
          )}
        </div>
      )}

      {/* Bio */}
      {talent.bio && (
        <p className="mt-4 text-sm text-neutral-500 line-clamp-2 leading-relaxed">
          {talent.bio}
        </p>
      )}
    </div>
  );
}
