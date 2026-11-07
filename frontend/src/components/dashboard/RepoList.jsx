import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { getRepositories, toggleFeatured } from '../../services/api';
import Spinner from '../common/Spinner';
import { Star, GitFork, ExternalLink, Bookmark, BookmarkCheck } from 'lucide-react';
import { getLangColor, timeAgo } from '../../utils/format';

const SORTS = [
  { value: 'stars', label: 'Stars' },
  { value: 'updated_at', label: 'Recently Updated' },
  { value: 'name', label: 'Name' },
];

export default function RepoList({ username }) {
  const [sort, setSort] = useState('stars');
  const [page, setPage] = useState(1);
  const limit = 12;

  const { data, isLoading, refetch } = useQuery({
    queryKey: ['repos', username, sort, page],
    queryFn: () => getRepositories(username, { sort_by: sort, page, limit }),
  });

  const handleFeatured = async (repo) => {
    await toggleFeatured(username, repo.name, !repo.featured);
    refetch();
  };

  if (isLoading) return <Spinner />;
  if (!data?.repositories?.length) return <p className="text-slate-400 text-sm">No repositories found.</p>;

  return (
    <div className="space-y-4">
      {/* Sort control */}
      <div className="flex gap-2 flex-wrap">
        {SORTS.map((s) => (
          <button
            key={s.value}
            onClick={() => { setSort(s.value); setPage(1); }}
            className={`text-xs px-3 py-1.5 rounded-lg font-medium transition ${sort === s.value ? 'bg-blue-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'}`}
          >
            {s.label}
          </button>
        ))}
      </div>

      {/* Grid */}
      <div className="grid sm:grid-cols-2 xl:grid-cols-3 gap-3">
        {data.repositories.map((repo) => (
          <div key={repo.id} className="card flex flex-col gap-2 hover:border-slate-600 transition group">
            <div className="flex items-start justify-between gap-2">
              <a href={repo.html_url} target="_blank" rel="noreferrer"
                className="font-semibold text-white text-sm hover:text-blue-400 transition flex items-center gap-1 leading-tight">
                {repo.name}
                <ExternalLink size={11} className="opacity-0 group-hover:opacity-60 transition" />
              </a>
              <button onClick={() => handleFeatured(repo)} title={repo.featured ? 'Unfeature' : 'Feature'}>
                {repo.featured
                  ? <BookmarkCheck size={16} className="text-blue-400" />
                  : <Bookmark size={16} className="text-slate-500 hover:text-slate-300 transition" />}
              </button>
            </div>

            {repo.description && <p className="text-xs text-slate-400 line-clamp-2">{repo.description}</p>}

            <div className="flex items-center gap-3 text-xs text-slate-400 mt-auto pt-1">
              {repo.language && (
                <span className="flex items-center gap-1">
                  <span className="w-2 h-2 rounded-full" style={{ background: getLangColor(repo.language) }} />
                  {repo.language}
                </span>
              )}
              <span className="flex items-center gap-1"><Star size={11} /> {repo.stars}</span>
              <span className="flex items-center gap-1"><GitFork size={11} /> {repo.forks}</span>
              {repo.updated_at && <span className="ml-auto">{timeAgo(repo.updated_at)}</span>}
            </div>
          </div>
        ))}
      </div>

      {/* Pagination */}
      {data.total > limit && (
        <div className="flex gap-2 justify-center pt-2">
          <button onClick={() => setPage((p) => Math.max(1, p - 1))} disabled={page === 1} className="btn-secondary disabled:opacity-40">← Prev</button>
          <span className="text-sm text-slate-400 self-center">Page {page}</span>
          <button onClick={() => setPage((p) => p + 1)} disabled={data.repositories.length < limit} className="btn-secondary disabled:opacity-40">Next →</button>
        </div>
      )}
    </div>
  );
}
