import './index.css';
import { AppProvider, useApp } from './context/AppContext';
import Sidebar from './components/layout/Sidebar';
import TopBar from './components/layout/TopBar';
import ChatInterface from './components/chat/ChatInterface';
import RoadmapDashboard from './components/roadmap/RoadmapDashboard';
import ProgressDashboard from './components/progress/ProgressDashboard';
import AnalyticsPage from './pages/AnalyticsPage';
import OnboardingPage from './pages/OnboardingPage';
import XPNotification from './components/gamification/XPNotification';
import LevelUpModal from './components/gamification/LevelUpModal';

function AppContent() {
  const { state } = useApp();
  const { currentPage, focusMode } = state;

  if (currentPage === 'onboarding') return <OnboardingPage />;

  return (
    <div className={`app-layout ${focusMode ? 'focus-mode' : ''}`}>
      <Sidebar />
      <div className="main-content">
        <TopBar />
        <div className="page-content">
          {currentPage === 'chat'      && <ChatInterface />}
          {currentPage === 'roadmap'   && <RoadmapDashboard />}
          {currentPage === 'progress'  && <ProgressDashboard />}
          {currentPage === 'analytics' && <AnalyticsPage />}
        </div>
      </div>
      <XPNotification />
      <LevelUpModal />
    </div>
  );
}

export default function App() {
  return (
    <AppProvider>
      <AppContent />
    </AppProvider>
  );
}
