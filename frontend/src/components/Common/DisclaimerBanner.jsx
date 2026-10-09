import React from 'react';
import { AlertCircle, ShieldAlert } from 'lucide-react';

export default function DisclaimerBanner({ variant = 'default', message }) {
  if (variant === 'warning') {
    return (
      <div className="bg-amber-50 border border-amber-200 rounded-xl p-3.5 flex items-start gap-3 text-amber-900 text-xs sm:text-sm">
        <ShieldAlert className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
        <div>
          <p className="font-semibold text-amber-800">Safety & Security Reminder</p>
          <p className="mt-0.5 text-amber-700 leading-relaxed">
            {message || "Never enter your real ATM PIN, UPI PIN, One-Time Password (OTP), CVV, or full banking passwords. Official bank staff will never request these credentials."}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-slate-100 border border-slate-200/80 rounded-xl p-3 flex items-start gap-2.5 text-slate-600 text-xs">
      <AlertCircle className="w-4 h-4 text-slate-500 shrink-0 mt-0.5" />
      <p className="leading-relaxed">
        {message || "Educational guidance only: FinGuide AI uses relevant indexed evidence when available and identifies unverified material. It will say when official evidence is insufficient. It does not access accounts, execute transactions, or provide investment advice; verify specifics with your bank."}
      </p>
    </div>
  );
}
