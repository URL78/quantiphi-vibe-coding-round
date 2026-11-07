import React, { useState } from 'react';
import { BrainCircuit, Send, Loader2, MessageSquare, BookOpen } from 'lucide-react';
import { askDeepWiki, getWikiStructure } from '../services/api';

export default function DeepWikiPage() {
  const [owner, setOwner] = useState('');
  const [repo, setRepo] = useState('');
  const [question, setQuestion] = useState('');
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState('');
  const [error, setError] = useState('');
  const [structure, setStructure] = useState(null);
  const [structLoading, setStructLoading] = useState(false);

  const handleAsk = async (e) => {
    e.preventDefault();
    if (!owner.trim() || !repo.trim() || !question.trim()) return;
    setLoading(true); setError(''); setAnswer('');
    try {
      const res = await askDeepWiki(owner.trim(), repo.trim(), question.trim());
      setAnswer(res.answer);
    } catch (err) {
      setError(err?.response?.data?.detail?.message || 'DeepWiki unavailable. The repo may not be indexed yet.');
    } finally {
      setLoading(false);
    }
  };

  const handleStructure = async () => {
    if (!owner.trim() || !repo.trim()) return;
    setStructLoading(true); setStructure(null);
    try {
      const res = await getWikiStructure(owner.trim(), repo.trim());
      setStructure(res.structure);
    } catch (_) {
      setStructure('Could not retrieve structure.');
    } finally {
      setStructLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 py-10 space-y-8">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-purple-500/10 flex items-center justify-center">
          <BrainCircuit size={20} className="text-purple-400" />
        </div>
        <div>
          <h1 className="text-2xl font-bold text-white">DeepWiki AI</h1>
          <p className="text-slate-400 text-sm">Ask natural-language questions about any GitHub repository.</p>
        </div>
      </div>

      {/* Repo selector */}
      <div className="card space-y-3">
        <h2 className="font-semibold text-white text-sm">Repository</h2>
        <div className="grid sm:grid-cols-2 gap-3">
          <input className="input" placeholder="Owner (e.g. facebook)" value={owner} onChange={(e) => setOwner(e.target.value)} />
          <input className="input" placeholder="Repo (e.g. react)" value={repo} onChange={(e) => setRepo(e.target.value)} />
        </div>
        <button className="btn-secondary flex items-center gap-2 text-sm" onClick={handleStructure} disabled={structLoading || !owner || !repo}>
          {structLoading ? <Loader2 size={14} className="animate-spin" /> : <BookOpen size={14} />}
          Load Wiki Structure
        </button>
        {structure && (
          <pre className="bg-slate-900 rounded-lg p-3 text-xs text-slate-300 overflow-x-auto max-h-48 leading-relaxed">
            {typeof structure === 'string' ? structure : JSON.stringify(structure, null, 2)}
          </pre>
        )}
      </div>

      {/* Ask form */}
      <form onSubmit={handleAsk} className="card space-y-3">
        <h2 className="font-semibold text-white text-sm flex items-center gap-2"><MessageSquare size={15} /> Ask a Question</h2>
        <textarea
          className="input min-h-[100px] resize-y"
          placeholder="e.g. How does the reconciler work? What is the purpose of fiber architecture?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button
          type="submit"
          className="btn-primary flex items-center gap-2 justify-center w-full"
          disabled={loading || !owner.trim() || !repo.trim() || !question.trim()}
        >
          {loading ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
          {loading ? 'Asking DeepWiki…' : 'Ask'}
        </button>
        {error && <p className="text-red-400 text-sm">{error}</p>}
      </form>

      {/* Answer */}
      {answer && (
        <div className="card space-y-2">
          <h3 className="font-semibold text-purple-300 flex items-center gap-2"><BrainCircuit size={16} /> DeepWiki Answer</h3>
          <div className="text-slate-200 text-sm leading-relaxed whitespace-pre-wrap">{answer}</div>
        </div>
      )}
    </div>
  );
}
