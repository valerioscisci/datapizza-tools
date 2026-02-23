'use client';

import { useTranslations } from 'next-intl';
import { useEffect, useState, useCallback } from 'react';
import { Newspaper, ExternalLink, X, ChevronDown, Calendar } from 'lucide-react';
import { formatDate } from '@/lib/job-utils';
import { TechTag } from '@/components/ui/TechTag';

interface NewsItem {
  id: string;
  title: string;
  summary: string;
  source: string;
  source_url: string | null;
  category: string;
  tags: string[];
  author: string | null;
  published_at: string;
  created_at: string;
}

interface NewsListResponse {
  items: NewsItem[];
  total: number;
  page: number;
  page_size: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

const CATEGORY_FILTERS = ['all', 'AI', 'tech', 'careers'] as const;

function categoryBadgeColor(category: string): string {
  switch (category) {
    case 'AI': return 'bg-azure-50 text-azure-700 border-azure-300/30';
    case 'tech': return 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30';
    case 'careers': return 'bg-yellow-50 text-yellow-500 border-yellow-400/30';
    default: return 'bg-neutral-100 text-neutral-600 border-neutral-200';
  }
}

function Badge({ children, className }: { children: React.ReactNode; className: string }) {
  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full border ${className}`}>
      {children}
    </span>
  );
}

function NewsCard({ news, onClick }: { news: NewsItem; onClick: () => void }) {
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

function NewsDetailDialog({ news, onClose }: { news: NewsItem; onClose: () => void }) {
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

export default function NewsPage() {
  const t = useTranslations('news');
  const [news, setNews] = useState<NewsItem[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [selectedNews, setSelectedNews] = useState<NewsItem | null>(null);

  const fetchNews = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: '10',
      });
      if (filter !== 'all') {
        params.set('category', filter);
      }
      const res = await fetch(`${API_BASE}/api/v1/news?${params}`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: NewsListResponse = await res.json();
      setNews(data.items);
      setTotal(data.total);
    } catch {
      setNews([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [page, filter]);

  useEffect(() => {
    fetchNews();
  }, [fetchNews]);

  return (
    <>
      {/* Header */}
      <section className="bg-linear-to-b from-azure-25 to-white py-16 sm:py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-4xl sm:text-5xl font-heading font-semibold text-black-950">
            {t('title')}
          </h1>
          <p className="mt-4 text-lg text-neutral-600 max-w-2xl mx-auto">
            {t('subtitle')}
          </p>
        </div>
      </section>

      {/* Filters + News */}
      <section className="py-8 sm:py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Filters */}
          <div className="flex flex-wrap gap-2 mb-8">
            {CATEGORY_FILTERS.map((cat) => (
              <button
                key={cat}
                onClick={() => { setFilter(cat); setPage(1); }}
                aria-pressed={filter === cat}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                  filter === cat
                    ? 'bg-azure-600 text-white'
                    : 'bg-white text-neutral-600 border border-neutral-200 hover:border-azure-300 hover:text-azure-600'
                }`}
              >
                {t(`filters.${cat}`)}
              </button>
            ))}
          </div>

          {/* News Cards */}
          <div aria-live="polite">
            {loading ? (
              <div className="text-center py-16">
                <p className="text-neutral-500">{t('loading')}</p>
              </div>
            ) : news.length === 0 ? (
              <div className="text-center py-16">
                <p className="text-neutral-500">{t('empty')}</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {news.map((item) => (
                  <NewsCard
                    key={item.id}
                    news={item}
                    onClick={() => setSelectedNews(item)}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Pagination */}
          {total > 10 && (
            <div className="flex justify-center gap-2 mt-8">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 text-sm font-medium rounded-lg bg-white border border-neutral-200 text-neutral-600 hover:border-azure-300 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {t('pagination.previous')}
              </button>
              <span className="px-4 py-2 text-sm text-neutral-500">
                {t('pagination.page', { current: page, total: Math.ceil(total / 10) })}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(total / 10)}
                className="px-4 py-2 text-sm font-medium rounded-lg bg-white border border-neutral-200 text-neutral-600 hover:border-azure-300 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {t('pagination.next')}
              </button>
            </div>
          )}
        </div>
      </section>

      {/* News Detail Dialog */}
      {selectedNews && (
        <NewsDetailDialog
          news={selectedNews}
          onClose={() => setSelectedNews(null)}
        />
      )}
    </>
  );
}
