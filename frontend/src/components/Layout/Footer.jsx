import React from 'react';
import { ShieldCheck, Heart } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Footer() {
  return (
    <footer className="mt-auto border-t border-slate-200 bg-white py-6 px-4 sm:px-6 text-xs text-slate-500">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex items-center gap-2">
          <ShieldCheck className="w-4 h-4 text-emerald-600" />
          <span className="font-semibold text-slate-800">FinGuide AI</span>
          <span>— Understand Banking. Navigate Digital Services. Stay Scam-Aware.</span>
        </div>

        <div className="flex items-center gap-4 text-xs font-medium">
          <Link to="/about" className="hover:text-blue-600 transition-colors">
            Safety Charter
          </Link>
          <Link to="/sources" className="hover:text-blue-600 transition-colors">
            Sources & Provenance
          </Link>
          <Link to="/glossary" className="hover:text-blue-600 transition-colors">
            Glossary
          </Link>
          <a
            href="https://cybercrime.gov.in"
            target="_blank"
            rel="noopener noreferrer"
            className="text-emerald-700 hover:text-emerald-800 transition-colors"
          >
            Cybercrime Helpline (1930)
          </a>
        </div>
      </div>
      <div className="max-w-7xl mx-auto mt-3 pt-3 border-t border-slate-100 text-[11px] text-slate-400 text-center">
        FinGuide AI is an educational assistant. It never asks for PINs or passwords, and cannot perform transactions.
      </div>
    </footer>
  );
}
