import React, { useState } from 'react';
import { BrainCircuit, Send, Loader2, MessageSquare, BookOpen, Info, ExternalLink } from 'lucide-react';
import { askDeepWiki, getWikiStructure } from '../services/api';

// Repos confirmed to be indexed by DeepWiki
const EXAMPLE_REPOS = [
  { owner: 'facebook',   repo: 'react',      desc: 'React UI library' },
  { owner: 'microsoft',  repo: 'vscode',     desc: 'VS Code editor' },
  { owner: 'tiangolo',   repo: 'fastapi',    desc: 'FastAPI framework' },
  { owner: 'django',     repo: 'django',     desc: 'Django web framework' },
  { owner: 'tensorflow', repo: 'tensorflow', desc: 'TensorFlow ML' },
  { owner: 'vercel',     repo: 'next.js',    desc: 'Next.js framework' },
];

const EXAMPLE_QUESTIONS = [
  'How does the core architecture work?',
  'What are the main components and how do they interact?',
  'How does routing work in this codebase?',
  'What design patterns are used?',
  'How is state management handled?',
];

export default function DeepWikiPage() {
  const [owner, setOwner]       = useState('');
  const [repo, setRepo]         = useState('');
  const [question, setQuestion] = useState('');
  const [loading, setLoading]   = useState(false);
  const [answer, setAnswer]     = useState('');
  const [error, setError]       = useState('');

  const [structLoading, setStructLoading] = useState(false);
  const [structure, setStructure]         = useState(null);
  const [structError, setStructError]     = useState('');

  const setExample = (ex) => {
    setOwner(ex.owner);
    setRepo(ex.repo);
    setAnswer('');
    setError('');
    setStructure(null);
    setStructError('');
  };

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!owner.trim() || !repo.trim() || !question.trim()) return;
    setLoading(true);
    setError('');
    setAnswer('');
    try {
      const res = await askDeepWiki(owner.trim(), repo.trim(), question.trim());
      setAnswer(res.answer);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setError(
        typeof detail === 'string'
          ? detail
          : detail?.message || 'Could not get an answer from DeepWiki.'
      );
    } finally {
      setLoading(false);
    }
  };

  const handleStructure = async () => {
    if (!owner.trim() || !repo.trim()) return;
    setStructLoading(true);
    setStructure(null);
    setStructError('');
    try {
      const res = await getWikiStructure(owner.trim(), repo.trim());
      setStructure(res.structure);
    } catch (err) {
      const detail = err?.response?.data?.detail;
      setStructError(
        typeof detail === 'string'
          ? detail
          : detail?.message || 'Could not load wiki structure.'
      );
    } finally {
      setStructLoading(false);
    }
  };

  const repoReady = owner.trim() && repo.trim();

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-8">

      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center">
          <BrainCircuit size={20} className="text-purple-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">DeepWiki AI</h1>
          <p className="text-slate-400 text-sm">
            Ask natural-language questions about any GitHub repository.
          </p>
        </div>
      </div>

      {/* How it works */}
      <div className="bg-purple-500/10 border border-purple-500/20 rounded-xl p-4 flex gap-3">
        <Info size={16} className="text-purple-400 shrink-0 mt-0.5" />
        <div className="text-sm text-slate-300 space-y-1">
          <p className="font-medium text-purple-300">How DeepWiki works</p>
          <p>
            DeepWiki (<a href="https://deepwiki.com" target="_blank" rel="noreferrer" className="text-blue-400 underline">deepwiki.com</a>) indexes public GitHub repositories and builds an AI knowledge base from their code and docs.
            This app queries DeepWiki's MCP API and shows the answer here.
          </p>
          <p className="text-yellow-300 text-xs font-medium mt-1">
            ⚠️ DeepWiki only indexes popular public repositories. Use the examples below to test.
          </p>
        </div>
      </div>

      {/* Quick-start examples */}
      <div className="card space-y-3">
        <h2 className="font-semibold text-white text-sm flex items-center gap-2">
          <BookOpen size={15} className="text-purple-400" />
          Try a known-indexed repository
        </h2>
        <div className="grid sm:grid-cols-3 gap-2">
          {EXAMPLE_REPOS.map((ex) => (
            <button
              key={`${ex.owner}/${ex.repo}`}
              onClick={() => setExample(ex)}
              className={`text-left p-3 rounded-xl border text-xs transition ${
                owner === ex.owner && repo === ex.repo
                  ? 'border-purple-500 bg-purple-500/15 text-purple-300'
                  : 'border-slate-700 hover:border-slate-500 text-slate-400 hover:text-white bg-slate-800/40'
              }`}
            >
              <p className="font-semibold">{ex.owner}/{ex.repo}</p>
              <p className="text-slate-500 mt-0.5">{ex.desc}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Repo selector */}
      <div className="card space-y-3">
        <h2 className="font-semibold text-white text-sm">Repository</h2>
        <div className="grid sm:grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-slate-400 mb-1">Owner / Organisation</label>
            <input
              className="input"
              placeholder="e.g. facebook"
              value={owner}
              onChange={(e) => setOwner(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-xs text-slate-400 mb-1">Repository name</label>
            <input
              className="input"
              placeholder="e.g. react"
              value={repo}
              onChange={(e) => setRepo(e.target.value)}
            />
          </div>
        </div>

        {repoReady && (
          <a
            href={`https://github.com/${owner}/${repo}`}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-1.5 text-xs text-blue-400 hover:underline"
          >
            <ExternalLink size={11} /> github.com/{owner}/{repo}
          </a>
        )}

        <button
          className="btn-secondary flex items-center gap-2 text-sm"
          onClick={handleStructure}
          disabled={structLoading || !repoReady}
        >
          {structLoading ? <Loader2 size={14} className="animate-spin" /> : <BookOpen size={14} />}
          Load Wiki Structure
        </button>

        {structError && (
          <p className="text-sm text-red-300 bg-red-500/10 border border-red-500/20 rounded-lg p-3">
            {structError}
          </p>
        )}

        {structure && (
          <pre className="bg-slate-900/80 border border-slate-700 rounded-xl p-4 text-xs text-slate-300 overflow-x-auto max-h-64 leading-relaxed whitespace-pre-wrap">
            {typeof structure === 'string' ? structure : JSON.stringify(structure, null, 2)}
          </pre>
        )}
      </div>

      {/* Question form */}
      <form onSubmit={handleAsk} className="card space-y-3">
        <h2 className="font-semibold text-white text-sm flex items-center gap-2">
          <MessageSquare size={15} className="text-purple-400" />
          Ask a Question
        </h2>

        {/* Quick question suggestions */}
        <div className="flex flex-wrap gap-2">
          {EXAMPLE_QUESTIONS.map((q) => (
            <button
              key={q}
              type="button"
              onClick={() => setQuestion(q)}
              className="text-xs px-2.5 py-1 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-400 hover:text-white border border-slate-700 hover:border-slate-500 transition"
            >
              {q}
            </button>
          ))}
        </div>

        <textarea
          className="input min-h-[100px] resize-y"
          placeholder="e.g. How does React reconciliation work?&#10;What is the purpose of the fiber architecture?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />

        <button
          type="submit"
          className="btn-primary w-full flex items-center justify-center gap-2"
          disabled={loading || !repoReady || !question.trim()}
        >
          {loading
            ? <><Loader2 size={16} className="animate-spin" /> Asking DeepWiki…</>
            : <><Send size={16} /> Ask DeepWiki</>}
        </button>

        {loading && (
          <p className="text-center text-slate-400 text-xs">
            DeepWiki is analyzing the repository… this may take 10–30 seconds.
          </p>
        )}

        {error && (
          <div className="bg-red-500/10 border border-red-500/20 rounded-xl p-4 text-sm text-red-300 space-y-1">
            <p className="font-medium">DeepWiki could not answer this</p>
            <p>{error}</p>
            {error.includes('not indexed') && (
              <p className="text-xs text-slate-400 mt-2">
                💡 Try one of the example repositories above — they are confirmed to be indexed.
              </p>
            )}
          </div>
        )}
      </form>

      {/* Answer */}
      {answer && (
        <div className="card space-y-3 border-purple-500/20">
          <div className="flex items-center gap-2">
            <BrainCircuit size={16} className="text-purple-400" />
            <h3 className="font-semibold text-purple-300">DeepWiki Answer</h3>
            <span className="ml-auto text-xs text-slate-500">
              {owner}/{repo}
            </span>
          </div>
          <div className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap border-t border-slate-700/50 pt-3">
            {answer}
          </div>
        </div>
      )}
    </div>
  );
}
