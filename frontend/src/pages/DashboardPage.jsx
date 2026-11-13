import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  getProfile, getAnalytics, getLanguages,
  getStreaks, getContributions,
} from '../services/api';
import { useAutoSync } from '../hooks/useAutoSync';
import Spinner from '../components/common/Spinner';
import ErrorMessage from '../components/common/ErrorMessage';
import StatCard from '../components/common/StatCard';
import ProfileCard from '../components/dashboard/ProfileCard';
import LanguageChart from '../components/dashboard/LanguageChart';
import ContributionHeatmap from '../components/dashboard/ContributionHeatmap';
import StreakWidget from '../components/dashboard/StreakWidget';
import RepoList from '../components/dashboard/RepoList';
import { Users, Star, GitFork, BookOpen, Flame, Zap, RefreshCw, Loader2 } from 'lucide-react';
import { formatNumber } from '../utils/format';

export default function DashboardPage() {
  const { username } = useParams();
  const navigate = useNavigate();
  const qc = useQueryClient();
  const { syncing, syncError, ensureSync } = useAutoSync();
  const [autoSyncDone, setAutoSyncDone] = useState(false);

  // ── Data queries ────────────────────────────────────────────────────────
  const profileQ    = useQuery({ queryKey: ['profile', username],       queryFn: () => getProfile(username),       retry: false });
  const analyticsQ  = useQuery({ queryKey: ['analytics', username],     queryFn: () => getAnalytics(username),     enabled: !!profileQ.data, retry: false });
  const languagesQ  = useQuery({ queryKey: ['languages', username],     queryFn: () => getLanguages(username),     enabled: !!profileQ.data });
  const streaksQ    = useQuery({ queryKey: ['streaks', username],       queryFn: () => getStreaks(username),       enabled: !!profileQ.data });
  const contribQ    = useQuery({ queryKey: ['contributions', username], queryFn: () => getContributions(username), enabled: !!profileQ.data });

  // ── Auto-sync when profile is not cached ────────────────────────────────
  useEffect(() => {
    if (profileQ.isError && !autoSyncDone && !syncing) {
      setAutoSyncDone(true); // prevent loops
      ensureSync(username).then((ok) => {
        if (ok) {
          // Refetch everything after successful sync
          qc.invalidateQueries({ queryKey: ['profile', username] });
          qc.invalidateQueries({ queryKey: ['analytics', username] });
          qc.invalidateQueries({ queryKey: ['languages', username] });
          qc.invalidateQueries({ queryKey: ['streaks', username] });
          qc.invalidateQueries({ queryKey: ['contributions', username] });
        }
      });
    }
  }, [profileQ.isError, autoSyncDone, syncing, username]);

  // ── Loading states ───────────────────────────────────────────────────────
  if (syncing || (profileQ.isLoading && !autoSyncDone)) {
    return (
      <div className="flex flex-col items-center justify-center py-32 gap-4">
        <Loader2 size={40} className="animate-spin text-blue-400" />
        <p className="text-slate-400 text-sm">
          {syncing ? `Syncing @${username} from GitHub…` : 'Loading profile…'}
        </p>
      </div>
    );
  }

  if (syncError) {
    return (
      <div className="max-w-md mx-auto py-24">
        <ErrorMessage message={syncError} onRetry={() => navigate('/')} />
        <p className="text-center text-slate-500 text-xs mt-4">
          Go back and check the GitHub username.
        </p>
      </div>
    );
  }

  if (profileQ.isError && autoSyncDone) {
    return (
      <div className="max-w-md mx-auto py-24">
        <ErrorMessage
          message={profileQ.error?.response?.data?.detail?.message || 'Profile not found.'}
          onRetry={() => navigate('/')}
        />
      </div>
    );
  }

  if (!profileQ.data) return null;

  const profile  = profileQ.data;
  const analytics = analyticsQ.data;

  const stats = [
    { icon: Users,    label: 'Followers',     value: formatNumber(analytics?.followers),           color: 'blue'   },
    { icon: BookOpen, label: 'Repositories',  value: formatNumber(analytics?.public_repos),         color: 'purple' },
    { icon: Star,     label: 'Total Stars',   value: formatNumber(analytics?.total_stars),           color: 'yellow' },
    { icon: GitFork,  label: 'Total Forks',   value: formatNumber(analytics?.total_forks),           color: 'green'  },
    { icon: Flame,    label: 'Contributions', value: formatNumber(analytics?.total_contributions),  color: 'red'    },
    { icon: Zap,      label: 'Following',     value: formatNumber(analytics?.following),             color: 'indigo' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">@{username}</h1>
          <p className="text-slate-400 text-sm mt-0.5">GitHub Developer Dashboard</p>
        </div>
        <div className="flex gap-2 flex-wrap">
          <Link to={`/vibe-check/${username}`} className="btn-secondary flex items-center gap-1.5">
            <Zap size={14} /> Vibe Check
          </Link>
          <Link to={`/portfolio/${username}`} className="btn-secondary flex items-center gap-1.5">
            <BookOpen size={14} /> Portfolio
          </Link>
          <button
            onClick={() => ensureSync(username).then((ok) => ok && qc.invalidateQueries())}
            disabled={syncing}
            className="btn-secondary flex items-center gap-1.5"
          >
            <RefreshCw size={14} className={syncing ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Profile + Stats */}
      <div className="grid lg:grid-cols-4 gap-4">
        <ProfileCard profile={profile} />
        <div className="lg:col-span-3 grid sm:grid-cols-2 xl:grid-cols-3 gap-4">
          {stats.map((s) => <StatCard key={s.label} {...s} />)}
        </div>
      </div>

      {/* Streaks */}
      {streaksQ.data && <StreakWidget data={streaksQ.data} />}

      {/* Languages + Heatmap */}
      <div className="grid lg:grid-cols-2 gap-4">
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Language Distribution</h2>
          {languagesQ.isLoading
            ? <Spinner />
            : <LanguageChart data={languagesQ.data?.languages || []} />}
        </div>
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Contribution Heatmap</h2>
          {contribQ.isLoading
            ? <Spinner />
            : <ContributionHeatmap data={contribQ.data?.contributions || []} />}
        </div>
      </div>

      {/* Repositories */}
      <div className="card">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-white">Repositories</h2>
          <span className="text-xs text-slate-400">⭐ = feature a repo for your portfolio</span>
        </div>
        <RepoList username={username} />
      </div>
    </div>
  );
}
