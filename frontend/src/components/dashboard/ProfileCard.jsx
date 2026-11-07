import React from 'react';
import { MapPin, Link2, Users } from 'lucide-react';

export default function ProfileCard({ profile }) {
  if (!profile) return null;
  return (
    <div className="card flex flex-col items-center text-center gap-3 h-full">
      <img
        src={profile.avatar_url}
        alt={profile.github_username}
        className="w-24 h-24 rounded-full ring-2 ring-blue-500/40"
      />
      <div>
        <h2 className="text-xl font-bold text-white">{profile.name || profile.github_username}</h2>
        <a
          href={profile.github_url}
          target="_blank"
          rel="noreferrer"
          className="text-blue-400 text-sm hover:underline"
        >
          @{profile.github_username}
        </a>
      </div>
      {profile.bio && <p className="text-sm text-slate-400 leading-relaxed">{profile.bio}</p>}
      <div className="flex gap-4 text-sm text-slate-400">
        <span className="flex items-center gap-1"><Users size={13} /> {profile.followers} followers</span>
        <span>· {profile.following} following</span>
      </div>
      {profile.is_stale && (
        <span className="badge bg-yellow-500/15 text-yellow-400 border border-yellow-500/20 text-xs">Cache stale</span>
      )}
    </div>
  );
}
