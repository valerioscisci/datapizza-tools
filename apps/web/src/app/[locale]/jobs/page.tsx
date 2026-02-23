'use client';

import { useTranslations } from 'next-intl';
import { useEffect, useState } from 'react';
import { MapPin, Briefcase, ExternalLink, X, ChevronDown } from 'lucide-react';

interface Job {
  id: string;
  title: string;
  company: string;
  company_logo_url: string | null;
  location: string;
  work_mode: string;
  description: string;
  salary_min: number | null;
  salary_max: number | null;
  tags: string[];
  experience_level: string;
  experience_years: string | null;
  employment_type: string;
  smart_working: string | null;
  welfare: string | null;
  language: string | null;
  apply_url: string | null;
  created_at: string;
}

interface JobListResponse {
  items: Job[];
  total: number;
  page: number;
  page_size: number;
}

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8003';

const WORK_MODE_FILTERS = ['all', 'remote', 'hybrid', 'onsite'] as const;

function formatSalary(min: number | null, max: number | null): string | null {
  if (!min && !max) return null;
  const fmt = (n: number) => `${(n / 1000).toFixed(0)}k`;
  if (min && max) return `${fmt(min)}-${fmt(max)}`;
  if (min) return `da ${fmt(min)}`;
  return `fino a ${fmt(max!)}`;
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleDateString('it-IT', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  });
}

function workModeLabel(mode: string): string {
  switch (mode) {
    case 'remote': return 'Full Remote';
    case 'hybrid': return 'Lavoro Ibrido';
    case 'onsite': return 'In Sede';
    default: return mode;
  }
}

function experienceLevelEmoji(level: string): string {
  switch (level) {
    case 'junior': return '🌱';
    case 'mid': return '👨\u200d💻';
    case 'senior': return '🧑\u200d💻';
    default: return '👤';
  }
}

function Badge({ children, variant = 'default' }: { children: React.ReactNode; variant?: 'salary' | 'experience' | 'work_mode' | 'location' | 'welfare' | 'smart' | 'language' | 'default' }) {
  const colors: Record<string, string> = {
    salary: 'bg-yellow-50 text-yellow-500 border-yellow-400/30',
    experience: 'bg-azure-50 text-azure-700 border-azure-300/30',
    work_mode: 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30',
    location: 'bg-neutral-100 text-neutral-700 border-neutral-300/30',
    welfare: 'bg-red-50 text-red-600 border-red-500/30',
    smart: 'bg-neutral-100 text-neutral-600 border-neutral-300/30',
    language: 'bg-azure-50 text-azure-600 border-azure-300/30',
    default: 'bg-neutral-100 text-neutral-600 border-neutral-200',
  };

  return (
    <span className={`inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium rounded-full border ${colors[variant]}`}>
      {children}
    </span>
  );
}

function TechTag({ tag, primary }: { tag: string; primary: boolean }) {
  return (
    <span className={`inline-flex items-center px-2.5 py-1 text-xs font-medium rounded-full border ${
      primary
        ? 'bg-pastelgreen-100 text-pastelgreen-600 border-pastelgreen-500/30'
        : 'bg-neutral-100 text-neutral-600 border-neutral-200'
    }`}>
      {tag}
    </span>
  );
}

