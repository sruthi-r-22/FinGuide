import React, { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Layout/Sidebar';
import Navbar from './components/Layout/Navbar';
import Footer from './components/Layout/Footer';

// Pages
import HomePage from './pages/HomePage';
import ChatPage from './pages/ChatPage';
import GlossaryPage from './pages/GlossaryPage';
import ChecklistPage from './pages/ChecklistPage';
import ScamAwarenessPage from './pages/ScamAwarenessPage';
import ComparisonsPage from './pages/ComparisonsPage';
import SourcesPage from './pages/SourcesPage';
import AboutPage from './pages/AboutPage';

export default function App() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  return (
    <Router>
      <div className="min-h-screen bg-slate-50 flex flex-col font-sans text-slate-900 antialiased">
        {/* Sidebar */}
        <Sidebar
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />

        {/* Main Application Area (offset by sidebar width on large screens) */}
        <div className="lg:pl-72 flex flex-col min-h-screen">
          <Navbar onToggleSidebar={() => setIsSidebarOpen(!isSidebarOpen)} />

          <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/glossary" element={<GlossaryPage />} />
              <Route path="/checklist" element={<ChecklistPage />} />
              <Route path="/scam-awareness" element={<ScamAwarenessPage />} />
              <Route path="/comparisons" element={<ComparisonsPage />} />
              <Route path="/sources" element={<SourcesPage />} />
              <Route path="/about" element={<AboutPage />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>

          <Footer />
        </div>
      </div>
    </Router>
  );
}
