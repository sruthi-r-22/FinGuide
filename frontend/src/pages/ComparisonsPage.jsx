import React, { useState, useEffect } from 'react';
import { Scale, ExternalLink, ShieldCheck, CheckCircle2, Info } from 'lucide-react';
import { api } from '../services/api';
import LoadingSpinner from '../components/Common/LoadingSpinner';
import DisclaimerBanner from '../components/Common/DisclaimerBanner';

const COMPARISON_TOPICS = [
  { id: 'neft-rtgs-imps', label: 'NEFT vs RTGS vs IMPS' },
  { id: 'upi-vs-netbanking', label: 'UPI vs Internet Banking' },
  { id: 'savings-vs-current', label: 'Savings vs Current Account' },
  { id: 'debit-vs-credit', label: 'Debit Card vs Credit Card' },
];

export default function ComparisonsPage() {
  const [selectedTopic, setSelectedTopic] = useState('neft-rtgs-imps');
  const [comparison, setComparison] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTopicData(selectedTopic);
  }, [selectedTopic]);

  const fetchTopicData = async (topicId) => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.getComparisonTopic(topicId);
      setComparison(data);
    } catch (err) {
      console.error(err);
      setError('Failed to load comparison data. Please check backend connection.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <div className="p-2 rounded-xl bg-sky-50 border border-sky-200 text-sky-600">
            <Scale className="w-5 h-5" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Banking Comparisons Explainer</h1>
        </div>
        <p className="text-xs sm:text-sm text-slate-500">
          Educational side-by-side comparisons. Check linked RBI, NPCI, or bank publications for current official rules and terms.
        </p>
      </div>

      {/* Topic Switcher Pills */}
      <div className="flex flex-wrap gap-2 p-1.5 bg-slate-100 rounded-2xl w-fit">
        {COMPARISON_TOPICS.map((t) => (
          <button
            key={t.id}
            onClick={() => setSelectedTopic(t.id)}
            className={`px-4 py-2 rounded-xl text-xs sm:text-sm font-semibold transition-all cursor-pointer ${
              selectedTopic === t.id
                ? 'bg-white text-blue-700 shadow-xs border border-slate-200'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Main Comparison Area */}
      {isLoading ? (
        <LoadingSpinner text="Retrieving official comparative frameworks..." />
      ) : error ? (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-2xl text-xs">
          {error}
        </div>
      ) : comparison ? (
        <div className="space-y-6">
          {/* Header Card */}
          <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-2">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-bold text-slate-900">{comparison.title}</h2>
              <span className="text-[10px] font-bold uppercase px-2.5 py-0.5 rounded-full bg-blue-50 text-blue-700 border border-blue-200">
                Neutral Comparison
              </span>
            </div>
            <p className="text-xs sm:text-sm text-slate-600 leading-relaxed">
              {comparison.description}
            </p>
          </div>

          {/* Table Container with Horizontal Scroll */}
          <div className="overflow-x-auto bg-white rounded-2xl border border-slate-200 shadow-xs">
            <table className="w-full text-left text-xs sm:text-sm border-collapse">
              <thead>
                <tr className="bg-slate-900 text-white">
                  {comparison.columns.map((col, idx) => (
                    <th
                      key={idx}
                      className={`py-3.5 px-4 font-bold text-xs uppercase tracking-wider ${
                        idx === 0 ? 'w-1/4' : ''
                      }`}
                    >
                      {col}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {comparison.rows.map((row, rowIdx) => (
                  <tr
                    key={rowIdx}
                    className={rowIdx % 2 === 0 ? 'bg-white' : 'bg-slate-50/50'}
                  >
                    <td className="py-3.5 px-4 font-bold text-slate-800 bg-slate-50/80 border-r border-slate-100 text-xs sm:text-sm">
                      {row.feature}
                    </td>
                    {row.values.map((val, valIdx) => (
                      <td key={valIdx} className="py-3.5 px-4 text-slate-700 leading-relaxed text-xs sm:text-sm">
                        {val}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Neutral Summary Note */}
          <div className="bg-blue-50/70 border border-blue-200 p-5 rounded-2xl text-xs sm:text-sm text-blue-950 space-y-1.5 leading-relaxed">
            <div className="flex items-center gap-2 font-bold text-blue-900">
              <Info className="w-4 h-4 text-blue-600" />
              <span>Objective Educational Takeaway</span>
            </div>
            <p>{comparison.neutral_summary}</p>
          </div>

          {/* Official Sources Citation Bar */}
          <div className="bg-white p-4 rounded-2xl border border-slate-200 flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs">
            <div className="flex items-center gap-2 text-slate-600">
              <ShieldCheck className="w-4 h-4 text-emerald-600 shrink-0" />
              <span className="font-semibold text-slate-800">Referenced Official Authorities:</span>
            </div>
            <div className="flex flex-wrap items-center gap-3">
              {comparison.official_sources.map((src, i) => (
                <a
                  key={i}
                  href={src.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-1 font-semibold text-blue-600 hover:text-blue-800 transition-colors"
                >
                  <span>{src.title}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              ))}
            </div>
          </div>

          <DisclaimerBanner />
        </div>
      ) : null}
    </div>
  );
}
