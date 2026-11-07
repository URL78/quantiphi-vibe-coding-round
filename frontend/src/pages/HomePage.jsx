import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Code2, Zap, BrainCircuit, BarChart2, ArrowRight, Loader2 } from 'lucide-react';
import { syncProfile } from '../services/api';
import { useApp } from '../context/AppContext';

const FEATURES = [
  { icon: BarChart2, title: 'Analytics Dashboard', desc: 'Profile stats, language distribution, contribution heatmap, and coding streaks.', color: 'blue' },
  { icon: Zap, title: 'Vibe Check', desc: 'Paste any job description — instantly see how well your GitHub tech stack matches.', color: 'yellow' },
  { icon: BrainCircuit, title: 'DeepWiki AI', desc: 'Ask natural-language questions about any GitHub repository powered by DeepWiki MCP.', color: 'purple' },
];

const colorMap = {
  blue: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
  yellow: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/20',
  purple: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
};

export default function HomePage() {
  const [username, setUsername] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { setCurrentUser } = useApp();
  const navigate = useNavigate();

  const handleSync = async (e) => {
    e.preventDefault();
    const u = username.trim();
    if (!u) return;
    setLoading(true);
    setError('');
    try {
      await syncProfile(u);
      setCurrentUser(u);
      navigate(`/dashboard/${u}`);
    } catch (err) {
      const msg = err?.response?.data?.detail?.message || err?.response?.data?.detail || 'Failed to sync profile.';
      setError(typeof msg === 'string' ? msg : JSON.stringify(msg));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-[90vh] flex flex-col items-center justify-center px-4 py-16">
      {/* Hero */}
      <div className="text-center max-w-2xl">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-blue-400 text-sm mb-6">
          <Code2 size={14} /> GitHub Developer Portfolio
        </div>
        <h1 className="text-4xl sm:text-5xl font-extrabold text-white leading-tight mb-4">
          Transform your GitHub into a{' '}
          <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-400 to-purple-400">
            Professional Portfolio
          </span>
        </h1>
        <p className="text-slate-400 text-lg mb-10">
          Analytics · Vibe Check · AI-powered repo explanations — all from one GitHub username.
        </p>

        {/* Search form */}
        <form onSubmit={handleSync} className="flex gap-2 max-w-md mx-auto">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              className="input pl-9"
              placeholder="Enter GitHub username…"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              disabled={loading}
            />
          </div>
          <button className="btn-primary flex items-center gap-2 shrink-0" disabled={loading || !username.trim()}>
            {loading ? <Loader2 size={16} className="animate-spin" /> : <ArrowRight size={16} />}
            {loading ? 'Syncing…' : 'Explore'}
          </button>
        </form>

        {error && <p className="text-red-400 text-sm mt-3">{error}</p>}

        {/* Quick examples */}
        <div className="flex gap-2 justify-center mt-4 flex-wrap">
          {['torvalds', 'gvanrossum', 'addyosmani'].map((u) => (
            <button
              key={u}
              onClick={() => setUsername(u)}
              className="text-xs px-3 py-1 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white transition"
            >
              @{u}
            </button>
          ))}
        </div>
      </div>

      {/* Feature cards */}
      <div className="grid sm:grid-cols-3 gap-4 max-w-3xl w-full mt-16">
        {FEATURES.map(({ icon: Icon, title, desc, color }) => (
          <div key={title} className={`card border ${colorMap[color]} flex flex-col gap-3`}>
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${colorMap[color]} border`}>
              <Icon size={18} />
            </div>
            <h3 className="font-semibold text-white">{title}</h3>
            <p className="text-sm text-slate-400">{desc}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
