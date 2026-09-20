import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { LanguageProvider } from './context/LanguageContext';
import { GovernmentUtilityBar } from './components/government/GovernmentUtilityBar';
import { InstitutionalHeader } from './components/branding/InstitutionalHeader';
import { MainNavigation } from './components/navigation/MainNavigation';
import { SystemInfoStrip } from './components/government/SystemInfoStrip';
import { HomePage } from './pages/Home';
import { DetectionPage } from './pages/Detection';
import { ForensicsPage } from './pages/Forensics';
import { AnalyticsPage } from './pages/Analytics';
import { DashboardPage } from './pages/Dashboard';
import { AboutPage } from './pages/About';
import ScreeningPage from './pages/Screening';
import InvestigationsPage from './pages/Investigations';
import IdentityIntelligencePage from './pages/IdentityIntelligence';
import AuditTrailPage from './pages/AuditTrail';

function App() {
  const [fontScale, setFontScale] = useState(1);

  // Apply font scale to :root CSS custom property
  useEffect(() => {
    document.documentElement.style.setProperty('--fs-scale', String(fontScale));
  }, [fontScale]);

  return (
    <LanguageProvider>
      <BrowserRouter>
        {/* Skip link */}
        <a href="#main-content" className="skip-link">Skip to main content</a>

        {/* Government Utility Bar — fixed at very top */}
        <GovernmentUtilityBar onFontScale={setFontScale} currentScale={fontScale} />

        {/* Institutional Header */}
        <InstitutionalHeader />

        {/* Primary Navigation */}
        <MainNavigation />

        {/* System Info Strip */}
        <SystemInfoStrip />

        {/* Page Routes */}
        <Routes>
          {/* Root redirects to home */}
          <Route path="/" element={<Navigate to="/home" replace />} />

          {/* PS 26188 — Primary Routes */}
          <Route path="/home" element={<HomePage />} />
          <Route path="/screening" element={<ScreeningPage />} />
          <Route path="/investigations" element={<InvestigationsPage />} />
          <Route path="/forensics" element={<ForensicsPage />} />
          <Route path="/identity" element={<IdentityIntelligencePage />} />
          <Route path="/analytics" element={<AnalyticsPage />} />
          <Route path="/audit" element={<AuditTrailPage />} />
          <Route path="/about" element={<AboutPage />} />

          {/* Legacy/preserved routes */}
          <Route path="/detection" element={<DetectionPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />

          {/* Fallback */}
          <Route path="*" element={
            <main id="main-content" tabIndex={-1} style={{ padding: '48px 24px', textAlign: 'center' }}>
              <h1 style={{ fontSize: '24px', color: 'var(--c-navy)', marginBottom: '12px' }}>Page not found</h1>
              <p style={{ color: 'var(--c-text-muted)' }}>The requested page does not exist.</p>
              <a href="/home" className="btn-primary" style={{ display: 'inline-flex', marginTop: '20px' }}>← Return to Home</a>
            </main>
          } />
        </Routes>
      </BrowserRouter>
    </LanguageProvider>
  );
}

export default App;