function JobCard({ job, onClick }: { job: Job; onClick: () => void }) {
  const salary = formatSalary(job.salary_min, job.salary_max);

  return (
    <div
      onClick={onClick}
      onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onClick(); } }}
      tabIndex={0}
      role="button"
      className="p-6 bg-white rounded-2xl border border-neutral-200 hover:border-azure-300 hover:shadow-lg transition-all duration-300 cursor-pointer group"
    >
      <div className="flex items-start gap-4">
        {/* Company Logo */}
        <div className="w-14 h-14 bg-neutral-100 rounded-full flex items-center justify-center shrink-0 border border-neutral-200">
          <Briefcase className="w-6 h-6 text-neutral-400" />
        </div>

        <div className="flex-1 min-w-0">
          {/* Title + Company */}
          <h3 className="text-lg font-semibold text-black-950 group-hover:text-azure-600 transition-colors">
            {experienceLevelEmoji(job.experience_level)} {job.title}
          </h3>
          <p className="text-sm text-azure-600 font-medium mt-0.5">{job.company}</p>
        </div>

        {/* Expand hint */}
        <ChevronDown className="w-5 h-5 text-neutral-300 group-hover:text-azure-400 transition-colors shrink-0 mt-1" />
      </div>

      {/* Info Badges */}
      <div className="flex flex-wrap gap-2 mt-4">
        {salary && <Badge variant="salary">💰 RAL {salary}</Badge>}
        {job.employment_type && <Badge variant="default">{job.employment_type === 'full-time' ? 'Full Time' : job.employment_type}</Badge>}
        {job.experience_years && <Badge variant="experience">🧑‍💼 Esperienza: {job.experience_years}</Badge>}
        <Badge variant="work_mode">👥 {workModeLabel(job.work_mode)}</Badge>
      </div>

      <div className="flex flex-wrap gap-2 mt-2">
        <Badge variant="location">📍 {job.location}</Badge>
        {job.welfare && <Badge variant="welfare">🎁 {job.welfare}</Badge>}
        {job.smart_working && <Badge variant="smart">💻 Smart {job.smart_working}</Badge>}
      </div>

      {job.language && (
        <div className="flex flex-wrap gap-2 mt-2">
          <Badge variant="language">🗣️ {job.language}</Badge>
        </div>
      )}

      {/* Tech Tags */}
      {job.tags.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mt-4">
          {job.tags.map((tag, i) => (
            <TechTag key={tag} tag={tag} primary={i < 2} />
          ))}
        </div>
      )}

      {/* Description */}
      <p className="mt-4 text-sm text-neutral-500 line-clamp-3 leading-relaxed">
        {job.description}
      </p>
    </div>
  );
}

