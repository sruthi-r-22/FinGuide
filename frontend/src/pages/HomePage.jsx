import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  MessageSquare,
  BookOpen,
  ClipboardCheck,
  ShieldAlert,
  Scale,
  FileText,
  ArrowRight,
  ShieldCheck,
  Sparkles,
  Lock,
  Search,
  CheckCircle2
} from 'lucide-react';
import DisclaimerBanner from '../components/Common/DisclaimerBanner';

const SUGGESTED_QUESTIONS = [
  {
    title: "Opening a Savings Account",
    question: "What documents are generally needed to open a savings account?",
    category: "Accounts"
  },
  {
    title: "KYC vs CKYC Explainer",
    question: "Explain KYC and CKYC in simple words.",
    category: "Identity"
  },
  {
    title: "Payment Systems Comparison",
    question: "What is the difference between NEFT, RTGS, and IMPS?",
    category: "Payments"
  },
  {
    title: "Recognizing Scam Messages",
    question: "How can I recognize a fake KYC message?",
    category: "Safety"
  },
  {
    title: "Digital Identity Verification",
    question: "What is Aadhaar-based eKYC?",
    category: "Digital"
  }
];

const FEATURE_CARDS = [
  {
    title: "RAG Banking Assistant",
    description: "Ask banking questions. Answers cite authenticated official evidence when available and flag when an answer cannot be verified.",
    icon: MessageSquare,
    path: "/chat",
    color: "from-blue-600 to-indigo-600",
    badge: "AI Retrieval"
  },
  {
    title: "Document Checklist",
    description: "Interactive requirement builder for savings, current accounts, and KYC. Generates a downloadable PDF checklist.",
    icon: ClipboardCheck,
    path: "/checklist",
    color: "from-emerald-600 to-teal-600",
    badge: "PDF Export"
  },
  {
    title: "Banking Glossary",
    description: "Plain-English definitions and everyday examples for over 20 banking acronyms from KYC to IFSC and MICR.",
    icon: BookOpen,
    path: "/glossary",
    color: "from-indigo-600 to-purple-600",
    badge: "Searchable"
  },
  {
    title: "Spot the Scam",
    description: "Analyze suspicious SMS, calls, or collect requests with automated red flag detection and safety action guides.",
    icon: ShieldAlert,
    path: "/scam-awareness",
    color: "from-rose-600 to-amber-600",
    badge: "Safety Charter"
  },
  {
    title: "Banking Comparisons",
    description: "Side-by-side neutral comparison tables: NEFT vs RTGS vs IMPS, UPI vs Net Banking, Debit vs Credit Cards.",
    icon: Scale,
    path: "/comparisons",
    color: "from-sky-600 to-blue-700",
    badge: "Neutral Analysis"
  },
  {
    title: "Sources & Documents",
    description: "Inspect indexed documents, provenance labels, verification status, page and chunk counts, and verified source links when available.",
    icon: FileText,
    path: "/sources",
    color: "from-slate-700 to-slate-900",
    badge: "Provenance"
  }
];

