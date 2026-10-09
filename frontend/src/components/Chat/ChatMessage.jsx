import React from 'react';
import ReactMarkdown from 'react-markdown';
import { Bot, User, FileText, AlertCircle } from 'lucide-react';
import SourceBadge from './SourceBadge';
import StatusBadge from '../Common/StatusBadge';
import SuggestedQuestions from './SuggestedQuestions';

export default function ChatMessage({ message, onSelectQuestion }) {
  const isUser = message.sender === 'user';

  if (isUser) {
    return (
      <div className="flex justify-end gap-3 mb-6">
        <div className="max-w-[85%] sm:max-w-[75%] rounded-2xl rounded-tr-xs bg-blue-600 text-white p-4 shadow-sm">
          <p className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap">{message.text}</p>
          <span className="block text-[10px] text-blue-200 text-right mt-1.5">
            {message.timestamp || 'Just now'}
          </span>
        </div>
        <div className="w-9 h-9 rounded-xl bg-blue-100 border border-blue-200 flex items-center justify-center shrink-0 text-blue-700">
          <User className="w-5 h-5" />
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-start gap-3 mb-6 animate-fade-in">
      <div className="w-9 h-9 rounded-xl bg-slate-900 border border-slate-800 flex items-center justify-center shrink-0 text-white shadow-sm mt-0.5">
        <Bot className="w-5 h-5 text-blue-400" />
      </div>

      <div className="max-w-[95%] sm:max-w-[85%] bg-white rounded-2xl rounded-tl-xs border border-slate-200 p-5 shadow-xs">
        {/* Header: Grounded status indicator */}
        <div className="flex items-center justify-between pb-3 mb-3 border-b border-slate-100 text-xs">
          <div className="flex items-center gap-2">
            <span className="font-bold text-slate-800">FinGuide Assistant</span>
            <StatusBadge
              status={message.is_grounded}
              type="grounded"
              hasUnverifiedSources={(message.sources || []).some(
                (source) => source.content_type !== 'official_document'
                  || source.reference_status !== 'verified'
                  || source.verification_method !== 'manual_origin_and_sha256_review'
              )}
            />
          </div>
          <span className="text-[11px] text-slate-400">{message.timestamp || 'Just now'}</span>
        </div>

        {/* Security Warning if any */}
        {message.has_warning && message.warning_message && (
          <div className="mb-4 p-3 bg-amber-50 border border-amber-200 rounded-xl text-xs text-amber-900 flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
            <p className="leading-relaxed">{message.warning_message}</p>
          </div>
        )}

        {/* Answer Content rendered with Markdown */}
        <div className="prose prose-sm prose-slate max-w-none text-slate-800 leading-relaxed text-sm sm:text-base space-y-2 [&_h3]:text-base [&_h3]:font-bold [&_h3]:text-slate-900 [&_h3]:mt-3 [&_h3]:mb-1 [&_h4]:text-sm [&_h4]:font-semibold [&_h4]:text-slate-800 [&_h4]:mt-2 [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:list-decimal [&_ol]:pl-5 [&_li]:my-1 [&_blockquote]:border-l-4 [&_blockquote]:border-blue-400 [&_blockquote]:bg-slate-50 [&_blockquote]:py-1.5 [&_blockquote]:px-3 [&_blockquote]:rounded-r-lg [&_blockquote]:text-slate-600 [&_blockquote]:italic">
          <ReactMarkdown>{message.text}</ReactMarkdown>
        </div>

        {/* Source Citations */}
        {message.sources && message.sources.length > 0 && (
          <div className="mt-5 pt-4 border-t border-slate-100">
            <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2.5">
              <FileText className="w-4 h-4 text-slate-500" />
              <span>Retrieved Sources ({message.sources.length})</span>
            </div>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
              {message.sources.map((src, i) => (
                <SourceBadge key={i} source={src} />
              ))}
            </div>
          </div>
        )}

        {/* Follow up suggestions */}
        {message.follow_up_questions && message.follow_up_questions.length > 0 && (
          <SuggestedQuestions
            questions={message.follow_up_questions}
            onSelect={onSelectQuestion}
          />
        )}
      </div>
    </div>
  );
}