function JobDetailDialog({ job, onClose }: { job: Job; onClose: () => void }) {
  const salary = formatSalary(job.salary_min, job.salary_max);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4" onClick={onClose} role="presentation">
      {/* Backdrop */}
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />

      {/* Dialog */}
      <div
        role="dialog"
        aria-modal="true"
        aria-labelledby="job-dialog-title"
        className="relative bg-white rounded-3xl shadow-2xl w-full max-w-2xl max-h-[85vh] overflow-y-auto"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-4 right-4 w-8 h-8 bg-neutral-100 rounded-full flex items-center justify-center hover:bg-neutral-200 transition-colors cursor-pointer z-10"
          aria-label="Chiudi"
        >
          <X className="w-4 h-4 text-neutral-600" />
        </button>

        <div className="p-8">
          {/* Header */}
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 bg-neutral-100 rounded-full flex items-center justify-center shrink-0 border border-neutral-200">
              <Briefcase className="w-7 h-7 text-neutral-400" />
            </div>
            <div>
              <h2 id="job-dialog-title" className="text-2xl font-heading font-semibold text-black-950">
                {experienceLevelEmoji(job.experience_level)} {job.title}
              </h2>
              <p className="text-azure-600 font-medium mt-1">{job.company}</p>
              <p className="text-xs text-neutral-400 mt-1">
                Pubblicata il {formatDate(job.created_at)}
              </p>
            </div>
          </div>

          {/* Badges */}
          <div className="flex flex-wrap gap-2 mt-6">
            {salary && <Badge variant="salary">💰 RAL {salary}</Badge>}
            {job.employment_type && <Badge variant="default">{job.employment_type === 'full-time' ? 'Full Time' : job.employment_type}</Badge>}
            {job.experience_years && <Badge variant="experience">🧑‍💼 Esperienza: {job.experience_years}</Badge>}
            <Badge variant="work_mode">👥 {workModeLabel(job.work_mode)}</Badge>
          </div>

          <div className="flex flex-wrap gap-2 mt-2">
            <Badge variant="location">📍 {job.location}</Badge>
            {job.welfare && <Badge variant="welfare">🎁 {job.welfare}</Badge>}
            {job.smart_working && <Badge variant="smart">💻 Smart {job.smart_working}</Badge>}
            {job.language && <Badge variant="language">🗣️ {job.language}</Badge>}
          </div>

          {/* Tech Tags */}
          {job.tags.length > 0 && (
            <div className="flex flex-wrap gap-1.5 mt-5">
              {job.tags.map((tag, i) => (
                <TechTag key={tag} tag={tag} primary={i < 2} />
              ))}
            </div>
          )}

          {/* Description */}
          <div className="mt-6 pt-6 border-t border-neutral-200">
            <h3 className="text-sm font-semibold text-neutral-900 mb-3">Descrizione</h3>
            <p className="text-sm text-neutral-600 leading-relaxed whitespace-pre-line">
              {job.description}
            </p>
          </div>

          {/* CTA */}
          <div className="mt-8 flex gap-3">
            {job.apply_url ? (
              <a
                href={job.apply_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer"
              >
                Candidati
                <ExternalLink className="w-4 h-4" />
              </a>
            ) : (
              <span className="flex-1 inline-flex items-center justify-center gap-2 px-6 py-3 bg-neutral-300 text-neutral-500 font-medium rounded-xl">
                Candidatura non disponibile
              </span>
            )}
            <button
              onClick={onClose}
              className="px-6 py-3 bg-neutral-100 text-neutral-700 font-medium rounded-xl hover:bg-neutral-200 transition-colors cursor-pointer"
            >
              Chiudi
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function JobsPage() {
  const t = useTranslations('jobs');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);

  useEffect(() => {
    fetchJobs();
  }, [page, filter]);

  // Close dialog on Escape
  useEffect(() => {
    function handleEsc(e: KeyboardEvent) {
      if (e.key === 'Escape') setSelectedJob(null);
    }
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  async function fetchJobs() {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: String(page),
        page_size: '10',
      });
      if (filter !== 'all') {
        params.set('work_mode', filter);
      }
      const res = await fetch(`${API_BASE}/api/v1/jobs?${params}`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: JobListResponse = await res.json();
      setJobs(data.items);
      setTotal(data.total);
    } catch {
      setJobs([]);
      setTotal(0);
    } finally {
      setLoading(false);
    }
  }

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

      {/* Filters + Jobs */}
      <section className="py-8 sm:py-12">
        <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Filters */}
          <div className="flex flex-wrap gap-2 mb-8">
            {WORK_MODE_FILTERS.map((mode) => (
              <button
                key={mode}
                onClick={() => { setFilter(mode); setPage(1); }}
                className={`px-4 py-2 text-sm font-medium rounded-lg transition-colors cursor-pointer ${
                  filter === mode
                    ? 'bg-azure-600 text-white'
                    : 'bg-white text-neutral-600 border border-neutral-200 hover:border-azure-300 hover:text-azure-600'
                }`}
              >
                {t(`filters.${mode}`)}
              </button>
            ))}
          </div>

          {/* Job Cards */}
          {loading ? (
            <div className="text-center py-16">
              <p className="text-neutral-500">{t('loading')}</p>
            </div>
          ) : jobs.length === 0 ? (
            <div className="text-center py-16">
              <p className="text-neutral-500">{t('empty')}</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {jobs.map((job) => (
                <JobCard
                  key={job.id}
                  job={job}
                  onClick={() => setSelectedJob(job)}
                />
              ))}
            </div>
          )}

          {/* Pagination */}
          {total > 10 && (
            <div className="flex justify-center gap-2 mt-8">
              <button
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                disabled={page === 1}
                className="px-4 py-2 text-sm font-medium rounded-lg bg-white border border-neutral-200 text-neutral-600 hover:border-azure-300 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                Precedente
              </button>
              <span className="px-4 py-2 text-sm text-neutral-500">
                Pagina {page} di {Math.ceil(total / 10)}
              </span>
              <button
                onClick={() => setPage((p) => p + 1)}
                disabled={page >= Math.ceil(total / 10)}
                className="px-4 py-2 text-sm font-medium rounded-lg bg-white border border-neutral-200 text-neutral-600 hover:border-azure-300 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                Successiva
              </button>
            </div>
          )}
        </div>
      </section>

      {/* Job Detail Dialog */}
      {selectedJob && (
        <JobDetailDialog
          job={selectedJob}
          onClose={() => setSelectedJob(null)}
        />
      )}
    </>
  );
}
