import React, { useState, useEffect } from 'react';
import { Search, BookOpen, ExternalLink, ShieldAlert, Sparkles, Filter, X } from 'lucide-react';
import { api } from '../services/api';
import LoadingSpinner from '../components/Common/LoadingSpinner';

const CATEGORIES = [
  'All',
  'Identity & Compliance',
  'Payment Systems',
  'Banking Codes',
  'Security & Authentication',
  'Cards & Access',
  'Bank Accounts',
  'Account Management',
  'Digital Services'
];

export default function GlossaryPage() {
  const [terms, setTerms] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchGlossary();
  }, [searchTerm, selectedCategory]);

  const fetchGlossary = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const catParam = selectedCategory === 'All' ? '' : selectedCategory;
      const data = await api.getGlossary(searchTerm, catParam);
      setTerms(data);
    } catch (err) {
      console.error(err);
      setError('Failed to load glossary entries. Please check if the backend is running.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-6 pb-12">
      {/* Header */}
      <div>
        <div className="flex items-center gap-2 mb-1">
          <div className="p-2 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-600">
            <BookOpen className="w-5 h-5" />
          </div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight">Banking Glossary</h1>
        </div>
        <p className="text-xs sm:text-sm text-slate-500">
          Beginner-friendly definitions, practical examples, safety rules, and official links for fundamental banking terminology.
        </p>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-4 rounded-2xl border border-slate-200 shadow-xs space-y-4">
        <div className="relative">
          <Search className="absolute left-3.5 top-3.5 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by term, abbreviation, or concept (e.g. 'UPI', 'IFSC', 'KYC', 'eKYC')..."
            className="w-full pl-10 pr-10 py-2.5 rounded-xl border border-slate-200 text-sm text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-600 focus:border-transparent"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm('')}
              className="absolute right-3 top-3 text-slate-400 hover:text-slate-600"
            >
              <X className="w-4 h-4" />
            </button>
          )}
        </div>

        {/* Category Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-1 text-xs">
          <Filter className="w-3.5 h-3.5 text-slate-400 shrink-0 mr-1" />
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-3 py-1.5 rounded-xl font-medium transition-all shrink-0 cursor-pointer ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white shadow-xs'
                  : 'bg-slate-100 text-slate-600 hover:bg-slate-200'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Content Stream */}
      {isLoading ? (
        <LoadingSpinner text="Searching glossary terms..." />
      ) : error ? (
        <div className="p-4 bg-rose-50 border border-rose-200 text-rose-800 rounded-2xl text-xs">
          {error}
        </div>
      ) : terms.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-2xl border border-slate-200 p-8 space-y-3">
          <BookOpen className="w-10 h-10 text-slate-300 mx-auto" />
          <h3 className="text-base font-bold text-slate-700">No matching banking terms found</h3>
          <p className="text-xs text-slate-500 max-w-sm mx-auto">
            Try adjusting your search query or clear the category filter to view all available definitions.
          </p>
          <button
            onClick={() => { setSearchTerm(''); setSelectedCategory('All'); }}
            className="px-4 py-2 bg-slate-900 text-white rounded-xl text-xs font-semibold hover:bg-slate-800"
          >
            Reset Filters
          </button>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {terms.map((item) => (
            <div
              key={item.id}
              className="bg-white rounded-2xl border border-slate-200/90 hover:border-blue-300 hover:shadow-md transition-all p-5 flex flex-col justify-between gap-4"
            >
              <div className="space-y-3">
                {/* Term Header */}
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <h3 className="text-lg font-bold text-slate-900">{item.term}</h3>
                    {item.full_form && (
                      <p className="text-xs font-semibold text-blue-600 mt-0.5">
                        {item.full_form}
                      </p>
                    )}
                  </div>
                  <span className="px-2.5 py-0.5 rounded-full text-[10px] font-semibold bg-slate-100 text-slate-600 border border-slate-200 shrink-0">
                    {item.category}
                  </span>
                </div>

                {/* Definition */}
                <p className="text-xs sm:text-sm text-slate-700 leading-relaxed">
                  {item.definition}
                </p>

                {/* Example */}
                {item.example && (
                  <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/70 text-xs text-slate-600">
                    <span className="font-semibold text-slate-800 block mb-0.5">Everyday Example:</span>
                    <span>{item.example}</span>
                  </div>
                )}

                {/* Safety note */}
                {item.safety_note && (
                  <div className="bg-emerald-50/80 border border-emerald-200/80 p-3 rounded-xl text-xs text-emerald-900 flex items-start gap-2">
                    <ShieldAlert className="w-4 h-4 text-emerald-600 shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold text-emerald-800 block">Crucial Safety Rule:</span>
                      <span className="leading-relaxed">{item.safety_note}</span>
                    </div>
                  </div>
                )}
              </div>

              {/* Official Source Link */}
              <div className="pt-3 border-t border-slate-100 flex items-center justify-between text-[11px] text-slate-500">
                <span className="truncate max-w-[240px] sm:max-w-xs text-slate-500">
                  Source: {item.source_title}
                </span>
                {item.source_url && (
                  <a
                    href={item.source_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center gap-1 font-semibold text-blue-600 hover:text-blue-800 transition-colors"
                  >
                    <span>Official Doc</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
