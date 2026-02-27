'use client';

import { useState, useEffect, useCallback } from 'react';
import { X, AlertTriangle, Star } from 'lucide-react';
import { HireConfirmationModalProps } from './HireConfirmationModal.props';

export function HireConfirmationModal({
  proposal,
  onConfirm,
  onCancel,
  tHire,
}: HireConfirmationModalProps) {
  const [hiringNotes, setHiringNotes] = useState('');
  const [confirming, setConfirming] = useState(false);

  const completedCount = proposal.courses.filter((c) => c.is_completed).length;
  const totalCourses = proposal.courses.length;
  const allComplete = completedCount === totalCourses;

  const handleConfirm = async () => {
    setConfirming(true);
    await onConfirm(hiringNotes);
    setConfirming(false);
  };

  const handleKeyDown = useCallback((e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onCancel();
    }
  }, [onCancel]);

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = '';
    };
  }, [handleKeyDown]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      role="dialog"
      aria-modal="true"
      aria-labelledby="hire-modal-title"
    >
      {/* Overlay */}
      <div
        className="absolute inset-0 bg-black/50"
        onClick={onCancel}
      />

      {/* Modal */}
      <div className="relative bg-white rounded-2xl shadow-xl max-w-lg w-full p-6 z-10">
        {/* Close button */}
        <button
          onClick={onCancel}
          className="absolute top-4 right-4 p-1 text-neutral-400 hover:text-neutral-600 transition-colors cursor-pointer"
          aria-label="Chiudi"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Title */}
        <h2 id="hire-modal-title" className="text-xl font-heading font-semibold text-black-950 mb-4">
          {tHire('modalTitle')}
        </h2>

        {/* Talent info */}
        <div className="mb-4">
          <p className="text-base font-medium text-neutral-800">{proposal.talent_name}</p>
          <p className="text-sm text-neutral-500 mt-1">
            {tHire('progress', { completed: completedCount, total: totalCourses })}
          </p>
          <div className="flex items-center gap-1 mt-1">
            <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" aria-hidden="true" />
            <span className="text-sm font-medium text-azure-600">
              {tHire('xpEarned', { xp: proposal.total_xp })}
            </span>
          </div>
        </div>

        {/* Warning if not all courses complete */}
        {!allComplete && (
          <div className="mb-4 p-3 bg-yellow-50 border border-yellow-400/30 rounded-lg flex items-start gap-2">
            <AlertTriangle className="w-5 h-5 text-yellow-500 shrink-0 mt-0.5" aria-hidden="true" />
            <p className="text-sm text-yellow-700">
              {tHire('incompleteWarning', { completed: completedCount, total: totalCourses })}
            </p>
          </div>
        )}

        {/* Hiring notes textarea */}
        <div className="mb-6">
          <label htmlFor="hiring-notes" className="block text-sm font-medium text-neutral-700 mb-1">
            {tHire('notesLabel')}
          </label>
          <textarea
            id="hiring-notes"
            value={hiringNotes}
            onChange={(e) => setHiringNotes(e.target.value)}
            placeholder={tHire('notesPlaceholder')}
            className="w-full p-3 text-sm border border-neutral-200 rounded-xl resize-none focus:outline-none focus:border-azure-400 focus:ring-1 focus:ring-azure-400"
            rows={3}
          />
        </div>

        {/* Actions */}
        <div className="flex items-center gap-3 justify-end">
          <button
            onClick={onCancel}
            className="px-4 py-2 text-sm font-medium text-neutral-600 bg-white border border-neutral-200 rounded-xl hover:bg-neutral-50 transition-colors cursor-pointer"
          >
            {tHire('cancel')}
          </button>
          <button
            onClick={handleConfirm}
            disabled={confirming}
            className="px-4 py-2 text-sm font-medium text-white bg-emerald-500 rounded-xl hover:bg-emerald-600 transition-colors cursor-pointer disabled:opacity-50"
          >
            {tHire('confirm')}
          </button>
        </div>
      </div>
    </div>
  );
}
