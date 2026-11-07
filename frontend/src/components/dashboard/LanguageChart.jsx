import React from 'react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { getLangColor } from '../../utils/format';

export default function LanguageChart({ data }) {
  if (!data || data.length === 0)
    return <p className="text-slate-400 text-sm text-center py-8">No language data available.</p>;

  const top = data.slice(0, 8);

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie data={top} dataKey="repository_count" nameKey="name" cx="50%" cy="50%" outerRadius={90} paddingAngle={2}>
          {top.map((entry) => (
            <Cell key={entry.name} fill={getLangColor(entry.name)} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{ background: '#1e293b', border: '1px solid #334155', borderRadius: 8, color: '#e2e8f0' }}
          formatter={(val, name) => [`${val} repos`, name]}
        />
        <Legend
          formatter={(val) => <span style={{ color: '#94a3b8', fontSize: 12 }}>{val}</span>}
        />
      </PieChart>
    </ResponsiveContainer>
  );
}
