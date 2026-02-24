'use client';

import { useTranslations } from 'next-intl';
import { useEffect } from 'react';
import { Newspaper, ExternalLink, X } from 'lucide-react';
import { formatDate } from '@/lib/job-utils';
import { TechTag } from '@/components/ui/TechTag';
import { categoryBadgeColor } from '../_utils/constants';
import type { NewsItem } from '../_utils/types';
import { Badge } from './Badge';

export function NewsDetailDialog({ news, onClose }: { news: NewsItem; onClose: () => void }) {
  const t = useTranslations('news');

  useEffect(() => {
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, []);

  // Close on Escape
  useEffect(() => {
    function handleEsc(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose();
    }
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose} role="presentation">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />

      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="news-dialog-title"
        className="relative bg-white rounded-3xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 bg-neutral-100 rounded-full flex items-center justify-center hover:bg-neutral-200 transition-colors cursor-pointer z-10"
          aria-label={t('dialog.closeLabel')}
        >
          <X className="w-4 h-4 text-neutral-600" />
        </button>

        <div className="p-8">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center shrink-0 border border-neutral-200">
              <Newspaper className="w-7 h-7 text-neutral-400" />
            </div>
            <div>
              <h2 id="news-dialog-title" className="text-2xl font-heading font-semibold text-black-950">
                {news.title}
              </h2>
              <p className="text-azure-600 font-medium mt-1">{news.source}</p>
              <p className="text-xs text-neutral-400 mt-1">
                {t('card.publishedAt')} {formatDate(news.published_at, 'short')}
              </p>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 mt-6">
            <Badge className={categoryBadgeColor(news.category)}>{news.category}</Badge>
          </div>

          {news.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-5">
              {news.tags.map((tag, i) => (
                <TechTag key={tag} tag={tag} primary={i < 2} />
              ))}
            </div>
          )}

          <div className="mt-6 pt-6 border-t border-neutral-200">
            <p className="text-sm text-neutral-600 leading-relaxed whitespace-pre-line">
              {news.summary}
            </p>
          </div>

          <div className="mt-8 flex gap-3">
            {news.source_url ? (
              <a
                href={news.source_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer"
              >
                {t('dialog.readArticle')}
                <ExternalLink className="w-4 h-4" />
              </a>
            ) : null}
            <button
              onClick={onClose}
              className="px-6 py-3 bg-neutral-100 text-neutral-700 font-medium rounded-xl hover:bg-neutral-200 transition-colors cursor-pointer"
            >
              {t('dialog.close')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
