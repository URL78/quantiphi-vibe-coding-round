// Shared formatting utilities
export const formatNumber = (n) => {
  if (n === null || n === undefined) return '0';
  if (n >= 1000) return `${(n / 1000).toFixed(1)}k`;
  return String(n);
};

export const timeAgo = (dateStr) => {
  if (!dateStr) return 'Never';
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  const days = Math.floor(hrs / 24);
  return `${days}d ago`;
};

export const pct = (val) => (val === null || val === undefined ? 'N/A' : `${val.toFixed(1)}%`);

// Tailwind colour classes per language (for charts / badges)
export const LANG_COLORS = {
  Python: '#3b82f6',
  JavaScript: '#f59e0b',
  TypeScript: '#6366f1',
  Java: '#ef4444',
  'C++': '#8b5cf6',
  C: '#64748b',
  'C#': '#10b981',
  Go: '#06b6d4',
  Rust: '#f97316',
  Ruby: '#dc2626',
  PHP: '#7c3aed',
  Kotlin: '#a855f7',
  Swift: '#f97316',
  Scala: '#dc2626',
  Shell: '#16a34a',
  HTML: '#ea580c',
  CSS: '#2563eb',
  default: '#6b7280',
};

export const getLangColor = (lang) => LANG_COLORS[lang] || LANG_COLORS.default;
