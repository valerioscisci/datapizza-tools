import type { Job, JobMatchResult } from '../_utils/types';

export interface JobDetailDialogProps {
  job: Job;
  match?: JobMatchResult;
  onClose: () => void;
}
