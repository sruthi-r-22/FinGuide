import React, { useState, useEffect } from 'react';
import { Menu, ShieldCheck, Activity, KeyRound, CheckCircle, AlertTriangle } from 'lucide-react';
import { api } from '../../services/api';

export default function Navbar({ onToggleSidebar }) {
  const [health, setHealth] = useState(null);
  const [isOnline, setIsOnline] = useState(false);

  useEffect(() => {
    let isMounted = true;
    const check = async () => {
      try {
        const data = await api.checkHealth();
        if (isMounted) {
          setHealth(data);
          setIsOnline(true);
        }
      } catch {
        if (isMounted) {
          setIsOnline(false);
        }
      }
    };
    check();
    const interval = setInterval(check, 30000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  return (
    <header className="sticky top-0 z-30 bg-white/90 backdrop-blur-md border-b border-slate-200/80 px-4 sm:px-6 py-3">
      <div className="flex items-center justify-between max-w-7xl mx-auto">
        {/* Mobile menu trigger */}
        <div className="flex items-center gap-3">
          <button
            onClick={onToggleSidebar}
            className="lg:hidden p-2 rounded-xl text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-colors"
            aria-label="Toggle navigation"
          >
            <Menu className="w-5 h-5" />
          </button>

          <div className="hidden sm:flex items-center gap-2">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              Assistant Status:
            </span>
            <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-slate-100 text-slate-700 border border-slate-200">
              <span
                className={`w-2 h-2 rounded-full ${
                  isOnline ? 'bg-emerald-500 animate-pulse' : 'bg-rose-500'
                }`}
              />
              <span>{isOnline ? 'Core RAG Active' : 'Connecting to Backend...'}</span>
            </div>
          </div>
        </div>

        {/* Right side info: LLM & Document status */}
        <div className="flex items-center gap-2 sm:gap-3 text-xs">
          {health && (
            <div className="hidden md:flex items-center gap-2 px-3 py-1 rounded-xl bg-slate-50 border border-slate-200 text-slate-600">
              <ShieldCheck className="w-4 h-4 text-emerald-600" />
              <span>
                <b>{health.indexed_documents_count}</b> Documents Indexed (<b>{health.total_chunks}</b> chunks)
              </span>
            </div>
          )}

          <div className="flex items-center gap-1.5 px-2.5 py-1 rounded-xl bg-blue-50 border border-blue-200 text-blue-800 font-medium">
            <Activity className="w-3.5 h-3.5 text-blue-600" />
            <span>Educational Use Only</span>
          </div>
        </div>
      </div>
    </header>
  );
}
