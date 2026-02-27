export interface AIReadinessQuizProps {
  onSubmit: (answers: Record<string, number>) => void;
  onClose: () => void;
  loading: boolean;
}
