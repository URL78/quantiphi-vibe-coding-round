import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { getProfile, getAnalytics, getLanguages, getStreaks, getContributions } from '../services/api';
import Spinner from '../components/common/Spinner';
import ErrorMessage from '../components/common/ErrorMessage';
import StatCard from '../components/common/StatCard';
import ProfileCard from '../components/dashboard/ProfileCard';
import LanguageChart from '../components/dashboard/LanguageChart';
import ContributionHeatmap from '../components/dashboard/ContributionHeatmap';
import StreakWidget from '../components/dashboard/StreakWidget';
import RepoList from '../components/dashboard/RepoList';
import { Users, Star, GitFork, BookOpen, Flame, Zap } from 'lucide-react';
import { formatNumber } from '../utils/format';

export default function DashboardPage() {
  const { username } = useParams();

  const profileQ = useQuery({ queryKey: ['profile', username], queryFn: () => getProfile(username) });
  const analyticsQ = useQuery({ queryKey: ['analytics', username], queryFn: () => getAnalytics(username) });
  const languagesQ = useQuery({ queryKey: ['languages', username], queryFn: () => getLanguages(username) });
  const streaksQ = useQuery({ queryKey: ['streaks', username], queryFn: () => getStreaks(username) });
  const contribQ = useQuery({ queryKey: ['contributions', username], queryFn: () => getContributions(username) });

  const isLoading = profileQ.isLoading || analyticsQ.isLoading;
  const isError = profileQ.isError || analyticsQ.isError;

  if (isLoading) return <div className="py-24"><Spinner size={40} /></div>;
  if (isError) return <div className="py-24"><ErrorMessage message={profileQ.error?.response?.data?.detail?.message || 'Failed to load profile.'} /></div>;

  const profile = profileQ.data;
  const analytics = analyticsQ.data;
  const stats = [
    { icon: Users,    label: 'Followers',      value: formatNumber(analytics?.followers),           color: 'blue'   },
    { icon: BookOpen, label: 'Repositories',   value: formatNumber(analytics?.public_repos),        color: 'purple' },
    { icon: Star,     label: 'Total Stars',    value: formatNumber(analytics?.total_stars),          color: 'yellow' },
    { icon: GitFork,  label: 'Total Forks',    value: formatNumber(analytics?.total_forks),          color: 'green'  },
    { icon: Flame,    label: 'Contributions',  value: formatNumber(analytics?.total_contributions), color: 'red'    },
    { icon: Zap,      label: 'Following',      value: formatNumber(analytics?.following),            color: 'indigo' },
  ];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8 space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between flex-wrap gap-3">
        <h1 className="text-2xl font-bold text-white">Dashboard — @{username}</h1>
        <div className="flex gap-2">
          <Link to={`/vibe-check/${username}`} className="btn-secondary flex items-center gap-1.5">
            <Zap size={14} /> Vibe Check
          </Link>
        </div>
      </div>

      {/* Profile + Stats */}
      <div className="grid lg:grid-cols-4 gap-4">
        <div className="lg:col-span-1">
          <ProfileCard profile={profile} />
        </div>
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
          {languagesQ.isLoading ? <Spinner /> : <LanguageChart data={languagesQ.data?.languages || []} />}
        </div>
        <div className="card">
          <h2 className="text-lg font-semibold text-white mb-4">Contribution Heatmap</h2>
          {contribQ.isLoading ? <Spinner /> : <ContributionHeatmap data={contribQ.data?.contributions || []} />}
        </div>
      </div>

      {/* Repositories */}
      <div className="card">
        <h2 className="text-lg font-semibold text-white mb-4">Repositories</h2>
        <RepoList username={username} />
      </div>
    </div>
  );
}
