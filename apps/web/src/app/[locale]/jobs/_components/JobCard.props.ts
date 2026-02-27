import type { Job, JobMatchResult } from '../_utils/types';

export interface JobCardProps {
  job: Job;
  match?: JobMatchResult;
  onClick: () => void;
}
