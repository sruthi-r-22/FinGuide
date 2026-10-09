import React from 'react';
import { AlertTriangle, ShieldCheck, FileCheck } from 'lucide-react';

export default function StatusBadge({ status, type = 'grounded', hasUnverifiedSources = false }) {
  if (type === 'grounded') {
    return status ? (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
        Supported by Verified Official Source
      </span>
    ) : (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium bg-amber-50 text-amber-700 border border-amber-200">
        <AlertTriangle className="w-3.5 h-3.5 text-amber-500" />
        {hasUnverifiedSources ? 'Unverified sources only' : 'No verified evidence'}
      </span>
    );
  }

  if (type === 'risk') {
    const isCritical = status?.includes('CRITICAL');
    const isElevated = status?.includes('ELEVATED');
    return (
      <span
        className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold ${
          isCritical
            ? 'bg-rose-100 text-rose-800 border border-rose-300'
            : isElevated
            ? 'bg-amber-100 text-amber-800 border border-amber-300'
            : 'bg-emerald-100 text-emerald-800 border border-emerald-300'
        }`}
      >
        {status}
      </span>
    );
  }

  return (
    <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
      <FileCheck className="w-3 h-3 text-slate-500" />
      {status}
    </span>
  );
}
