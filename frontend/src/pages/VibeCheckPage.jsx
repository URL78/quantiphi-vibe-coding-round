import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { analyzeCompatibility, getRecommendations } from '../services/api';
import { Zap, CheckCircle2, XCircle, AlertCircle, Lightbulb, Loader2 } from 'lucide-react';

export default function VibeCheckPage() {
  const { username: paramUser } = useParams();
  const [username, setUsername] = useState(paramUser || '');
  const [jd, setJd] = useState('');
  const [result, setResult] = useState(null);
  const [recommendations, setRecommendations] = useState(null);

  const mutation = useMutation({
    mutationFn: () => analyzeCompatibility(username.trim(), jd.trim()),
    onSuccess: async (data) => {
      setResult(data);
      if (data.analysis_id) {
        try {
          const recs = await getRecommendations(data.analysis_id);
          setRecommendations(recs.recommendations);
        } catch (_) {}
      }
    },
  });

  const pct = result?.match_percentage;
  const scoreColor =
    pct === null || pct === undefined ? 'text-slate-400'
    : pct >= 70 ? 'text-green-400'
    : pct >= 40 ? 'text-yellow-400'
    : 'text-red-400';

  const scoreRing =
    pct === null || pct === undefined ? 'ring-slate-600'
    : pct >= 70 ? 'ring-green-500'
    : pct >= 40 ? 'ring-yellow-500'
    : 'ring-red-500';

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-8">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-yellow-500/10 flex items-center justify-center">
          <Zap size={20} className="text-yellow-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Vibe Check</h1>
          <p className="text-slate-400 text-sm">Tech-stack compatibility analysis against a job description.</p>
        </div>
      </div>

      {/* Form */}
      <div className="card space-y-4">
        <div>
          <label className="block text-sm text-slate-300 mb-1 font-medium">GitHub Username</label>
          <input className="input" placeholder="e.g. torvalds" value={username} onChange={(e) => setUsername(e.target.value)} />
        </div>
        <div>
          <label className="block text-sm text-slate-300 mb-1 font-medium">Job Description</label>
          <textarea
            className="input min-h-[180px] resize-y"
            placeholder="Paste the full job description here…"
            value={jd}
            onChange={(e) => setJd(e.target.value)}
          />
        </div>
        <button
          className="btn-primary w-full flex items-center justify-center gap-2"
          disabled={mutation.isPending || !username.trim() || !jd.trim()}
          onClick={() => { setResult(null); setRecommendations(null); mutation.mutate(); }}
        >
          {mutation.isPending ? <Loader2 size={16} className="animate-spin" /> : <Zap size={16} />}
          {mutation.isPending ? 'Analyzing…' : 'Run Vibe Check'}
        </button>
        {mutation.isError && (
          <p className="text-red-400 text-sm">
            {mutation.error?.response?.data?.detail?.message || 'Analysis failed. Make sure the profile is synced.'}
          </p>
        )}
      </div>

      {/* Results */}
      {result && (
        <div className="space-y-4">
          {/* Score badge */}
          <div className="card flex flex-col sm:flex-row items-center gap-6">
            <div className={`w-28 h-28 rounded-full ring-4 ${scoreRing} flex flex-col items-center justify-center shrink-0`}>
              <span className={`text-3xl font-black ${scoreColor}`}>
                {pct !== null && pct !== undefined ? `${pct.toFixed(0)}%` : 'N/A'}
              </span>
              <span className="text-xs text-slate-400">match</span>
            </div>
            <div className="text-center sm:text-left">
              <p className="text-white font-semibold text-lg">
                {pct === null ? 'No recognized languages' : pct >= 70 ? 'Strong Match! 🎉' : pct >= 40 ? 'Partial Match' : 'Low Match'}
              </p>
              <p className="text-slate-400 text-sm mt-1">{result.message}</p>
              <p className="text-xs text-slate-500 mt-1">Score basis: {result.score_basis}</p>
            </div>
          </div>

          {/* Language breakdown */}
          {result.recognized_required_languages?.length > 0 && (
            <div className="card space-y-3">
              <h3 className="font-semibold text-white">Language Breakdown</h3>
              <div className="space-y-2">
                {result.recognized_required_languages.map((lang) => {
                  const matched = result.matched_languages?.includes(lang);
                  return (
                    <div key={lang} className="flex items-center gap-2">
                      {matched
                        ? <CheckCircle2 size={16} className="text-green-400 shrink-0" />
                        : <XCircle size={16} className="text-red-400 shrink-0" />}
                      <span className={`text-sm ${matched ? 'text-green-300' : 'text-red-300'}`}>{lang}</span>
                      <span className={`ml-auto text-xs badge ${matched ? 'bg-green-500/15 text-green-400' : 'bg-red-500/15 text-red-400'}`}>
                        {matched ? 'In portfolio' : 'Missing'}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Unassessed keywords */}
          {result.unassessed_keywords?.length > 0 && (
            <div className="card">
              <div className="flex items-center gap-2 mb-3">
                <AlertCircle size={16} className="text-blue-400" />
                <h3 className="font-semibold text-white text-sm">Other Tech Detected (not scored)</h3>
              </div>
              <div className="flex flex-wrap gap-2">
                {result.unassessed_keywords.map((kw) => (
                  <span key={kw} className="badge bg-blue-500/10 text-blue-300 border border-blue-500/20 text-xs">{kw}</span>
                ))}
              </div>
            </div>
          )}

          {/* Career recommendations */}
          {recommendations?.length > 0 && (
            <div className="card space-y-3">
              <div className="flex items-center gap-2">
                <Lightbulb size={16} className="text-yellow-400" />
                <h3 className="font-semibold text-white">Career Recommendations</h3>
              </div>
              {recommendations.map((r) => (
                <div key={r.skill} className="bg-slate-800/50 rounded-xl p-3 border border-slate-700/40">
                  <p className="font-medium text-yellow-300 text-sm mb-1">{r.skill}</p>
                  <p className="text-slate-400 text-xs leading-relaxed">{r.suggestion}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
