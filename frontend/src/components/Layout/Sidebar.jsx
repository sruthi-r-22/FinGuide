import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  Home,
  MessageSquare,
  BookOpen,
  ClipboardCheck,
  ShieldAlert,
  Scale,
  FileText,
  Info,
  ShieldCheck,
  Sparkles,
  ExternalLink
} from 'lucide-react';

const NAV_ITEMS = [
  { name: 'Home', path: '/', icon: Home },
  { name: 'Ask FinGuide', path: '/chat', icon: MessageSquare, badge: 'RAG' },
  { name: 'Banking Glossary', path: '/glossary', icon: BookOpen },
  { name: 'Document Checklist', path: '/checklist', icon: ClipboardCheck },
  { name: 'Spot the Scam', path: '/scam-awareness', icon: ShieldAlert, badge: 'Safety' },
  { name: 'Banking Comparisons', path: '/comparisons', icon: Scale },
  { name: 'Sources & Documents', path: '/sources', icon: FileText },
  { name: 'About & Disclaimer', path: '/about', icon: Info },
];

export default function Sidebar({ isOpen, onClose }) {
  return (
    <>
      {/* Mobile backdrop */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40 bg-slate-900/50 backdrop-blur-xs lg:hidden"
          onClick={onClose}
        />
      )}

      <aside
        className={`fixed top-0 bottom-0 left-0 z-50 w-72 bg-slate-950 text-slate-100 flex flex-col transition-transform duration-300 ease-in-out border-r border-slate-800 ${
          isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'
        }`}
      >
        {/* Logo and Brand */}
        <div className="p-5 border-b border-slate-800/80 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-blue-600 via-indigo-600 to-emerald-400 p-0.5 shadow-lg shadow-blue-500/20">
              <div className="w-full h-full bg-slate-950 rounded-[10px] flex items-center justify-center">
                <ShieldCheck className="w-5 h-5 text-emerald-400" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-1.5">
                <span className="font-bold text-lg tracking-tight text-white">FinGuide</span>
                <span className="text-xs font-semibold px-1.5 py-0.5 rounded bg-blue-500/20 text-blue-400 border border-blue-500/30">AI</span>
              </div>
              <p className="text-[11px] text-slate-400 tracking-wide font-medium">Banking Education Assistant</p>
            </div>
          </div>
        </div>

        {/* Navigation list */}
        <div className="flex-1 overflow-y-auto py-4 px-3 space-y-1">
          <p className="px-3 pb-2 text-[10px] font-bold uppercase tracking-wider text-slate-400">
            Platform Features
          </p>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            return (
              <NavLink
                key={item.path}
                to={item.path}
                onClick={onClose}
                className={({ isActive }) =>
                  `flex items-center justify-between px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                    isActive
                      ? 'bg-blue-600 text-white shadow-md shadow-blue-600/30'
                      : 'text-slate-300 hover:text-white hover:bg-slate-900/80'
                  }`
                }
              >
                <div className="flex items-center gap-3">
                  <Icon className="w-4 h-4 shrink-0" />
                  <span>{item.name}</span>
                </div>
                {item.badge && (
                  <span className="text-[10px] px-1.5 py-0.5 rounded-full font-semibold uppercase tracking-wider bg-slate-800 text-slate-300 border border-slate-700">
                    {item.badge}
                  </span>
                )}
              </NavLink>
            );
          })}
        </div>

        {/* Official helpline info card */}
        <div className="p-4 m-3 rounded-xl bg-slate-900/90 border border-slate-800 text-xs">
          <div className="flex items-center gap-2 text-emerald-400 font-semibold mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Cyber Fraud Emergency</span>
          </div>
          <p className="text-slate-400 text-[11px] leading-relaxed mb-2">
            Lost funds or facing scam call? Call National Helpline immediately.
          </p>
          <a
            href="tel:1930"
            className="flex items-center justify-between px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 font-bold hover:bg-emerald-500/20 transition-colors"
          >
            <span>Dial 1930</span>
            <ExternalLink className="w-3 h-3" />
          </a>
        </div>

        {/* Footer info */}
        <div className="p-4 border-t border-slate-800/80 text-[11px] text-slate-400 text-center">
          <p className="font-medium text-slate-400">Strictly Educational</p>
          <p className="text-[10px] mt-0.5">Official evidence required for verification</p>
        </div>
      </aside>
    </>
  );
}
