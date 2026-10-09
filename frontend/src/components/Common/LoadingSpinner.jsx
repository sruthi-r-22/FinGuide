import React from 'react';

export default function LoadingSpinner({ size = 'md', text = 'Loading...' }) {
  const sizeClasses = {
    sm: 'w-4 h-4 border-2',
    md: 'w-6 h-6 border-2',
    lg: 'w-8 h-8 border-3',
  };

  return (
    <div className="flex flex-col items-center justify-center p-6 gap-3">
      <div
        className={`${sizeClasses[size] || sizeClasses.md} rounded-full border-blue-600 border-t-transparent animate-spin`}
      />
      {text && <p className="text-xs sm:text-sm text-slate-500 font-medium">{text}</p>}
    </div>
  );
}
