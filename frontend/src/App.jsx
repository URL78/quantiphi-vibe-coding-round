import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AppProvider } from './context/AppContext';
import Navbar from './components/common/Navbar';
import HomePage from './pages/HomePage';
import DashboardPage from './pages/DashboardPage';
import PortfolioPage from './pages/PortfolioPage';
import VibeCheckPage from './pages/VibeCheckPage';
import DeepWikiPage from './pages/DeepWikiPage';

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: 1, staleTime: 5 * 60 * 1000 } },
});

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppProvider>
        <BrowserRouter>
          <div className="min-h-screen flex flex-col">
            <Navbar />
            <main className="flex-1">
              <Routes>
                <Route path="/" element={<HomePage />} />
                <Route path="/dashboard" element={<Navigate to="/" replace />} />
                <Route path="/dashboard/:username" element={<DashboardPage />} />
                <Route path="/portfolio" element={<Navigate to="/" replace />} />
                <Route path="/portfolio/:username" element={<PortfolioPage />} />
                <Route path="/vibe-check" element={<VibeCheckPage />} />
                <Route path="/vibe-check/:username" element={<VibeCheckPage />} />
                <Route path="/deepwiki" element={<DeepWikiPage />} />
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </main>
            <footer className="text-center py-4 text-xs text-slate-600 border-t border-slate-800">
              GitHub Developer Portfolio · Built for Quantiphi Vibe Coding Assessment
            </footer>
          </div>
        </BrowserRouter>
      </AppProvider>
    </QueryClientProvider>
  );
}
