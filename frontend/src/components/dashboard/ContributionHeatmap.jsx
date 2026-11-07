import React, { useMemo } from 'react';

const INTENSITY_COLORS = [
  'bg-slate-800',       // 0 – none
  'bg-green-900/60',    // 1
  'bg-green-700/70',    // 2
  'bg-green-500/80',    // 3
  'bg-green-400',       // 4
];

export default function ContributionHeatmap({ data }) {
  if (!data || data.length === 0)
    return <p className="text-slate-400 text-sm text-center py-8">Contribution data not available. A GitHub token is required.</p>;

  // Group by week
  const weeks = useMemo(() => {
    const map = new Map();
    data.forEach((d) => {
      const date = new Date(d.date);
      const day = date.getDay(); // 0=Sun
      const weekStart = new Date(date);
      weekStart.setDate(date.getDate() - day);
      const key = weekStart.toISOString().slice(0, 10);
      if (!map.has(key)) map.set(key, Array(7).fill(null));
      map.get(key)[day] = d;
    });
    return Array.from(map.values());
  }, [data]);

  const days = ['S','M','T','W','T','F','S'];

  return (
    <div className="overflow-x-auto">
      <div className="flex gap-0.5 min-w-max">
        {/* Day labels */}
        <div className="flex flex-col gap-0.5 mr-1 pt-5">
          {days.map((d, i) => (
            <span key={i} className="text-[9px] text-slate-500 h-3 leading-3">{i % 2 === 1 ? d : ''}</span>
          ))}
        </div>
        {/* Weeks */}
        {weeks.map((week, wi) => (
          <div key={wi} className="flex flex-col gap-0.5">
            {week.map((day, di) => (
              <div
                key={di}
                title={day ? `${day.date}: ${day.count} contributions` : ''}
                className={`w-3 h-3 rounded-sm ${day ? INTENSITY_COLORS[day.intensity ?? 0] : 'bg-slate-800/40'}`}
              />
            ))}
          </div>
        ))}
      </div>
      <div className="flex items-center gap-1.5 mt-2 text-xs text-slate-400">
        <span>Less</span>
        {INTENSITY_COLORS.map((c, i) => <div key={i} className={`w-3 h-3 rounded-sm ${c}`} />)}
        <span>More</span>
      </div>
    </div>
  );
}
