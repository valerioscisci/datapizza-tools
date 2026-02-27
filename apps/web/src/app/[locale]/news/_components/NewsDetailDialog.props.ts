import type { NewsItem } from '../_utils/types';

export interface NewsDetailDialogProps {
  news: NewsItem;
  onClose: () => void;
}
