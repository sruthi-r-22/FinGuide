import React from 'react';
import { ShieldCheck, Lock, AlertCircle, Database, Cpu, ExternalLink } from 'lucide-react';
import DisclaimerBanner from '../components/Common/DisclaimerBanner';

export default function AboutPage() {
  return (
    <div className="space-y-8 max-w-4xl pb-12">
      <div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-slate-900 tracking-tight">
          About FinGuide AI
        </h1>
        <p className="text-xs sm:text-sm text-slate-500 mt-1">
          Mission, Safety Architecture & Grounded Retrieval Methodology
        </p>
      </div>

      <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-xs space-y-4 leading-relaxed text-sm text-slate-700">
        <h2 className="text-base font-bold text-slate-900">Project Mission & Educational Intent</h2>
        <p>
          <b>FinGuide AI</b> is an educational banking guidance platform created to demystify complex banking processes for students, first-time account holders, and digital citizens. Modern retail banking involves intricate compliance rules (KYC, CKYC, OVDs), multi-tiered payment rails (NEFT, RTGS, IMPS, UPI), and emerging cyber fraud techniques.
        </p>
        <p>
          FinGuide AI uses <b>Retrieval-Augmented Generation (RAG)</b> to search its indexed documents. A document can support an official banking rule only after its publisher and provenance have been verified. Generated demos and unknown material are labelled unverified; when authenticated official evidence is unavailable, the assistant says it cannot verify the answer.
        </p>
      </div>

      {/* Safety Charter Grid */}
      <div className="space-y-3">
        <h2 className="text-base font-bold text-slate-900">Core Safety & Privacy Principles</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200/90 space-y-2">
            <div className="flex items-center gap-2 text-rose-700 font-bold text-sm">
              <Lock className="w-4 h-4" />
              <span>Zero-Credential Rule</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              FinGuide AI never asks for, accepts, or logs banking credentials. Automated security filters detect and reject 16-digit card numbers, CVVs, OTPs, ATM PINs, and UPI PINs before processing.
            </p>
          </div>

          <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200/90 space-y-2">
            <div className="flex items-center gap-2 text-blue-700 font-bold text-sm">
              <ShieldCheck className="w-4 h-4" />
              <span>Non-Transactional Guarantee</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              This system does not link to live bank accounts, cannot check account balances, execute payments, or debit funds. It operates strictly as an informational reference.
            </p>
          </div>

          <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200/90 space-y-2">
            <div className="flex items-center gap-2 text-emerald-700 font-bold text-sm">
              <Database className="w-4 h-4" />
              <span>Source-Grounded Anti-Hallucination</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              Answers cite retrieved official document pages only when the source is authenticated and the excerpt supports the claim. Otherwise, FinGuide AI identifies unverified material or states that it could not verify the answer.
            </p>
          </div>

          <div className="bg-slate-50 p-5 rounded-2xl border border-slate-200/90 space-y-2">
            <div className="flex items-center gap-2 text-indigo-700 font-bold text-sm">
              <Cpu className="w-4 h-4" />
              <span>Neutral Financial Position</span>
            </div>
            <p className="text-xs text-slate-600 leading-relaxed">
              FinGuide AI provides neutral factual comparisons and never recommends commercial credit products, loans, or individualized stock/mutual fund investments.
            </p>
          </div>
        </div>
      </div>

      {/* Emergency Cyber Contact */}
      <div className="bg-emerald-950 text-white p-6 rounded-2xl border border-emerald-900 space-y-3">
        <h3 className="text-base font-bold text-emerald-300">Reporting Cyber Financial Fraud in India</h3>
        <p className="text-xs text-slate-300 leading-relaxed">
          If you have been targeted by a financial scam, unauthorized transaction, or identity theft, contact your bank and use the official cybercrime reporting channels promptly. Reporting does not guarantee that funds will be frozen or recovered:
        </p>
        <div className="flex flex-wrap gap-4 pt-1">
          <div className="bg-emerald-900/60 border border-emerald-700/60 p-3 rounded-xl">
            <span className="text-[10px] uppercase tracking-wider text-emerald-300 font-bold block">Toll-Free Helpline</span>
            <span className="text-lg font-bold text-white">Dial 1930</span>
          </div>
          <div className="bg-emerald-900/60 border border-emerald-700/60 p-3 rounded-xl">
            <span className="text-[10px] uppercase tracking-wider text-emerald-300 font-bold block">National Portal</span>
            <a
              href="https://cybercrime.gov.in"
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-bold text-emerald-300 hover:text-white flex items-center gap-1"
            >
              <span>cybercrime.gov.in</span>
              <ExternalLink className="w-3.5 h-3.5" />
            </a>
          </div>
        </div>
      </div>

      <DisclaimerBanner />
    </div>
  );
}
