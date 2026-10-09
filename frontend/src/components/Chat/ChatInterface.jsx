import React, { useState, useRef, useEffect } from 'react';
import { Send, Trash2, RotateCcw, AlertTriangle, Sparkles, ShieldAlert } from 'lucide-react';
import ChatMessage from './ChatMessage';
import LoadingSpinner from '../Common/LoadingSpinner';
import { api } from '../../services/api';

const DEFAULT_WELCOME_MESSAGE = {
  id: 'welcome',
  sender: 'ai',
  text: `### Welcome to FinGuide AI! 👋
I am an educational banking assistant. I use indexed documents only when they are relevant, and identify generated demos or unverified material separately. I present banking rules as official only when they are supported by an authenticated official source.

**How can I help you today?** You can select one of the suggested questions below or type your own.`,
  sources: [],
  is_grounded: false,
  has_warning: false,
  follow_up_questions: [
    "What documents are generally needed to open a savings account?",
    "Explain KYC and CKYC in simple words.",
    "What is the difference between NEFT, RTGS, and IMPS?",
    "How can I recognize a fake KYC message?",
    "What is Aadhaar-based eKYC?"
  ],
  timestamp: 'Ready'
};

export default function ChatInterface({ initialQuestion = null }) {
  const [messages, setMessages] = useState([DEFAULT_WELCOME_MESSAGE]);
  const [inputValue, setInputValue] = useState(initialQuestion || '');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastQuestion, setLastQuestion] = useState('');
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (initialQuestion) {
      handleSend(initialQuestion);
    }
  }, [initialQuestion]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSend = async (questionToSend = null) => {
    const text = (questionToSend || inputValue).trim();
    if (!text || isLoading) return;

    setError(null);
    setLastQuestion(text);
    const userMsg = {
      id: Date.now().toString(),
      sender: 'user',
      text: text,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputValue('');
    setIsLoading(true);

    try {
      // Build lightweight conversation history
      const history = messages.slice(-4).map((m) => ({
        role: m.sender === 'user' ? 'user' : 'assistant',
        content: m.text,
      }));

      const res = await api.askQuestion(text, history);

      const aiMsg = {
        id: (Date.now() + 1).toString(),
        sender: 'ai',
        text: res.answer,
        sources: res.sources || [],
        further_reading: res.further_reading || [],
        is_grounded: res.is_grounded,
        has_warning: res.has_warning,
        warning_message: res.warning_message,
        follow_up_questions: res.follow_up_questions || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      console.error('Chat error:', err);
      const errMsg = err.response?.data?.detail || 'Failed to reach FinGuide backend. Please ensure the server is running.';
      setError(errMsg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleClearChat = () => {
    setMessages([DEFAULT_WELCOME_MESSAGE]);
    setError(null);
  };

  const handleRetry = () => {
    if (lastQuestion) {
      handleSend(lastQuestion);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-140px)] sm:h-[calc(100vh-130px)] max-w-5xl mx-auto bg-slate-50/50 rounded-2xl border border-slate-200/90 shadow-xs overflow-hidden">
      {/* Top Banner / Controls */}
      <div className="bg-white px-4 sm:px-6 py-3 border-b border-slate-200/80 flex items-center justify-between gap-4">
        <div className="flex items-center gap-2 text-xs text-slate-600">
          <div className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />
          <span className="font-semibold text-slate-800">FinGuide RAG Session</span>
          <span className="hidden sm:inline text-slate-400">| Official-source verification required</span>
        </div>

        <button
          onClick={handleClearChat}
          className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 hover:text-rose-600 hover:bg-rose-50 rounded-lg transition-colors border border-slate-200 hover:border-rose-200"
          title="Clear conversation"
        >
          <Trash2 className="w-3.5 h-3.5" />
          <span>Clear Chat</span>
        </button>
      </div>

      {/* Security alert header banner */}
      <div className="px-4 sm:px-6 py-2 bg-amber-50/90 border-b border-amber-200/70 text-[11px] text-amber-900 flex items-center gap-2">
        <ShieldAlert className="w-4 h-4 text-amber-600 shrink-0" />
        <p className="truncate">
          <b>Safe Banking Warning:</b> Never enter actual passwords, OTPs, UPI PINs, or 16-digit debit card numbers here.
        </p>
      </div>

      {/* Messages stream */}
      <div className="flex-1 overflow-y-auto p-4 sm:p-6 space-y-2">
        {messages.map((msg) => (
          <ChatMessage
            key={msg.id}
            message={msg}
            onSelectQuestion={(q) => handleSend(q)}
          />
        ))}

        {isLoading && (
          <div className="flex items-start gap-3 animate-fade-in">
            <div className="w-9 h-9 rounded-xl bg-slate-900 flex items-center justify-center text-white shrink-0">
              <Sparkles className="w-4 h-4 text-blue-400 animate-spin" />
            </div>
            <div className="bg-white border border-slate-200 p-4 rounded-2xl rounded-tl-xs shadow-xs">
              <LoadingSpinner size="sm" text="Searching relevant indexed documents and checking source provenance..." />
            </div>
          </div>
        )}

        {error && (
          <div className="p-4 bg-rose-50 border border-rose-200 rounded-2xl text-rose-800 text-xs flex items-center justify-between gap-3 animate-fade-in">
            <div className="flex items-center gap-2">
              <AlertTriangle className="w-4 h-4 text-rose-600 shrink-0" />
              <span>{error}</span>
            </div>
            <button
              onClick={handleRetry}
              className="flex items-center gap-1 px-3 py-1 bg-white hover:bg-rose-100 border border-rose-300 rounded-lg font-medium text-rose-700 transition-colors"
            >
              <RotateCcw className="w-3 h-3" />
              <span>Retry</span>
            </button>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="bg-white border-t border-slate-200 p-3 sm:p-4">
        <div className="relative flex items-center">
          <textarea
            ref={inputRef}
            rows={2}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask any banking procedure, KYC, payment, or scam question (e.g., 'What is Aadhaar eKYC?')..."
            className="w-full resize-none rounded-xl border border-slate-300 pl-4 pr-24 py-3 text-sm text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent transition-all shadow-inner"
            disabled={isLoading}
          />
          <button
            onClick={() => handleSend()}
            disabled={!inputValue.trim() || isLoading}
            className="absolute right-3 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-300 text-white rounded-lg text-xs font-semibold flex items-center gap-1.5 shadow-sm transition-all cursor-pointer disabled:cursor-not-allowed"
          >
            <span>Ask</span>
            <Send className="w-3.5 h-3.5" />
          </button>
        </div>
        <div className="flex items-center justify-between mt-2 px-1 text-[11px] text-slate-400">
          <span>Press Enter to send, Shift+Enter for new line</span>
          <span>Grounded Retrieval • Anti-Hallucination Safe</span>
        </div>
      </div>
    </div>
  );
}
