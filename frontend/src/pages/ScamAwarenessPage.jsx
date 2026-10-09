import React, { useState, useEffect } from 'react';
import {
  ShieldAlert,
  AlertTriangle,
  CheckCircle2,
  PhoneCall,
  ExternalLink,
  ShieldCheck,
  Search,
  Sparkles,
  Info
} from 'lucide-react';
import { api } from '../services/api';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import StatusBadge from '../components/Common/StatusBadge';
import DisclaimerBanner from '../components/Common/DisclaimerBanner';

export default function ScamAwarenessPage() {
  const [samples, setSamples] = useState([]);
  const [selectedSample, setSelectedSample] = useState(null);
  const [messageInput, setMessageInput] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSamples();
  }, []);

  const fetchSamples = async () => {
    try {
      const data = await api.getScamSamples();
      setSamples(data);
      if (data && data.length > 0) {
        selectScenario(data[0]);
      }
    } catch (err) {
      console.error(err);
    }
  };

  const selectScenario = (scenario) => {
    setSelectedSample(scenario);
    setMessageInput(scenario.message_text);
    setAnalysis(null);
    setError(null);
  };

  const handleAnalyze = async () => {
    if (!messageInput.trim() || isLoading) return;
    setIsLoading(true);
    setError(null);
    try {
      const res = await api.analyzeScam(
        messageInput.trim(),
        selectedSample?.scenario_type || null
      );
      setAnalysis(res);
    } catch (err) {
      console.error(err);
      setError(
        err.response?.data?.detail ||
          'Failed to analyze message. Ensure backend is running and no personal credentials were submitted.'
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Page Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <div className="p-2 rounded-xl bg-rose-50 border border-rose-200 text-rose-600">
            <ShieldAlert className="w-5 h-5" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Spot the Scam</h1>
        </div>
        <p className="text-xs sm:text-sm text-slate-500">
          Learn how to recognize online financial fraud, phishing SMS messages, fake bank support calls, and fraudulent UPI collect requests.
        </p>
      </div>

      {/* Safety input warning banner */}
      <DisclaimerBanner
        variant="warning"
        message="Privacy & Safety Notice: Fictional and educational analysis only. Never enter real account numbers, active passwords, phone numbers, or received OTPs into any test tool."
      />

      {/* Main Analysis Section */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left Side: Fictional Sample Scenarios */}
        <div className="lg:col-span-5 space-y-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-3">
            <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500">
              1. Choose an Educational Example
            </h2>
            <div className="space-y-2">
              {samples.map((scenario) => {
                const isSelected = selectedSample?.id === scenario.id;
                return (
                  <div
                    key={scenario.id}
                    onClick={() => selectScenario(scenario)}
                    className={`p-3.5 rounded-xl border text-left cursor-pointer transition-all ${
                      isSelected
                        ? 'bg-blue-50/80 border-blue-400 shadow-xs'
                        : 'bg-slate-50/60 border-slate-200 hover:bg-slate-100 hover:border-slate-300'
                    }`}
                  >
                    <div className="flex items-center justify-between gap-2 mb-1">
                      <span className="font-semibold text-xs sm:text-sm text-slate-800">
                        {scenario.title}
                      </span>
                      <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-200 text-slate-700">
                        {scenario.scenario_type}
                      </span>
                    </div>
                    <p className="text-xs text-slate-500 line-clamp-1">{scenario.description}</p>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Side: Message Inspector & Analysis */}
        <div className="lg:col-span-7 space-y-4">
          <div className="bg-white p-5 rounded-2xl border border-slate-200 shadow-xs space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold uppercase tracking-wider text-slate-500">
                2. Message / Call Script to Analyze
              </h2>
              {selectedSample && (
                <span className="text-xs font-semibold text-blue-600">
                  {selectedSample.scenario_type}
                </span>
              )}
            </div>

            <textarea
              rows={4}
              value={messageInput}
              onChange={(e) => setMessageInput(e.target.value)}
              placeholder="Paste or edit a suspicious banking communication snippet..."
              className="w-full p-3.5 rounded-xl border border-slate-300 text-xs sm:text-sm text-slate-800 font-mono leading-relaxed focus:outline-none focus:ring-2 focus:ring-blue-600"
            />

            <div className="flex items-center justify-between pt-1">
              <span className="text-[11px] text-slate-400">
                Safe static sandbox: links will not be opened
              </span>
              <button
                onClick={handleAnalyze}
                disabled={!messageInput.trim() || isLoading}
                className="px-5 py-2.5 rounded-xl bg-rose-600 hover:bg-rose-700 disabled:bg-slate-300 text-white font-semibold text-xs sm:text-sm shadow-md transition-all cursor-pointer shrink-0 flex items-center gap-1.5"
              >
                <ShieldAlert className="w-4 h-4" />
                <span>{isLoading ? 'Analyzing Signs...' : 'Analyze Message'}</span>
              </button>
            </div>
          </div>

          {/* Analysis Results Display */}
          {isLoading ? (
            <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-xs">
              <LoadingSpinner text="Scanning message for fraud heuristics and deception triggers..." />
            </div>
          ) : error ? (
            <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-2xl text-xs">
              {error}
            </div>
          ) : analysis ? (
            <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm space-y-5 animate-fade-in">
              {/* Header Risk Assessment */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-4 border-b border-slate-100">
                <div>
                  <h3 className="text-base font-bold text-slate-900">Safety Analysis Results</h3>
                  <p className="text-xs text-slate-500">Heuristic pattern detection summary</p>
                </div>
                <StatusBadge status={analysis.risk_level} type="risk" />
              </div>

              {/* Warning Signs */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-rose-700 flex items-center gap-1.5">
                  <AlertTriangle className="w-4 h-4 text-rose-600" />
                  <span>Potential Warning Signs Detected ({analysis.potential_warning_signs.length})</span>
                </h4>
                <div className="space-y-1.5">
                  {analysis.potential_warning_signs.map((sign, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-xl bg-rose-50/80 border border-rose-200 text-xs text-rose-900 flex items-start gap-2"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-rose-600 mt-1.5 shrink-0" />
                      <span>{sign}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Why Suspicious */}
              <div className="bg-slate-50 p-4 rounded-xl border border-slate-200/80 text-xs sm:text-sm text-slate-700 space-y-1 leading-relaxed">
                <span className="font-bold text-slate-900 block">Why this communication is suspicious:</span>
                <p>{analysis.why_suspicious}</p>
              </div>

              {/* Safe Actions */}
              <div className="space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-emerald-800 flex items-center gap-1.5">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  <span>Recommended Safe Actions</span>
                </h4>
                <div className="space-y-1.5">
                  {analysis.safe_actions.map((act, idx) => (
                    <div
                      key={idx}
                      className="p-2.5 rounded-xl bg-emerald-50/70 border border-emerald-200 text-xs text-emerald-950 flex items-start gap-2"
                    >
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 mt-1.5 shrink-0" />
                      <span>{act}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Official Safety Resources */}
              <div className="pt-4 border-t border-slate-100 space-y-2">
                <h4 className="text-xs font-bold uppercase tracking-wider text-slate-500">
                  Official Fraud Helplines & Reporting Portals
                </h4>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs">
                  {analysis.official_safety_resources.map((res, idx) => (
                    <div key={idx} className="p-3 rounded-xl bg-slate-50 border border-slate-200 space-y-1">
                      <span className="font-bold text-slate-800 block">{res.name}</span>
                      <p className="font-semibold text-blue-700 text-[11px]">{res.contact_or_url}</p>
                      <p className="text-slate-500 text-[10px] leading-normal">{res.description}</p>
                    </div>
                  ))}
                </div>
              </div>

              <div className="p-3 bg-slate-100 rounded-xl text-[11px] text-slate-500 italic">
                {analysis.disclaimer}
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
