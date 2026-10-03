import { useState, useEffect } from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { Header } from './components/Header';
import type { TabType } from './components/Header';
import { LoginModal } from './components/LoginModal';
import { OverviewPage } from './pages/OverviewPage';
import { ForecastPage } from './pages/ForecastPage';
import { ActivityPage } from './pages/ActivityPage';
import { SimulatePage } from './pages/SimulatePage';
import { InspectPage } from './pages/InspectPage';
import { Footer } from './components/Footer';
import { CalculationModal } from './components/CalculationModal';
import './App.css';

const TAB_STORAGE_KEY = 'spendable_active_tab';

const getInitialTab = (): TabType => {
  try {
    const hash = window.location.hash.replace('#', '').toLowerCase();
    if (['overview', 'activity', 'forecast', 'simulate', 'inspect'].includes(hash)) {
      return hash as TabType;
    }
    const stored = localStorage.getItem(TAB_STORAGE_KEY);
    if (stored && ['overview', 'activity', 'forecast', 'simulate', 'inspect'].includes(stored)) {
      return stored as TabType;
    }
  } catch {
    // fallback
  }
  return 'overview';
};

function MainApp() {
  const { isAuthenticated, isLoading, loginAsDemo } = useAuth();
  const [activeTab, setActiveTabState] = useState<TabType>(getInitialTab);
  const [showLoginModal, setShowLoginModal] = useState<boolean>(false);
  const [showCalcModal, setShowCalcModal] = useState<boolean>(false);

  const changeTab = (tab: TabType) => {
    setActiveTabState(tab);
    try {
      localStorage.setItem(TAB_STORAGE_KEY, tab);
      window.location.hash = tab;
    } catch {}
  };

  useEffect(() => {
    const handleHashChange = () => {
      const newTab = getInitialTab();
      setActiveTabState(newTab);
    };

    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const handleCloseLoginModal = async () => {
    setShowLoginModal(false);
    if (!isAuthenticated) {
      try {
        await loginAsDemo('acc_supan');
      } catch (err) {
        console.error('Failed fallback login on modal dismiss:', err);
      }
    }
  };

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
        setActiveTab={changeTab}
        onOpenLogin={() => setShowLoginModal(true)}
      />

      {/* Main Content Pane or Login Screen */}
      {!isAuthenticated || showLoginModal ? (
        <LoginModal
          isOpen={true}
          onClose={handleCloseLoginModal}
        />
      ) : (
        <main className="main-content">
          {activeTab === 'overview' && (
            <OverviewPage
              onNavigateTab={(tab) => changeTab(tab)}
              onOpenCalcModal={() => setShowCalcModal(true)}
            />
          )}

          {activeTab === 'activity' && <ActivityPage />}

          {activeTab === 'forecast' && <ForecastPage />}

          {activeTab === 'simulate' && <SimulatePage />}

          {activeTab === 'inspect' && <InspectPage />}
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
