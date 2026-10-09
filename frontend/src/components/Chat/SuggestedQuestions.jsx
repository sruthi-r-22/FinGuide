import React from 'react';
import { HelpCircle, ArrowRight } from 'lucide-react';

export default function SuggestedQuestions({ questions, onSelect }) {
  if (!questions || questions.length === 0) return null;

  return (
    <div className="space-y-2 mt-4 pt-3 border-t border-slate-200/60">
      <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-500 uppercase tracking-wider">
        <HelpCircle className="w-3.5 h-3.5 text-blue-500" />
        <span>Suggested Follow-up Questions</span>
      </div>
      <div className="flex flex-wrap gap-2">
        {questions.map((q, idx) => (
          <button
            key={idx}
            onClick={() => onSelect(q)}
            className="flex items-center gap-2 text-left text-xs bg-white hover:bg-blue-50 text-slate-700 hover:text-blue-700 border border-slate-200 hover:border-blue-300 py-2 px-3 rounded-xl transition-all shadow-2xs hover:shadow-xs group"
          >
            <span>{q}</span>
            <ArrowRight className="w-3 h-3 text-slate-400 group-hover:text-blue-600 shrink-0 transition-transform group-hover:translate-x-0.5" />
          </button>
        ))}
      </div>
    </div>
  );
}
