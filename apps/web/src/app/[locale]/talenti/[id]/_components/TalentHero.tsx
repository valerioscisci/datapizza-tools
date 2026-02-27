'use client';

import {
  Briefcase,
  MapPin,
  Linkedin,
  Github,
  Globe,
} from 'lucide-react';
import { useTranslations } from 'next-intl';
import { availabilityBadgeStyle } from '../_utils/constants';
import { TalentHeroProps } from './TalentHero.props';

export function TalentHero({ talent, tProfile }: TalentHeroProps) {
  return (
    <section className="bg-linear-to-b from-azure-25 to-white py-16 sm:py-20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center">
          {/* Avatar */}
          <div className="w-24 h-24 bg-azure-100 rounded-full flex items-center justify-center text-3xl font-heading font-semibold text-azure-700 mb-4 border-4 border-white shadow-lg">
            {talent.full_name.charAt(0).toUpperCase()}
          </div>

          {/* Name */}
          <h1 className="text-3xl sm:text-4xl font-heading font-semibold text-black-950">
            {talent.full_name}
          </h1>

          {/* Role | Location */}
          <div className="flex items-center gap-2 mt-2 text-neutral-600 text-base">
            {talent.current_role && (
              <span className="flex items-center gap-1">
                <Briefcase className="w-4 h-4" aria-hidden="true" />
                {talent.current_role}
              </span>
            )}
            {talent.current_role && talent.location && (
              <span className="text-neutral-300">|</span>
            )}
            {talent.location && (
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4" aria-hidden="true" />
                {talent.location}
              </span>
            )}
          </div>

          {/* Badges */}
          <div className="flex flex-wrap items-center justify-center gap-2 mt-3">
            <span
              className={`inline-flex items-center px-3 py-1 text-sm font-medium rounded-full border ${availabilityBadgeStyle(talent.availability_status)}`}
            >
              {tProfile(`availability_options.${talent.availability_status}` as Parameters<typeof tProfile>[0])}
            </span>
            {talent.experience_level && (
              <span className="inline-flex items-center px-3 py-1 text-sm font-medium rounded-full border bg-azure-50 text-azure-700 border-azure-300/30">
                {tProfile(`experience_levels.${talent.experience_level}` as Parameters<typeof tProfile>[0])}
              </span>
            )}
            {talent.experience_years && (
              <span className="inline-flex items-center px-3 py-1 text-sm font-medium rounded-full border bg-neutral-100 text-neutral-600 border-neutral-200">
                {talent.experience_years}
              </span>
            )}
          </div>

          {/* Social links */}
          <div className="flex items-center gap-3 mt-4">
            {talent.linkedin_url && (
              <a
                href={talent.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer"
                aria-label="LinkedIn"
              >
                <Linkedin className="w-5 h-5" aria-hidden="true" />
              </a>
            )}
            {talent.github_url && (
              <a
                href={talent.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" aria-hidden="true" />
              </a>
            )}
            {talent.portfolio_url && (
              <a
                href={talent.portfolio_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer"
                aria-label="Portfolio"
              >
                <Globe className="w-5 h-5" aria-hidden="true" />
              </a>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
