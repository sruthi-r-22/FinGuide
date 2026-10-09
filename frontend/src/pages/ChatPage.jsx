import React from 'react';
import { useLocation } from 'react-router-dom';
import ChatInterface from '../components/Chat/ChatInterface';

export default function ChatPage() {
  const location = useLocation();
  const initialQuestion = location.state?.question || null;

  return (
    <div className="space-y-4">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Ask FinGuide AI</h1>
          <p className="text-xs sm:text-sm text-slate-500">
            Ask a banking or safety question. Answers cite authenticated official sources when available and say when they cannot be verified.
          </p>
        </div>
      </div>

      <ChatInterface initialQuestion={initialQuestion} />
    </div>
  );
}
