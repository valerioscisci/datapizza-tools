'use client';

import { Suspense } from 'react';
import { useTranslations } from 'next-intl';
import { ArrowLeft, Check, Loader2 } from 'lucide-react';
import Link from 'next/link';
import { useNuovaProposta } from '../_hooks/useNuovaProposta';
import { TalentInfoCard } from './TalentInfoCard';
import { CourseSelector } from './CourseSelector';
import { SelectedCoursesList } from './SelectedCoursesList';

function NuovaPropostaContent() {
  const t = useTranslations('proposals.create');
  const tTalents = useTranslations('talents');
  const tCourses = useTranslations('courses');

  const {
    user,
    loading,
    isCompany,
    talent,
    loadingTalent,
    filteredCourses,
    selectedCourses,
    courseSearch,
    setCourseSearch,
    message,
    setMessage,
    budgetRange,
    setBudgetRange,
    submitting,
    error,
    success,
    loadingCourses,
    isSelected,
    toggleCourse,
    moveCourse,
    removeCourse,
    handleSubmit,
  } = useNuovaProposta();

  if (loading || !user || !isCompany) return null;

  const inputClass =
    'w-full px-4 py-2.5 rounded-lg border border-neutral-200 text-sm focus:outline-none focus:ring-2 focus:ring-azure-500 focus:border-azure-500 transition-colors';

  return (
    <>
      {/* Back link */}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pt-8">
        <Link
          href="/it/azienda/proposte"
          className="inline-flex items-center gap-1 text-sm text-neutral-500 hover:text-azure-600 transition-colors cursor-pointer"
        >
          <ArrowLeft className="w-4 h-4" aria-hidden="true" />
          {t('title')}
        </Link>
      </div>

      {/* Header */}
      <section className="bg-linear-to-b from-azure-25 to-white py-12 sm:py-16">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h1 className="text-3xl sm:text-4xl font-heading font-semibold text-black-950">
            {t('title')}
          </h1>
          <p className="mt-3 text-lg text-neutral-600 max-w-2xl mx-auto">
            {t('subtitle')}
          </p>
        </div>
      </section>

      {/* Form */}
      <section className="py-8 sm:py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">
          {/* Success */}
          {success && (
            <div className="p-4 rounded-xl bg-pastelgreen-100 border border-pastelgreen-500/30 text-pastelgreen-600 text-sm font-medium flex items-center gap-2">
              <Check className="w-5 h-5" aria-hidden="true" />
              {t('success')}
            </div>
          )}

          {/* Error */}
          {error && (
            <div className="p-4 rounded-xl bg-red-50 border border-red-200 text-red-600 text-sm">
              {error}
            </div>
          )}

          {/* Talent Info */}
          <TalentInfoCard
            talent={talent}
            loadingTalent={loadingTalent}
            t={t}
            tTalents={tTalents}
          />

          {/* Form Content */}
          <form onSubmit={(e) => handleSubmit(e, t('atLeastOneCourse'))} className="space-y-6">
            {/* Course Selection */}
            <CourseSelector
              filteredCourses={filteredCourses}
              courseSearch={courseSearch}
              setCourseSearch={setCourseSearch}
              isSelected={isSelected}
              toggleCourse={toggleCourse}
              loadingCourses={loadingCourses}
              t={t}
              tCourses={tCourses}
            />

            {/* Selected Courses - Reorderable */}
            <SelectedCoursesList
              selectedCourses={selectedCourses}
              moveCourse={moveCourse}
              removeCourse={removeCourse}
              t={t}
            />

            {/* Message */}
            <div className="p-6 bg-white rounded-2xl border border-neutral-200">
              <label htmlFor="message" className="block text-lg font-heading font-semibold text-black-950 mb-2">
                {t('message')}
              </label>
              <textarea
                id="message"
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder={t('messagePlaceholder')}
                className={`${inputClass} min-h-[120px] resize-y`}
              />
            </div>

            {/* Budget */}
            <div className="p-6 bg-white rounded-2xl border border-neutral-200">
              <label htmlFor="budget" className="block text-lg font-heading font-semibold text-black-950 mb-2">
                {t('budgetRange')}
              </label>
              <input
                id="budget"
                type="text"
                value={budgetRange}
                onChange={(e) => setBudgetRange(e.target.value)}
                placeholder={t('budgetPlaceholder')}
                className={inputClass}
              />
            </div>

            {/* Submit */}
            <div className="flex justify-end">
              <button
                type="submit"
                disabled={submitting || success || !talent}
                className="px-8 py-3.5 bg-azure-600 text-white font-medium rounded-xl hover:bg-azure-700 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {submitting && <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />}
                {submitting ? t('submitting') : t('submit')}
              </button>
            </div>
          </form>
        </div>
      </section>
    </>
  );
}

export function NuovaPropostaPage() {
  return (
    <Suspense fallback={null}>
      <NuovaPropostaContent />
    </Suspense>
  );
}
