'use client';

import {
  Briefcase,
  MapPin,
  Linkedin,
  Github,
  Globe,
  Pencil,
} from 'lucide-react';
import { useTranslations } from 'next-intl';
import { ProfileResponse, availabilityBadgeStyle } from '../_utils/constants';

interface ProfileHeaderProps {
  profile: ProfileResponse;
  onEdit: () => void;
  t: ReturnType<typeof useTranslations>;
}

export function ProfileHeader({ profile, onEdit, t }: ProfileHeaderProps) {
  return (
    <section className="bg-linear-to-b from-azure-25 to-white py-16 sm:py-20">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col items-center text-center">
          {/* Avatar */}
          <div className="w-24 h-24 bg-azure-100 rounded-full flex items-center justify-center text-3xl font-heading font-semibold text-azure-700 mb-4 border-4 border-white shadow-lg">
            {profile.full_name.charAt(0).toUpperCase()}
          </div>

          {/* Name */}
          <h1 className="text-3xl sm:text-4xl font-heading font-semibold text-black-950">
            {profile.full_name}
          </h1>

          {/* Role | Location */}
          <div className="flex items-center gap-2 mt-2 text-neutral-600 text-base">
            {profile.current_role && (
              <span className="flex items-center gap-1">
                <Briefcase className="w-4 h-4" aria-hidden="true" />
                {profile.current_role}
              </span>
            )}
            {profile.current_role && profile.location && (
              <span className="text-neutral-300">|</span>
            )}
            {profile.location && (
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4" aria-hidden="true" />
                {profile.location}
              </span>
            )}
          </div>

          {/* Availability badge */}
          <div className="mt-3">
            <span
              className={`inline-flex items-center px-3 py-1 text-sm font-medium rounded-full border ${availabilityBadgeStyle(profile.availability_status)}`}
            >
              {t(`availability_options.${profile.availability_status}` as Parameters<typeof t>[0])}
            </span>
          </div>

          {/* Social links */}
          <div className="flex items-center gap-3 mt-4">
            {profile.linkedin_url && (
              <a
                href={profile.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer"
                aria-label="LinkedIn"
              >
                <Linkedin className="w-5 h-5" />
              </a>
            )}
            {profile.github_url && (
              <a
                href={profile.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer"
                aria-label="GitHub"
              >
                <Github className="w-5 h-5" />
              </a>
            )}
            {profile.portfolio_url && (
              <a
                href={profile.portfolio_url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-2 text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer"
                aria-label="Portfolio"
              >
                <Globe className="w-5 h-5" />
              </a>
            )}
          </div>

          {/* Edit button */}
          <button
            onClick={onEdit}
            className="mt-4 px-4 py-2 bg-azure-600 text-white rounded-lg hover:bg-azure-700 transition-colors cursor-pointer flex items-center gap-2 text-sm font-medium"
          >
            <Pencil className="w-4 h-4" aria-hidden="true" />
            {t('editProfile')}
          </button>
        </div>
      </div>
    </section>
  );
}
