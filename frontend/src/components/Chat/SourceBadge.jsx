import React, { useState } from 'react';
import { ExternalLink, ChevronDown, ChevronUp, FileText } from 'lucide-react';
import {
  getSourceTrustLabel,
  isGeneratedDemo,
  isVerifiedOfficialSource,
} from '../../utils/sourceProvenance';

export default function SourceBadge({ source }) {
  const [expanded, setExpanded] = useState(false);
  const isDemo = isGeneratedDemo(source);
  const isOfficial = isVerifiedOfficialSource(source);
  const provenanceLabel = getSourceTrustLabel(source);

  return (
    <div className="bg-slate-50 border border-slate-200/90 rounded-xl p-3 text-xs transition-all hover:border-blue-300">
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 font-medium text-slate-800">
          <FileText className="w-4 h-4 text-blue-600 shrink-0" />
          <span className="truncate max-w-[260px] sm:max-w-md font-semibold">
            {source.document_title || 'Unknown source'}
          </span>
          <span className={`px-1.5 py-0.5 rounded font-bold text-[10px] ${isDemo ? 'bg-amber-100 text-amber-800' : isOfficial ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-700'}`}>
            {isDemo
              ? 'UNVERIFIED DEMO'
              : isOfficial
                ? 'OFFICIAL'
                : source.reference_status === 'unverified'
                  ? 'UNVERIFIED'
                  : 'UNKNOWN'}
          </span>
          {source.page_number && (
            <span className="px-1.5 py-0.5 rounded bg-blue-100 text-blue-800 font-bold text-[10px]">
              Page {source.page_number}
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          {isOfficial && source.source_url && (
            <a
              href={source.source_url}
              target="_blank"
              rel="noopener noreferrer"
              className="p-1 text-slate-500 hover:text-blue-600 rounded-md transition-colors"
              title={source.reference_status === 'verified' ? 'Open verified source' : 'Open unverified reference link'}
            >
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          )}
          <button
            onClick={() => setExpanded(!expanded)}
            className="p-1 text-slate-500 hover:text-slate-800 rounded-md transition-colors"
            title={expanded ? "Hide snippet" : "Show citation excerpt"}
          >
            {expanded ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>
      </div>

      {expanded && (
        <div className="mt-2.5 pt-2.5 border-t border-slate-200/80 text-slate-600 space-y-1.5 animate-fade-in">
          <p className={`font-semibold ${isDemo ? 'text-amber-800' : isOfficial ? 'text-emerald-800' : 'text-slate-700'}`}>
            {provenanceLabel}
          </p>
          <p><b>Publisher:</b> {source.publisher || 'Unknown'}</p>
          <p><b>Issuing organization:</b> {source.authority || 'Unknown'}</p>
          <p><b>Published:</b> {source.published_date || 'Unknown'}</p>
          {source.provenance_note && <p>{source.provenance_note}</p>}
          {isOfficial && source.snippet && (
            <p className="italic text-[11px] leading-relaxed bg-white p-2 rounded-lg border border-slate-200">
              "{source.snippet}"
            </p>
          )}
          <div className="flex items-center justify-between text-[10px] text-slate-400 pt-1">
            <span>Last verified: {source.last_verified || 'Unknown / not verified'}</span>
            {source.relevance_score != null && (
              <span>Relevance: {Math.round(source.relevance_score * 100)}%</span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
