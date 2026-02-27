import type { NewsItem } from '../_utils/types';

export interface NewsCardProps {
  news: NewsItem;
  onClick: () => void;
}
