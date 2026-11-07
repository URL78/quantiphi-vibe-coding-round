import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Code2, LayoutDashboard, FileText, Zap, BrainCircuit, Home } from 'lucide-react';
import { useApp } from '../../context/AppContext';

const NAV = [
  { to: '/', label: 'Home', icon: Home },
  { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { to: '/portfolio', label: 'Portfolio', icon: FileText },
  { to: '/vibe-check', label: 'Vibe Check', icon: Zap },
  { to: '/deepwiki', label: 'DeepWiki AI', icon: BrainCircuit },
];

export default function Navbar() {
  const { currentUser } = useApp();
  const location = useLocation();

  return (
    <header className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur border-b border-slate-800">
      <div className="max-w-7xl mx-auto px-4 h-14 flex items-center justify-between gap-4">
        {/* Logo */}
        <Link to="/" className="flex items-center gap-2 font-bold text-blue-400 shrink-0">
          <Code2 size={22} />
          <span className="hidden sm:inline">DevPortfolio</span>
        </Link>

        {/* Nav links */}
        <nav className="flex items-center gap-1 overflow-x-auto">
          {NAV.map(({ to, label, icon: Icon }) => {
            const active = location.pathname === to || (to !== '/' && location.pathname.startsWith(to));
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-sm font-medium transition whitespace-nowrap
                  ${active ? 'bg-blue-600 text-white' : 'text-slate-400 hover:text-white hover:bg-slate-800'}`}
              >
                <Icon size={15} />
                <span className="hidden md:inline">{label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Current user */}
        {currentUser && (
          <span className="text-xs text-slate-400 shrink-0 hidden sm:block">
            @{currentUser}
          </span>
        )}
      </div>
    </header>
  );
}
