import React, { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { analyzeCompatibility, getRecommendations } from '../services/api';
import {
  Zap, CheckCircle2, XCircle, AlertCircle, Lightbulb,
  Loader2, Info, ChevronDown, ChevronUp,
} from 'lucide-react';

// Known-working example job descriptions to help users test
const EXAMPLE_JD = `We are looking for a Senior Software Engineer to join our backend team.

Required skills:
- Python (FastAPI or Django)
- JavaScript or TypeScript for frontend work
- SQL databases (PostgreSQL preferred)
- Docker and Kubernetes for containerization
- Experience with AWS or GCP
- Familiarity with Java or Go is a plus

Nice to have:
- Rust or C++ for performance-critical components
- GraphQL API experience
- Kafka or RabbitMQ for event streaming`;

export default function VibeCheckPage() {
  const { username: paramUser } = useParams();
  const [username, setUsername]       = useState(paramUser || '');
  const [jd, setJd]                   = useState('');
  const [result, setResult]           = useState(null);
  const [recommendations, setRecs]    = useState(null);
  const [showJdPreview, setShowJdPreview] = useState(false);

  const mutation = useMutation({
    mutationFn: () => analyzeCompatibility(username.trim(), jd.trim()),
    onSuccess: async (data) => {
      setResult(data);
      setRecs(null);
      if (data.analysis_id) {
        try {
          const r = await getRecommendations(data.analysis_id);
          setRecs(r.recommendations);
        } catch (_) {}
      }
    },
  });

  const handleRun = () => {
    setResult(null);
    setRecs(null);
    mutation.mutate();
  };

  const pct = result?.match_percentage;
  const scoreColor =
    pct === null || pct === undefined ? 'text-slate-300'
    : pct >= 70 ? 'text-green-400'
    : pct >= 40 ? 'text-yellow-400'
    : 'text-red-400';

  const scoreRing =
    pct === null || pct === undefined ? 'ring-slate-600'
    : pct >= 70 ? 'ring-green-500'
    : pct >= 40 ? 'ring-yellow-500'
    : 'ring-red-500';

  const scoreLabel =
    pct === null || pct === undefined ? 'No languages detected'
    : pct === 100 ? '🎉 Perfect Match!'
    : pct >= 70 ? '✅ Strong Match'
    : pct >= 40 ? '⚠️ Partial Match'
    : '❌ Low Match';

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-8">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-yellow-500/10 border border-yellow-500/20 flex items-center justify-center">
          <Zap size={20} className="text-yellow-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">Vibe Check</h1>
          <p className="text-slate-400 text-sm">
            Paste any job description → see how your GitHub tech stack matches it.
          </p>
        </div>
      </div>

      {/* How it works */}
      <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-4 flex gap-3">
        <Info size={16} className="text-blue-400 shrink-0 mt-0.5" />
        <div className="text-sm text-slate-300 space-y-1">
          <p className="font-medium text-blue-300">How Vibe Check works</p>
          <p>It scans the job description for <strong>programming language names</strong> (Python, Java, Go…), then checks which of those languages appear in your cached GitHub repositories. The match % = matched languages ÷ required languages.</p>
          <p className="text-slate-400 text-xs">Frameworks (React, Docker, FastAPI) are detected but <em>not</em> scored — they appear as "Other tech detected".</p>
        </div>
      </div>

      {/* Form */}
      <div className="card space-y-4">
        <div>
          <label className="block text-sm font-medium text-slate-300 mb-1.5">GitHub Username</label>
          <input
            className="input"
            placeholder="e.g. torvalds"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <p className="text-xs text-slate-500 mt-1">
            Profile is synced automatically — no manual step needed.
          </p>
        </div>

        <div>
          <div className="flex items-center justify-between mb-1.5">
            <label className="block text-sm font-medium text-slate-300">Job Description</label>
            <button
              className="text-xs text-blue-400 hover:text-blue-300 transition"
              onClick={() => setJd(EXAMPLE_JD)}
            >
              Load example JD
            </button>
          </div>
          <textarea
            className="input min-h-[200px] resize-y font-mono text-sm"
            placeholder="Paste the full job description here…&#10;&#10;The more specific the JD, the better the match.&#10;e.g. 'We use Python, Go, and TypeScript…'"
            value={jd}
            onChange={(e) => setJd(e.target.value)}
          />
          <p className="text-xs text-slate-500 mt-1">
            {jd.trim().split(/\s+/).filter(Boolean).length} words
          </p>
        </div>

        <button
          className="btn-primary w-full flex items-center justify-center gap-2"
          disabled={mutation.isPending || !username.trim() || !jd.trim()}
          onClick={handleRun}
        >
          {mutation.isPending
            ? <><Loader2 size={16} className="animate-spin" /> Analyzing…</>
            : <><Zap size={16} /> Run Vibe Check</>}
        </button>

        {mutation.isPending && (
          <p className="text-center text-slate-400 text-xs">
            Syncing profile if needed, then comparing languages…
          </p>
        )}

        {mutation.isError && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-3 text-sm text-red-300">
            {mutation.error?.response?.data?.detail?.message
              || 'Analysis failed. Check the username and try again.'}
          </div>
        )}
      </div>

      {/* ── Results ── */}
      {result && (
        <div className="space-y-4">

          {/* Score ring */}
          <div className="card flex flex-col sm:flex-row items-center gap-6">
            <div className={`w-32 h-32 rounded-full ring-4 ${scoreRing} flex flex-col items-center justify-center shrink-0`}>
              <span className={`text-4xl font-black ${scoreColor}`}>
                {pct !== null && pct !== undefined ? `${pct}%` : 'N/A'}
              </span>
              <span className="text-xs text-slate-400 mt-0.5">match</span>
            </div>
            <div className="text-center sm:text-left">
              <p className="text-xl font-bold text-white">{scoreLabel}</p>
              <p className="text-slate-400 text-sm mt-1">{result.message}</p>
              {result.recognized_required_languages?.length > 0 && (
                <p className="text-slate-500 text-xs mt-2">
                  {result.matched_languages?.length} of {result.recognized_required_languages?.length} languages matched
                </p>
              )}
            </div>
          </div>

          {/* Language breakdown */}
          {result.recognized_required_languages?.length > 0 && (
            <div className="card space-y-2">
              <h3 className="font-semibold text-white mb-3">
                Languages found in JD ({result.recognized_required_languages.length})
              </h3>
              {result.recognized_required_languages.map((lang) => {
                const matched = result.matched_languages?.includes(lang);
                return (
                  <div
                    key={lang}
                    className={`flex items-center gap-3 p-3 rounded-xl border ${
                      matched
                        ? 'bg-green-500/10 border-green-500/20'
                        : 'bg-red-500/10 border-red-500/20'
                    }`}
                  >
                    {matched
                      ? <CheckCircle2 size={18} className="text-green-400 shrink-0" />
                      : <XCircle size={18} className="text-red-400 shrink-0" />}
                    <span className={`font-medium text-sm ${matched ? 'text-green-200' : 'text-red-200'}`}>
                      {lang}
                    </span>
                    <span className={`ml-auto text-xs font-medium badge ${
                      matched
                        ? 'bg-green-500/20 text-green-300'
                        : 'bg-red-500/20 text-red-300'
                    }`}>
                      {matched ? '✓ In your repos' : '✗ Not found'}
                    </span>
                  </div>
                );
              })}
            </div>
          )}

          {result.recognized_required_languages?.length === 0 && (
            <div className="card border-yellow-500/20 flex gap-3">
              <AlertCircle size={18} className="text-yellow-400 shrink-0 mt-0.5" />
              <div className="text-sm">
                <p className="font-medium text-yellow-300">No programming languages detected</p>
                <p className="text-slate-400 mt-1">
                  The job description didn't contain recognizable programming language names.
                  Make sure the JD mentions specific languages like <em>Python, Java, TypeScript, Go</em>, etc.
                </p>
              </div>
            </div>
          )}

          {/* Other tech keywords */}
          {result.unassessed_keywords?.length > 0 && (
            <div className="card">
              <button
                className="flex items-center gap-2 w-full text-left"
                onClick={() => setShowJdPreview((v) => !v)}
              >
                <AlertCircle size={15} className="text-blue-400" />
                <span className="text-sm font-medium text-white">
                  Other tech detected (not scored) — {result.unassessed_keywords.length} items
                </span>
                {showJdPreview ? <ChevronUp size={14} className="ml-auto text-slate-400" /> : <ChevronDown size={14} className="ml-auto text-slate-400" />}
              </button>
              {showJdPreview && (
                <div className="mt-3 flex flex-wrap gap-2">
                  {result.unassessed_keywords.map((kw) => (
                    <span key={kw} className="badge bg-blue-500/10 text-blue-300 border border-blue-500/20 text-xs capitalize">
                      {kw}
                    </span>
                  ))}
                </div>
              )}
              <p className="text-xs text-slate-500 mt-2">
                Frameworks, tools, and infrastructure keywords are shown for context but excluded from the score.
              </p>
            </div>
          )}

          {/* Career recommendations */}
          {recommendations?.length > 0 && (
            <div className="card space-y-3">
              <div className="flex items-center gap-2">
                <Lightbulb size={16} className="text-yellow-400" />
                <h3 className="font-semibold text-white">Career Recommendations</h3>
              </div>
              <p className="text-xs text-slate-400">
                How to close the gaps between the JD and your current portfolio:
              </p>
              {recommendations.map((r) => (
                <div key={r.skill} className="bg-slate-800/60 border border-slate-700/40 rounded-xl p-4">
                  <p className="font-semibold text-yellow-300 text-sm mb-1.5">{r.skill}</p>
                  <p className="text-slate-300 text-sm leading-relaxed">{r.suggestion}</p>
                </div>
              ))}
            </div>
          )}

          {recommendations !== null && recommendations?.length === 0 && result.match_percentage === 100 && (
            <div className="card border-green-500/20 text-center py-6">
              <p className="text-2xl mb-2">🎉</p>
              <p className="text-green-300 font-semibold">Perfect match — no gaps to fill!</p>
              <p className="text-slate-400 text-sm mt-1">Your portfolio already covers everything in this job description.</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
