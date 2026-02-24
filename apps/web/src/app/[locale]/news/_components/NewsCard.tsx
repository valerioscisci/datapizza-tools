'use client';

import { Newspaper, ChevronDown, Calendar } from 'lucide-react';
import { formatDate } from '@/lib/job-utils';
import { TechTag } from '@/components/ui/TechTag';
import { categoryBadgeColor } from '../_utils/constants';
import type { NewsItem } from '../_utils/types';
import { Badge } from './Badge';

export function NewsCard({ news, onClick }: { news: NewsItem; onClick: () => void }) {
  return (
    <div
      onClick={onClick}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick(); } }}
      tabIndex={0}
      role="button"
      className="p-6 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 hover:shadow-lg transition-all duration-300 cursor-pointer group"
    >
      <div className="flex items-start gap-4">
        <div className="w-14 h-14 bg-neutral-100 rounded-full flex items-center justify-center shrink-0 border border-neutral-200">
          <Newspaper className="w-6 h-6 text-neutral-400" />
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-black-950 group-hover:text-azure-600 transition-colors">
            {news.title}
          </h3>
          <p className="text-sm text-azure-600 font-medium mt-0.5">{news.source}</p>
        </div>

        <ChevronDown className="w-5 h-5 text-neutral-300 group-hover:text-azure-400 transition-colors shrink-0 mt-1" />
      </div>

      <div className="flex flex-wrap gap-2 mt-4">
        <Badge className={categoryBadgeColor(news.category)}>{news.category}</Badge>
      </div>

      {news.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-3">
          {news.tags.map((tag, i) => (
            <TechTag key={tag} tag={tag} primary={i < 2} />
          ))}
        </div>
      )}

      <p className="mt-4 text-sm text-neutral-500 line-clamp-3 leading-relaxed">
        {news.summary}
      </p>

      <div className="flex items-center gap-1.5 mt-4">
        <Calendar className="w-3.5 h-3.5 text-neutral-400" />
        <span className="text-xs text-neutral-400">{formatDate(news.published_at, 'short')}</span>
      </div>
    </div>
  );
}
