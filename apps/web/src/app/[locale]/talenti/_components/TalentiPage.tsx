'use client';

import { useTranslations } from 'next-intl';
import { useRouter } from 'next/navigation';
import { useState, useCallback, useEffect, useRef } from 'react';
import { Search } from 'lucide-react';
import { API_BASE, EXPERIENCE_LEVEL_FILTERS, AVAILABILITY_FILTERS, AI_READINESS_FILTERS, type Talent, type TalentListResponse } from '../_utils/constants';
import { TalentCard } from './TalentCard';

export function TalentiPage() {
  const t = useTranslations('talents');
  const router = useRouter();

  const [talents, setTalents] = useState<Talent[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [searchInput, setSearchInput] = useState('');
  const [submittedSearch, setSubmittedSearch] = useState('');
  const [experienceLevel, setExperienceLevel] = useState<string>('all');
  const [availability, setAvailability] = useState<string>('all');
  const [aiReadiness, setAiReadiness] = useState<string>('all');
  const debounceRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const fetchTalents = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: '10',
      });
      if (submittedSearch.trim()) {
        params.set('search', submittedSearch.trim());
      }
      if (experienceLevel !== 'all') {
        params.set('experience_level', experienceLevel);
      }
      if (availability !== 'all') {
        params.set('availability', availability);
      }
      if (aiReadiness !== 'all') {
        params.set('ai_readiness', aiReadiness);
      }
      const res = await fetch(`${API_BASE}/api/v1/talents?${params}`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: TalentListResponse = await res.json();
      setTalents(data.items);
      setTotal(data.total);
    } catch {
      setTalents([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }, [page, submittedSearch, experienceLevel, availability, aiReadiness]);

  useEffect(() => {
    fetchTalents();
  }, [fetchTalents]);

  const handleSearchChange = (value: string) => {
    setSearchInput(value);
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => {
      setSubmittedSearch(value);
      setPage(1);
    }, 350);
  };

  // Cleanup debounce on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, []);

  const handleSearchKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      if (debounceRef.current) clearTimeout(debounceRef.current);
      setSubmittedSearch(searchInput);
      setPage(1);
    }
  };

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

      {/* Filters + Talents */}
      <section className="py-8 sm:py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Search */}
          <div className="relative mb-6">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400" aria-hidden="true" />
            <input
              type="text"
              value={searchInput}
              onChange={(e) => handleSearchChange(e.target.value)}
              onKeyDown={handleSearchKeyDown}
              placeholder={t('search.placeholder')}
              className="w-full pl-12 pr-4 py-3 border border-neutral-200 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-azure-500 focus:border-azure-500"
            />
          </div>

          {/* Filter buttons */}
          <div className="flex flex-col sm:flex-row gap-4 mb-8">
            {/* Experience Level */}
            <div className="flex flex-wrap gap-2">
              <span className="flex items-center text-xs font-semibold text-neutral-400 uppercase tracking-wider mr-1">
                {t('filters.experienceLevel')}
              </span>
              {EXPERIENCE_LEVEL_FILTERS.map((level) => (
                <button
                  key={level}
                  onClick={() => { setExperienceLevel(level); setPage(1); }}
                  aria-pressed={experienceLevel === level}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                    experienceLevel === level
                      ? 'bg-azure-600 text-white'
                      : 'bg-white text-neutral-600 border border-neutral-200 hover:border-azure-300 hover:text-azure-600'
                  }`}
                >
                  {t(`filters.${level}` as Parameters<typeof t>[0])}
                </button>
              ))}
            </div>

            {/* Availability */}
            <div className="flex flex-wrap gap-2">
              <span className="flex items-center text-xs font-semibold text-neutral-400 uppercase tracking-wider mr-1">
                {t('filters.availability')}
              </span>
              {AVAILABILITY_FILTERS.map((status) => (
                <button
                  key={status}
                  onClick={() => { setAvailability(status); setPage(1); }}
                  aria-pressed={availability === status}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                    availability === status
                      ? 'bg-azure-600 text-white'
                      : 'bg-white text-neutral-600 border border-neutral-200 hover:border-azure-300 hover:text-azure-600'
                  }`}
                >
                  {t(`filters.${status}` as Parameters<typeof t>[0])}
                </button>
              ))}
            </div>

            {/* AI Readiness */}
            <div className="flex flex-wrap gap-2">
              <span className="flex items-center text-xs font-semibold text-neutral-400 uppercase tracking-wider mr-1">
                {t('filters.aiReadiness')}
              </span>
              {AI_READINESS_FILTERS.map((level) => (
                <button
                  key={level}
                  onClick={() => { setAiReadiness(level); setPage(1); }}
                  aria-pressed={aiReadiness === level}
                  className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                    aiReadiness === level
                      ? 'bg-azure-600 text-white'
                      : 'bg-white text-neutral-600 border border-neutral-200 hover:border-azure-300 hover:text-azure-600'
                  }`}
                >
                  {level === 'all'
                    ? t('filters.aiReadinessAll')
                    : t(`filters.${level}` as Parameters<typeof t>[0])}
                </button>
              ))}
            </div>
          </div>

          {/* Talent Cards */}
          <div aria-live="polite">
            {loading ? (
              <div className="text-center py-16">
                <p className="text-neutral-500">{t('loading')}</p>
              </div>
            ) : talents.length === 0 ? (
              <div className="text-center py-16">
                <p className="text-neutral-500 font-medium">{t('empty')}</p>
                <p className="text-neutral-400 text-sm mt-2">{t('emptyDescription')}</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {talents.map((talent) => (
                  <TalentCard
                    key={talent.id}
                    talent={talent}
                    onClick={() => router.push(`/it/talenti/${talent.id}`)}
                    t={t}
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
    </>
  );
}