export default function HomePage() {
  const [query, setQuery] = useState('');
  const navigate = useNavigate();

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      navigate('/chat', { state: { question: query.trim() } });
    }
  };

  const handleCardClick = (question) => {
    navigate('/chat', { state: { question } });
  };

  return (
    <div className="space-y-12 pb-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden rounded-3xl bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-white p-8 sm:p-12 lg:p-16 border border-slate-800 shadow-xl">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-blue-600/15 via-transparent to-transparent pointer-events-none" />

        <div className="relative max-w-3xl mx-auto text-center space-y-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-xs font-semibold uppercase tracking-wider">
            <Sparkles className="w-3.5 h-3.5" />
            <span>AI-Powered Banking Education</span>
          </div>

          <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white leading-tight">
            Banking made easier with <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-300 to-emerald-400">FinGuide AI</span>
          </h1>

          <p className="text-base sm:text-lg text-slate-300 leading-relaxed font-normal">
            Understand banking procedures, account-opening requirements, terminology, digital payments, and online safety. Answers distinguish verified official evidence from unverified material.
          </p>

          {/* Large Question Input Box */}
          <form onSubmit={handleSearchSubmit} className="pt-2 max-w-2xl mx-auto">
            <div className="relative flex items-center">
              <Search className="absolute left-4 w-5 h-5 text-slate-400" />
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Ask any banking question (e.g., 'What is KYC and why is it mandatory?')"
                className="w-full pl-12 pr-28 py-4 rounded-2xl bg-slate-900/90 border border-slate-700 text-white placeholder-slate-400 text-sm sm:text-base focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all shadow-lg"
              />
              <button
                type="submit"
                disabled={!query.trim()}
                className="absolute right-2.5 px-5 py-2.5 rounded-xl bg-blue-600 hover:bg-blue-500 disabled:bg-slate-800 text-white font-semibold text-xs sm:text-sm flex items-center gap-1.5 transition-all shadow-md cursor-pointer disabled:cursor-not-allowed"
              >
                <span>Ask</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </form>

          {/* Golden Rules Quick Pills */}
          <div className="flex flex-wrap items-center justify-center gap-3 pt-3 text-xs text-slate-400">
            <span className="flex items-center gap-1">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />
              Requires Verified Official Evidence
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <Lock className="w-3.5 h-3.5 text-blue-400" />
              Zero Credentials Accepted
            </span>
            <span>•</span>
            <span className="flex items-center gap-1">
              <ShieldCheck className="w-3.5 h-3.5 text-indigo-400" />
              100% Educational
            </span>
          </div>
        </div>
      </section>

      {/* Suggested Questions Section */}
      <section className="space-y-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-slate-900">Suggested Questions</h2>
            <p className="text-xs sm:text-sm text-slate-500">Popular starting points for students and first-time account holders</p>
          </div>
          <button
            onClick={() => navigate('/chat')}
            className="text-xs font-semibold text-blue-600 hover:text-blue-700 flex items-center gap-1"
          >
            Open Chat <ArrowRight className="w-3 h-3" />
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3.5">
          {SUGGESTED_QUESTIONS.map((item, idx) => (
            <div
              key={idx}
              onClick={() => handleCardClick(item.question)}
              className="group p-4 bg-white rounded-2xl border border-slate-200 hover:border-blue-300 hover:shadow-md transition-all cursor-pointer flex flex-col justify-between gap-3"
            >
              <div>
                <span className="inline-block px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider bg-slate-100 text-slate-600 group-hover:bg-blue-50 group-hover:text-blue-700 mb-2">
                  {item.category}
                </span>
                <h3 className="text-sm font-semibold text-slate-800 group-hover:text-blue-600 transition-colors">
                  {item.title}
                </h3>
                <p className="text-xs text-slate-500 mt-1 line-clamp-2">
                  "{item.question}"
                </p>
              </div>

              <div className="flex items-center justify-between text-xs font-medium text-slate-400 group-hover:text-blue-600 pt-2 border-t border-slate-100">
                <span>Ask FinGuide</span>
                <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
              </div>
            </div>
          ))}
        </div>
      </section>

      {/* Feature Modules Cards */}
      <section className="space-y-4">
        <div>
          <h2 className="text-xl font-bold text-slate-900">Explore Banking Features</h2>
          <p className="text-xs sm:text-sm text-slate-500">Comprehensive educational tools designed for clarity, safety, and empowerment</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {FEATURE_CARDS.map((feat, idx) => {
            const Icon = feat.icon;
            return (
              <div
                key={idx}
                onClick={() => navigate(feat.path)}
                className="group relative bg-white p-6 rounded-2xl border border-slate-200 hover:border-blue-400 hover:shadow-lg transition-all cursor-pointer flex flex-col justify-between"
              >
                <div>
                  <div className="flex items-center justify-between mb-4">
                    <div className={`w-11 h-11 rounded-xl bg-gradient-to-tr ${feat.color} text-white flex items-center justify-center shadow-md`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 group-hover:bg-blue-50 group-hover:text-blue-700 border border-slate-200">
                      {feat.badge}
                    </span>
                  </div>

                  <h3 className="text-base font-bold text-slate-900 group-hover:text-blue-600 transition-colors">
                    {feat.title}
                  </h3>
                  <p className="text-xs sm:text-sm text-slate-600 mt-2 leading-relaxed">
                    {feat.description}
                  </p>
                </div>

                <div className="flex items-center gap-1.5 text-xs font-semibold text-blue-600 group-hover:text-blue-700 mt-5 pt-3 border-t border-slate-100">
                  <span>Open Tool</span>
                  <ArrowRight className="w-3.5 h-3.5 transition-transform group-hover:translate-x-1" />
                </div>
              </div>
            );
          })}
        </div>
      </section>

      {/* Mandatory Disclaimer Banner */}
      <DisclaimerBanner />
    </div>
  );
}
