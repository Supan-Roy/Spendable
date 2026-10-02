import { useState } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Header } from './components/Header';
import type { TabType } from './components/Header';
import { LoginModal } from './components/LoginModal';
import { OverviewPage } from './pages/OverviewPage';
import { ForecastPage } from './pages/ForecastPage';
import { ActivityPage } from './pages/ActivityPage';
import { SimulatePage } from './pages/SimulatePage';
import { Footer } from './components/Footer';
import { CalculationModal } from './components/CalculationModal';
import './App.css';

function MainApp() {
  const { isAuthenticated, isLoading } = useAuth();
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [showLoginModal, setShowLoginModal] = useState<boolean>(false);
  const [showCalcModal, setShowCalcModal] = useState<boolean>(false);

  if (isLoading) {
    return (
      <div className="container app-loading-screen">
        <div className="app-loading-badge">
          <img src="/logo.svg" alt="Spendable Logo" className="logo-img spinning" draggable={false} />
          <span>Initializing Spendable Intelligence...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="container">
      {/* Top Application Header */}
      <Header
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenLogin={() => setShowLoginModal(true)}
      />

      {/* Main Content Pane or Login Screen */}
      {!isAuthenticated || showLoginModal ? (
        <LoginModal
          isOpen={true}
          onClose={isAuthenticated ? () => setShowLoginModal(false) : undefined}
          canClose={isAuthenticated}
        />
      ) : (
        <main className="main-content">
          {activeTab === 'overview' && (
            <OverviewPage
              onNavigateTab={(tab) => setActiveTab(tab)}
              onOpenCalcModal={() => setShowCalcModal(true)}
            />
          )}

          {activeTab === 'activity' && <ActivityPage />}

          {activeTab === 'forecast' && <ForecastPage />}

          {activeTab === 'simulate' && <SimulatePage />}
        </main>
      )}

      {/* Formula Explanation Modal */}
      <CalculationModal
        isOpen={showCalcModal}
        onClose={() => setShowCalcModal(false)}
      />

      {/* Product Footer */}
      <Footer />
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
