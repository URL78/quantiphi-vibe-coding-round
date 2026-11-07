import axios from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: { 'Content-Type': 'application/json' },
});

// ── Profile ──────────────────────────────────────────────────────────────
export const syncProfile = (username, force_refresh = false) =>
  api.post('/profile/sync', { username, force_refresh }).then((r) => r.data);

export const getProfile = (username) =>
  api.get(`/profile/${username}`).then((r) => r.data);

export const refreshProfile = (username) =>
  api.post(`/profile/${username}/refresh`).then((r) => r.data);

// ── Analytics ────────────────────────────────────────────────────────────
export const getAnalytics = (username) =>
  api.get(`/analytics/${username}`).then((r) => r.data);

export const getLanguages = (username) =>
  api.get(`/analytics/${username}/languages`).then((r) => r.data);

// ── Contributions ────────────────────────────────────────────────────────
export const getContributions = (username, params = {}) =>
  api.get(`/contributions/${username}`, { params }).then((r) => r.data);

export const getStreaks = (username) =>
  api.get(`/contributions/${username}/streaks`).then((r) => r.data);

// ── Repositories ─────────────────────────────────────────────────────────
export const getRepositories = (username, params = {}) =>
  api.get(`/repositories/${username}`, { params }).then((r) => r.data);

export const getRepository = (username, repo) =>
  api.get(`/repositories/${username}/${repo}`).then((r) => r.data);

export const toggleFeatured = (username, repo, featured, display_order = 0) =>
  api.patch(`/repositories/${username}/${repo}/featured`, { featured, display_order }).then((r) => r.data);

// ── Vibe Check ───────────────────────────────────────────────────────────
export const analyzeCompatibility = (username, job_description) =>
  api.post('/compatibility/analyze', { username, job_description }).then((r) => r.data);

export const getAnalysis = (analysis_id) =>
  api.get(`/compatibility/${analysis_id}`).then((r) => r.data);

// ── Career ───────────────────────────────────────────────────────────────
export const getRecommendations = (analysis_id) =>
  api.get(`/career/recommendations/${analysis_id}`).then((r) => r.data);

// ── DeepWiki ─────────────────────────────────────────────────────────────
export const getWikiStructure = (owner, repo) =>
  api.get(`/deepwiki/${owner}/${repo}/structure`).then((r) => r.data);

export const askDeepWiki = (owner, repo, question) =>
  api.post(`/deepwiki/${owner}/${repo}/ask`, { question }).then((r) => r.data);

// ── Interview ────────────────────────────────────────────────────────────
export const generateInterviewQuestions = (payload) =>
  api.post('/interview/generate', payload).then((r) => r.data);

export const evaluateAnswer = (payload) =>
  api.post('/interview/evaluate', payload).then((r) => r.data);

// ── Settings ─────────────────────────────────────────────────────────────
export const getSettings = (username) =>
  api.get(`/settings/${username}`).then((r) => r.data);

export const updateSettings = (username, theme) =>
  api.put(`/settings/${username}`, { theme }).then((r) => r.data);

// ── Portfolio ────────────────────────────────────────────────────────────
export const getPortfolio = (username) =>
  api.get(`/portfolio/${username}`).then((r) => r.data);

export default api;
