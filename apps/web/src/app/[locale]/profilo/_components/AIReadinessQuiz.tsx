'use client';

import { useState, useEffect, useCallback } from 'react';
import { useTranslations } from 'next-intl';
import { X, ChevronLeft, ChevronRight, Loader2, Send } from 'lucide-react';
import { cn } from '@/lib/utils/utils';
import { AIReadinessQuizProps } from './AIReadinessQuiz.props';

const QUESTION_IDS = [
  'q1_ai_coding_assistants',
  'q2_prompt_writing',
  'q3_agentic_workflows',
  'q4_ai_code_review',
  'q5_ai_api_integration',
  'q6_ai_output_evaluation',
  'q7_rag_systems',
  'q8_prompt_engineering',
] as const;

const ANSWER_VALUES = [0, 1, 2, 3, 4] as const;

const ANSWER_KEYS = ['never', 'beginner', 'intermediate', 'advanced', 'expert'] as const;

export function AIReadinessQuiz({ onSubmit, onClose, loading }: AIReadinessQuizProps) {
  const t = useTranslations('profile.aiReadiness');

  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [showConfirmClose, setShowConfirmClose] = useState(false);

  const totalQuestions = QUESTION_IDS.length;
  const currentQuestionId = QUESTION_IDS[currentStep] as string;
  const isLastQuestion = currentStep === totalQuestions - 1;
  const isFirstQuestion = currentStep === 0;
  const currentAnswer = answers[currentQuestionId];
  const hasAnswered = currentAnswer !== undefined;

  // Lock body scroll and handle Escape key
  useEffect(() => {
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        if (showConfirmClose) {
          setShowConfirmClose(false);
        } else {
          setShowConfirmClose(true);
        }
      }
    };

    document.addEventListener('keydown', handleKeyDown);

    return () => {
      document.body.style.overflow = originalOverflow;
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [showConfirmClose]);

  const handleSelectAnswer = useCallback((value: number) => {
    const questionId = QUESTION_IDS[currentStep] as string;
    setAnswers((prev) => ({
      ...prev,
      [questionId]: value,
    }));
  }, [currentStep]);

  const handleNext = useCallback(() => {
    if (!isLastQuestion && hasAnswered) {
      setCurrentStep((prev) => prev + 1);
    }
  }, [isLastQuestion, hasAnswered]);

  const handleBack = useCallback(() => {
    if (!isFirstQuestion) {
      setCurrentStep((prev) => prev - 1);
    }
  }, [isFirstQuestion]);

  const handleSubmit = useCallback(() => {
    // Verify all questions answered
    const allAnswered = QUESTION_IDS.every((qid) => answers[qid] !== undefined);
    if (allAnswered) {
      onSubmit(answers);
    }
  }, [answers, onSubmit]);

  const handleCloseAttempt = useCallback(() => {
    const hasAnyAnswer = Object.keys(answers).length > 0;
    if (hasAnyAnswer) {
      setShowConfirmClose(true);
    } else {
      onClose();
    }
  }, [answers, onClose]);

  const progressPercent = ((currentStep + 1) / totalQuestions) * 100;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
      onClick={(e) => { if (e.target === e.currentTarget) handleCloseAttempt(); }}
      onKeyDown={() => {}}
      role="presentation"
    >
      <div
        className="relative w-full max-w-2xl mx-4 bg-white rounded-2xl shadow-xl max-h-[90vh] overflow-y-auto"
        role="dialog"
        aria-modal="true"
        aria-label={t('quiz.questionOf', { current: currentStep + 1, total: totalQuestions })}
      >
        {/* Close button */}
        <button
          onClick={handleCloseAttempt}
          className="absolute top-4 right-4 p-2 text-neutral-400 hover:text-neutral-600 transition-colors cursor-pointer z-10"
          aria-label={t('quiz.cancel')}
        >
          <X className="w-5 h-5" aria-hidden="true" />
        </button>

        {/* Progress bar */}
        <div className="px-6 pt-6 pb-2">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-neutral-500">
              {t('quiz.questionOf', { current: currentStep + 1, total: totalQuestions })}
            </span>
            <span className="text-sm font-semibold text-azure-600">
              {Math.round(progressPercent)}%
            </span>
          </div>
          <div className="w-full h-2 bg-neutral-100 rounded-full overflow-hidden">
            <div
              className="h-full bg-azure-600 rounded-full transition-all duration-300 ease-in-out"
              style={{ width: `${progressPercent}%` }}
            />
          </div>
        </div>

        {/* Question */}
        <div className="px-6 py-6" aria-live="polite">
          <h3 className="text-lg font-heading font-semibold text-black-950 mb-6">
            {t(`quiz.questions.${currentQuestionId}` as Parameters<typeof t>[0])}
          </h3>

          {/* Answer options */}
          <div className="space-y-3">
            {ANSWER_VALUES.map((value) => {
              const answerKey = ANSWER_KEYS[value];
              const isSelected = currentAnswer === value;

              return (
                <button
                  key={value}
                  onClick={() => handleSelectAnswer(value)}
                  className={cn(
                    'w-full text-left px-4 py-3 rounded-xl border-2 transition-all duration-200 cursor-pointer',
                    isSelected
                      ? 'border-azure-600 bg-azure-50 text-azure-700'
                      : 'border-neutral-200 bg-white text-neutral-700 hover:border-azure-300 hover:bg-azure-25'
                  )}
                >
                  <div className="flex items-center gap-3">
                    <div
                      className={cn(
                        'w-5 h-5 rounded-full border-2 shrink-0 flex items-center justify-center transition-colors',
                        isSelected
                          ? 'border-azure-600 bg-azure-600'
                          : 'border-neutral-300'
                      )}
                    >
                      {isSelected && (
                        <div className="w-2 h-2 rounded-full bg-white" />
                      )}
                    </div>
                    <div>
                      <span className="text-sm font-medium">
                        {t(`quiz.answers.${answerKey}` as Parameters<typeof t>[0])}
                      </span>
                    </div>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Navigation */}
        <div className="px-6 pb-6 flex items-center justify-between">
          <button
            onClick={handleBack}
            disabled={isFirstQuestion}
            className={cn(
              'inline-flex items-center gap-2 px-4 py-2.5 text-sm font-medium rounded-lg transition-colors cursor-pointer',
              isFirstQuestion
                ? 'text-neutral-300 cursor-not-allowed'
                : 'text-neutral-600 hover:text-azure-600 hover:bg-azure-50'
            )}
          >
            <ChevronLeft className="w-4 h-4" aria-hidden="true" />
            {t('quiz.back')}
          </button>

          {isLastQuestion ? (
            <button
              onClick={handleSubmit}
              disabled={!hasAnswered || loading}
              className={cn(
                'inline-flex items-center gap-2 px-6 py-2.5 text-sm font-medium rounded-lg transition-colors cursor-pointer',
                !hasAnswered || loading
                  ? 'bg-neutral-100 text-neutral-400 cursor-not-allowed'
                  : 'bg-azure-600 text-white hover:bg-azure-700'
              )}
            >
              {loading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
                  {t('quiz.submitting')}
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" aria-hidden="true" />
                  {t('quiz.submit')}
                </>
              )}
            </button>
          ) : (
            <button
              onClick={handleNext}
              disabled={!hasAnswered}
              className={cn(
                'inline-flex items-center gap-2 px-6 py-2.5 text-sm font-medium rounded-lg transition-colors cursor-pointer',
                !hasAnswered
                  ? 'bg-neutral-100 text-neutral-400 cursor-not-allowed'
                  : 'bg-azure-600 text-white hover:bg-azure-700'
              )}
            >
              {t('quiz.next')}
              <ChevronRight className="w-4 h-4" aria-hidden="true" />
            </button>
          )}
        </div>

        {/* Confirm close dialog */}
        {showConfirmClose && (
          <div className="absolute inset-0 bg-black/30 rounded-2xl flex items-center justify-center z-20">
            <div className="bg-white rounded-xl p-6 mx-4 shadow-lg max-w-sm w-full" role="alertdialog" aria-label={t('quiz.confirmCancel')}>
              <p className="text-sm font-medium text-neutral-900 mb-4">
                {t('quiz.confirmCancel')}
              </p>
              <div className="flex items-center justify-end gap-3">
                <button
                  onClick={() => setShowConfirmClose(false)}
                  className="px-4 py-2 text-sm font-medium text-neutral-600 hover:text-neutral-800 transition-colors cursor-pointer"
                >
                  {t('quiz.back')}
                </button>
                <button
                  onClick={onClose}
                  className="px-4 py-2 text-sm font-medium bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors cursor-pointer"
                >
                  {t('quiz.cancel')}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
