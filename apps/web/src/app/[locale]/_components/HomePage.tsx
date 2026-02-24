'use client';

import { HeroSection } from './HeroSection';
import { StatsSection } from './StatsSection';
import { ServicesSection } from './ServicesSection';
import { CommunitySection } from './CommunitySection';
import { HomeCtaSection } from './HomeCtaSection';

export function HomePage() {
  return (
    <>
      <HeroSection />
      <StatsSection />
      <ServicesSection />
      <CommunitySection />
      <HomeCtaSection />
    </>
  );
}
