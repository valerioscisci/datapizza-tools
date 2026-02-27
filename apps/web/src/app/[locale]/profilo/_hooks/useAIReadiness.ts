'use client';

import { useState, useCallback, useEffect } from 'react';
import { useAuth } from '@/lib/auth/use-auth';
import { API_BASE } from '../_utils/constants';
import type { AIReadinessResult, SuggestionsResult, QuizMeta } from '../_utils/constants';

interface UseAIReadinessReturn {
  readiness: AIReadinessResult | null;
  suggestions: SuggestionsResult | null;
  quizMeta: QuizMeta | null;
  loading: boolean;
  error: string | null;
  submitQuiz: (answers: Record<string, number>) => Promise<void>;
  loadSuggestions: () => Promise<void>;
  loadQuizMeta: () => Promise<void>;
}

export function useAIReadiness(): UseAIReadinessReturn {
  const { accessToken, isAuthenticated } = useAuth();
  const [readiness, setReadiness] = useState<AIReadinessResult | null>(null);
  const [suggestions, setSuggestions] = useState<SuggestionsResult | null>(null);
  const [quizMeta, setQuizMeta] = useState<QuizMeta | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadCachedAssessment = useCallback(async () => {
    if (!accessToken) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/profile/ai-readiness`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) return; // 404 means no assessment yet
      const data: AIReadinessResult = await res.json();
      setReadiness(data);
    } catch {
      // Silently ignore cache load failures
    }
  }, [accessToken]);

  const loadSuggestions = useCallback(async () => {
    if (!accessToken) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/profile/ai-readiness/suggestions`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) return;
      const data: SuggestionsResult = await res.json();
      setSuggestions(data);
    } catch {
      // Silently ignore suggestion load failures
    }
  }, [accessToken]);

  const loadQuizMeta = useCallback(async () => {
    if (!accessToken) return;
    try {
      const res = await fetch(`${API_BASE}/api/v1/profile/ai-readiness/quiz`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (!res.ok) return;
      const data: QuizMeta = await res.json();
      setQuizMeta(data);
    } catch {
      // Silently ignore quiz meta load failures
    }
  }, [accessToken]);

  const submitQuiz = useCallback(async (answers: Record<string, number>) => {
    if (!accessToken) return;
    setLoading(true);
    setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/v1/profile/ai-readiness`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ answers }),
      });
      if (!res.ok) {
        throw new Error(`API error: ${res.status}`);
      }
      const data: AIReadinessResult = await res.json();
      setReadiness(data);
      // Load suggestions after submitting quiz
      await loadSuggestions();
    } catch {
      setError('error');
    } finally {
      setLoading(false);
    }
  }, [accessToken, loadSuggestions]);

  // On mount: load cached assessment and suggestions
  useEffect(() => {
    if (isAuthenticated && accessToken) {
      loadCachedAssessment().then(() => {
        loadSuggestions();
      });
    }
  }, [isAuthenticated, accessToken, loadCachedAssessment, loadSuggestions]);

  return {
    readiness,
    suggestions,
    quizMeta,
    loading,
    error,
    submitQuiz,
    loadSuggestions,
    loadQuizMeta,
  };
}
