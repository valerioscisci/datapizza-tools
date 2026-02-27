export interface ChatSectionProps {
  proposalId: string;
  accessToken: string;
  currentUserId: string;
  currentUserType: 'company' | 'talent';
  proposalStatus: string;
}
