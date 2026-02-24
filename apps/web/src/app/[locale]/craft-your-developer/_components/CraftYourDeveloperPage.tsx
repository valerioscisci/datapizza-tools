'use client';

import { CraftHeroSection } from './CraftHeroSection';
import { ProblemSection } from './ProblemSection';
import { BenefitsSection } from './BenefitsSection';
import { HowItWorksSection } from './HowItWorksSection';
import { DiscoverTalentsSection } from './DiscoverTalentsSection';
import { ComparisonSection } from './ComparisonSection';
import { CraftCtaSection } from './CraftCtaSection';

export function CraftYourDeveloperPage() {
  return (
    <>
      <CraftHeroSection />
      <ProblemSection />
      <BenefitsSection />
      <HowItWorksSection />
      <DiscoverTalentsSection />
      <ComparisonSection />
      <CraftCtaSection />
    </>
  );
}
