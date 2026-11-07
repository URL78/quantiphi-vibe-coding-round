import React from 'react';
import { Flame, TrendingUp, Calendar } from 'lucide-react';

export default function StreakWidget({ data }) {
  if (!data) return null;
  return (
    <div className="grid sm:grid-cols-3 gap-4">
      <div className="card flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-orange-500/10 flex items-center justify-center">
          <Flame size={20} className="text-orange-400" />
        </div>
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wide">Current Streak</p>
          <p className="text-2xl font-bold text-white">{data.current_streak} <span className="text-sm font-normal text-slate-400">days</span></p>
        </div>
      </div>
      <div className="card flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-blue-500/10 flex items-center justify-center">
          <TrendingUp size={20} className="text-blue-400" />
        </div>
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wide">Longest Streak</p>
          <p className="text-2xl font-bold text-white">{data.longest_streak} <span className="text-sm font-normal text-slate-400">days</span></p>
        </div>
      </div>
      <div className="card flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-green-500/10 flex items-center justify-center">
          <Calendar size={20} className="text-green-400" />
        </div>
        <div>
          <p className="text-xs text-slate-400 uppercase tracking-wide">Last Contribution</p>
          <p className="text-lg font-bold text-white">{data.last_contribution_date || 'N/A'}</p>
        </div>
      </div>
    </div>
  );
}
