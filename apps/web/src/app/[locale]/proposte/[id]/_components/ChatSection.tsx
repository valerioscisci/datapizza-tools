'use client';

import { useTranslations } from 'next-intl';
import { useState, useEffect, useRef, useCallback } from 'react';
import { MessageCircle, Send, Loader2 } from 'lucide-react';
import { API_BASE, type ChatMessage, type ChatMessagesResponse } from '../../_utils/constants';
import { ChatSectionProps } from './ChatSection.props';

export function ChatSection({
  proposalId,
  accessToken,
  currentUserId,
  currentUserType,
  proposalStatus,
}: ChatSectionProps) {
  const t = useTranslations('proposals.chat');

  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(true);
  const [newMessage, setNewMessage] = useState('');
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const chatContainerRef = useRef<HTMLDivElement>(null);

  const chatEnabled = ['accepted', 'completed', 'hired'].includes(proposalStatus);

  const fetchMessages = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/v1/proposals/${proposalId}/messages?page=1&page_size=50`, {
        headers: { Authorization: `Bearer ${accessToken}` },
      });
      if (res.ok) {
        const data: ChatMessagesResponse = await res.json();
        setMessages(data.items);
      }
    } catch {
      // Silently fail
    } finally {
      setLoading(false);
    }
  }, [proposalId, accessToken]);

  useEffect(() => {
    if (chatEnabled) {
      fetchMessages();
    } else {
      setLoading(false);
    }
  }, [chatEnabled, fetchMessages]);

  // Polling every 10 seconds
  useEffect(() => {
    if (!chatEnabled) return;
    const interval = setInterval(fetchMessages, 10000);
    return () => clearInterval(interval);
  }, [chatEnabled, fetchMessages]);

  // Auto-scroll on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!newMessage.trim() || sending) return;
    setSending(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/proposals/${proposalId}/messages`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content: newMessage.trim() }),
      });
      if (res.ok) {
        setNewMessage('');
        await fetchMessages();
      }
    } catch {
      // Silently fail
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const formatTime = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString('it-IT', { hour: '2-digit', minute: '2-digit' });
  };

  const formatDay = (dateStr: string): string => {
    const date = new Date(dateStr);
    return date.toLocaleDateString('it-IT', { day: '2-digit', month: '2-digit', year: 'numeric' });
  };

  return (
    <div className="mt-8">
      <div className="flex items-center gap-2 mb-4">
        <MessageCircle className="w-5 h-5 text-azure-600" aria-hidden="true" />
        <h2 className="text-lg font-heading font-semibold text-black-950">{t('title')}</h2>
      </div>

      {!chatEnabled ? (
        <div className="p-6 bg-neutral-50 rounded-2xl border border-neutral-200 text-center">
          <p className="text-sm text-neutral-500">{t('unavailable')}</p>
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-neutral-200 overflow-hidden">
          {/* Messages area */}
          <div
            ref={chatContainerRef}
            className="h-80 overflow-y-auto p-4 space-y-3"
          >
            {loading ? (
              <div className="flex items-center justify-center h-full">
                <Loader2 className="w-5 h-5 animate-spin text-neutral-400" aria-hidden="true" />
              </div>
            ) : messages.length === 0 ? (
              <div className="flex items-center justify-center h-full">
                <p className="text-sm text-neutral-400">{t('empty')}</p>
              </div>
            ) : (
              messages.map((msg, idx) => {
                const isCurrentUser = msg.sender_id === currentUserId;
                const prevMessage = idx > 0 ? messages[idx - 1] : null;
                const showDate = idx === 0 || (prevMessage != null && formatDay(msg.created_at) !== formatDay(prevMessage.created_at));

                return (
                  <div key={msg.id}>
                    {showDate && (
                      <div className="text-center my-2">
                        <span className="text-xs text-neutral-400 bg-neutral-50 px-2 py-0.5 rounded-full">
                          {formatDay(msg.created_at)}
                        </span>
                      </div>
                    )}
                    <div className={`flex ${isCurrentUser ? 'justify-end' : 'justify-start'}`}>
                      <div className={`max-w-xs sm:max-w-sm ${isCurrentUser ? 'items-end' : 'items-start'}`}>
                        <p className={`text-xs mb-0.5 ${isCurrentUser ? 'text-right text-azure-400' : 'text-left text-neutral-400'}`}>
                          {msg.sender_name}
                        </p>
                        <div
                          className={`px-3 py-2 rounded-2xl ${
                            isCurrentUser
                              ? 'bg-azure-600 text-white rounded-br-sm'
                              : 'bg-neutral-100 text-black-950 rounded-bl-sm'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                        </div>
                        <p className={`text-xs mt-0.5 ${isCurrentUser ? 'text-right text-neutral-300' : 'text-left text-neutral-300'}`}>
                          {formatTime(msg.created_at)}
                        </p>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input area */}
          <div className="border-t border-neutral-200 p-3 flex items-center gap-2">
            <input
              type="text"
              value={newMessage}
              onChange={(e) => setNewMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={t('placeholder')}
              className="flex-1 px-3 py-2 text-sm border border-neutral-200 rounded-xl focus:outline-none focus:border-azure-400 focus:ring-1 focus:ring-azure-400"
              disabled={sending}
            />
            <button
              onClick={handleSend}
              disabled={sending || !newMessage.trim()}
              className="p-2.5 bg-azure-600 text-white rounded-xl hover:bg-azure-700 transition-colors cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label={t('send')}
            >
              {sending ? (
                <Loader2 className="w-4 h-4 animate-spin" aria-hidden="true" />
              ) : (
                <Send className="w-4 h-4" aria-hidden="true" />
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
