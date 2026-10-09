import React, { useState, useEffect } from 'react';
import {
  ClipboardCheck,
  Download,
  Building2,
  FileCheck2,
  ExternalLink,
  ShieldCheck,
  AlertCircle,
  HelpCircle,
  Sparkles
} from 'lucide-react';
import { api } from '../services/api';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import DisclaimerBanner from '../components/Common/DisclaimerBanner';

const TASKS = [
  { id: 'savings_account', label: 'Opening a Savings Account' },
  { id: 'current_account', label: 'Opening a Current Account (Business)' },
  { id: 'kyc_requirements', label: 'Understanding KYC Requirements' },
  { id: 'kyc_update', label: 'Updating KYC Details' },
  { id: 'digital_banking', label: 'Digital Banking Registration (UPI / Net Banking)' },
];

const BANKS = [
  { id: '', label: 'General Regulatory Framework (All Banks)' },
  { id: 'sbi', label: 'State Bank of India (SBI)' },
];

export default function ChecklistPage() {
  const [selectedTask, setSelectedTask] = useState('savings_account');
  const [selectedBank, setSelectedBank] = useState('');
  const [checklist, setChecklist] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchChecklist();
  }, [selectedTask, selectedBank]);

  const fetchChecklist = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getChecklist(selectedTask, selectedBank || null);
      setChecklist(data);
    } catch (err) {
      console.error(err);
      setError('Failed to generate document checklist. Please verify backend connection.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleDownloadPdf = async () => {
    setIsDownloading(true);
    try {
      await api.downloadChecklistPdf(selectedTask, selectedBank || null);
    } catch (err) {
      console.error('PDF download error:', err);
      alert('Failed to generate PDF. Please ensure backend is running.');
    } finally {
      setIsDownloading(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 mb-1">
            <div className="p-2 rounded-xl bg-emerald-50 border border-emerald-200 text-emerald-600">
              <ClipboardCheck className="w-5 h-5" />
            </div>
            <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Document Checklist Generator</h1>
          </div>
          <p className="text-xs sm:text-sm text-slate-500">
            Source-backed banking documentation requirements verified against RBI directions and bank charters.
          </p>
        </div>

        {checklist && (
          <button
            onClick={handleDownloadPdf}
            disabled={isDownloading}
            className="flex items-center justify-center gap-2 px-4 py-2.5 rounded-xl bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-300 text-white font-semibold text-xs sm:text-sm shadow-md transition-all cursor-pointer shrink-0"
          >
            <Download className="w-4 h-4" />
            <span>{isDownloading ? 'Generating PDF...' : 'Download Checklist (PDF)'}</span>
          </button>
        )}
      </div>

      {/* Task & Bank Selectors */}
      <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
            1. Select Banking Task
          </label>
          <select
            value={selectedTask}
            onChange={(e) => setSelectedTask(e.target.value)}
            className="w-full p-2.5 rounded-xl border border-slate-300 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            {TASKS.map((t) => (
              <option key={t.id} value={t.id}>
                {t.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-xs font-bold uppercase tracking-wider text-slate-500 mb-2">
            2. Target Institution (Optional)
          </label>
          <select
            value={selectedBank}
            onChange={(e) => setSelectedBank(e.target.value)}
            className="w-full p-2.5 rounded-xl border border-slate-300 text-sm font-medium text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600"
          >
            {BANKS.map((b) => (
              <option key={b.id} value={b.id}>
                {b.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Checklist Content */}
      {isLoading ? (
        <LoadingSpinner text="Preparing educational document checklist..." />
      ) : error ? (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-2xl text-xs">
          {error}
        </div>
      ) : checklist ? (
        <div className="space-y-4">
          <div className="flex items-center justify-between bg-slate-900 text-white px-5 py-3.5 rounded-2xl shadow-sm">
            <div>
              <h2 className="text-sm sm:text-base font-bold">{checklist.task_title}</h2>
              <p className="text-[11px] text-slate-400">
                {checklist.items.length} general checklist items. Confirm current requirements with your institution.
              </p>
            </div>
            <span className="text-[11px] font-semibold px-2.5 py-1 rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">
              Educational Guidance
            </span>
          </div>

          <div className="space-y-3">
            {checklist.items.map((item, index) => (
              <div
                key={index}
                className="bg-white rounded-2xl border border-slate-200 p-5 hover:border-slate-300 shadow-2xs transition-all space-y-3"
              >
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-2">
                  <div className="flex items-start gap-3">
                    <div className="w-7 h-7 rounded-lg bg-blue-50 text-blue-700 font-bold text-xs flex items-center justify-center shrink-0 border border-blue-200 mt-0.5">
                      {index + 1}
                    </div>
                    <div>
                      <h3 className="text-base font-bold text-slate-900">{item.requirement}</h3>
                      <span className="inline-block mt-1 text-[11px] font-semibold text-slate-500 bg-slate-100 px-2 py-0.5 rounded-md">
                        {item.category}
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center gap-2 sm:self-start">
                    <span
                      className={`text-[11px] font-semibold px-2.5 py-1 rounded-full ${
                        item.is_bank_dependent
                          ? 'bg-amber-50 text-amber-800 border border-amber-200'
                          : 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                      }`}
                    >
                      {item.verified_status}
                    </span>
                  </div>
                </div>

                <div className="text-xs sm:text-sm text-slate-600 bg-slate-50 p-3 rounded-xl border border-slate-200/80 leading-relaxed">
                  <span className="font-semibold text-slate-800 block mb-0.5">Why this is required:</span>
                  {item.why_needed}
                </div>

                <div className="flex flex-col sm:flex-row sm:items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-100 gap-1">
                  <span className="font-medium text-slate-600">
                    Authority / Reference: {item.source_document}
                  </span>
                  {item.source_url && (
                    <a
                      href={item.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-800 font-semibold inline-flex items-center gap-1"
                    >
                      <span>Official Source Link</span>
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>

          <DisclaimerBanner message={checklist.disclaimer} />
        </div>
      ) : null}
    </div>
  );
}
