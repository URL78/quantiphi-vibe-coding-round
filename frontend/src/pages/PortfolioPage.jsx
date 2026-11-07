import React from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getPortfolio } from '../services/api';
import Spinner from '../components/common/Spinner';
import ErrorMessage from '../components/common/ErrorMessage';
import { Code2, Star, GitFork, Users, ExternalLink } from 'lucide-react';
import { formatNumber, getLangColor } from '../utils/format';

export default function PortfolioPage() {
  const { username } = useParams();
  const { data, isLoading, isError, error } = useQuery({
    queryKey: ['portfolio', username],
    queryFn: () => getPortfolio(username),
  });

  if (isLoading) return <div className="py-24"><Spinner size={40} /></div>;
  if (isError) return (
    <div className="py-24">
      <ErrorMessage message={error?.response?.data?.detail?.message || 'Portfolio not available.'} />
    </div>
  );

  const { profile, analytics, languages, featured_repositories, latest_analysis } = data;

  return (
    <div className="max-w-4xl mx-auto px-4 py-10 space-y-10">
      {/* Profile hero */}
      <div className="card flex flex-col sm:flex-row items-center sm:items-start gap-6">
        <img src={profile.avatar_url} alt={profile.github_username} className="w-28 h-28 rounded-full ring-4 ring-blue-500/30 shrink-0" />
        <div className="text-center sm:text-left">
          <h1 className="text-3xl font-black text-white">{profile.name || profile.github_username}</h1>
          <a href={profile.github_url} target="_blank" rel="noreferrer" className="inline-flex items-center gap-1 text-blue-400 hover:underline text-sm mt-1">
            <Code2 size={13} /> @{profile.github_username} <ExternalLink size={11} />
          </a>
          {profile.bio && <p className="text-slate-400 mt-3 max-w-xl">{profile.bio}</p>}
          <div className="flex gap-5 mt-4 justify-center sm:justify-start text-sm text-slate-300 flex-wrap">
            <span className="flex items-center gap-1"><Users size={14} /> {formatNumber(analytics.followers)} followers</span>
            <span className="flex items-center gap-1"><Star size={14} /> {formatNumber(analytics.total_stars)} stars</span>
            <span className="flex items-center gap-1"><GitFork size={14} /> {formatNumber(analytics.total_forks)} forks</span>
          </div>
        </div>
      </div>

      {/* Top languages */}
      {languages?.length > 0 && (
        <div className="card">
          <h2 className="text-lg font-bold text-white mb-4">Top Languages</h2>
          <div className="space-y-2">
            {languages.slice(0, 6).map((lang) => (
              <div key={lang.name} className="flex items-center gap-3">
                <span className="w-2 h-2 rounded-full shrink-0" style={{ background: getLangColor(lang.name) }} />
                <span className="text-sm text-slate-200 w-28 shrink-0">{lang.name}</span>
                <div className="flex-1 bg-slate-700/50 rounded-full h-2 overflow-hidden">
                  <div className="h-2 rounded-full" style={{ width: `${lang.percentage}%`, background: getLangColor(lang.name) }} />
                </div>
                <span className="text-xs text-slate-400 w-12 text-right">{lang.percentage}%</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Featured repos */}
      {featured_repositories?.length > 0 && (
        <div>
          <h2 className="text-lg font-bold text-white mb-4">Featured Projects</h2>
          <div className="grid sm:grid-cols-2 gap-4">
            {featured_repositories.map((repo) => (
              <div key={repo.id} className="card hover:border-slate-600 transition">
                <a href={repo.html_url} target="_blank" rel="noreferrer" className="font-semibold text-white hover:text-blue-400 transition flex items-center gap-1.5">
                  {repo.name} <ExternalLink size={12} />
                </a>
                {repo.description && <p className="text-sm text-slate-400 mt-1 line-clamp-2">{repo.description}</p>}
                <div className="flex gap-3 mt-3 text-xs text-slate-400">
                  {repo.language && (
                    <span className="flex items-center gap-1">
                      <span className="w-2 h-2 rounded-full" style={{ background: getLangColor(repo.language) }} />
                      {repo.language}
                    </span>
                  )}
                  <span className="flex items-center gap-1"><Star size={11} /> {repo.stars}</span>
                  <span className="flex items-center gap-1"><GitFork size={11} /> {repo.forks}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Latest Vibe Check */}
      {latest_analysis && (
        <div className="card border-yellow-500/20">
          <h2 className="text-lg font-bold text-white mb-3">Latest Vibe Check</h2>
          <div className="flex items-center gap-4">
            <div className={`text-4xl font-black ${(latest_analysis.match_percentage ?? 0) >= 70 ? 'text-green-400' : (latest_analysis.match_percentage ?? 0) >= 40 ? 'text-yellow-400' : 'text-red-400'}`}>
              {latest_analysis.match_percentage !== null ? `${latest_analysis.match_percentage?.toFixed(0)}%` : 'N/A'}
            </div>
            <div>
              <p className="text-slate-300 text-sm">tech-stack match</p>
              <div className="flex flex-wrap gap-1.5 mt-2">
                {latest_analysis.matched_languages?.map((l) => (
                  <span key={l} className="badge bg-green-500/15 text-green-300 border border-green-500/20">{l}</span>
                ))}
                {latest_analysis.unmatched_languages?.map((l) => (
                  <span key={l} className="badge bg-red-500/15 text-red-300 border border-red-500/20">{l}</span>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
