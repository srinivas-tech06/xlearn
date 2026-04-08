import { useApp } from '../../context/AppContext';

const PAGE_TITLES = {
  chat: '🧠 AI Learning Assistant',
  roadmap: '🗺️ Learning Roadmap',
  progress: '📈 Progress Dashboard',
  analytics: '🔬 Learning Analytics',
};

const MENTOR_CONFIG = {
  direct: { icon: '🎯', name: 'Direct', color: '#06b6d4' },
  socratic: { icon: '🧠', name: 'Socratic', color: '#7c3aed' },
  storyteller: { icon: '📖', name: 'Storyteller', color: '#f59e0b' },
  motivator: { icon: '🚀', name: 'Motivator', color: '#10b981' },
};

export default function TopBar() {
  const { state, actions } = useApp();
  const { currentPage, user, focusMode, mentor, ragSources } = state;

  const mentorCfg = MENTOR_CONFIG[mentor] || MENTOR_CONFIG.direct;
  const initial = user?.name?.[0]?.toUpperCase() || 'L';

  return (
    <header className={`topbar ${focusMode ? 'topbar-focus' : ''}`}>
      <div className="topbar-left">
        {focusMode && (
          <div className="focus-logo">🧠</div>
        )}
        <span className="topbar-title">{PAGE_TITLES[currentPage] || 'AI Learning'}</span>
      </div>

      <div className="topbar-right">
        {/* RAG indicator */}
        {ragSources && ragSources.length > 0 && (
          <div className="rag-indicator" title={`Knowledge retrieved: ${ragSources.map(s=>s.topic).join(', ')}`}>
            <span>⚡</span>
            <span>RAG Active</span>
          </div>
        )}

        {/* Mentor badge */}
        {currentPage === 'chat' && (
          <div className="mentor-badge" style={{ '--mentor-color': mentorCfg.color }}>
            <span>{mentorCfg.icon}</span>
            <span>{mentorCfg.name}</span>
          </div>
        )}

        {/* Streak */}
        {user?.streak > 0 && (
          <div className="streak-badge">
            🔥 {user.streak} day streak
          </div>
        )}

        {/* Focus mode toggle */}
        {focusMode && (
          <button className="exit-focus-btn" onClick={actions.toggleFocusMode}>
            Exit Focus
          </button>
        )}

        <div className="user-avatar">{initial}</div>
      </div>
    </header>
  );
}
