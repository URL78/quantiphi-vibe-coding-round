import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function ErrorMessage({ message, onRetry }) {
  return (
    <div className="flex flex-col items-center gap-3 py-8 text-red-400">
      <AlertTriangle size={36} />
      <p className="text-center text-sm">{message || 'Something went wrong.'}</p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="px-4 py-1.5 rounded-lg bg-red-500/20 hover:bg-red-500/30 text-red-300 text-sm transition"
        >
          Retry
        </button>
      )}
    </div>
  );
}
