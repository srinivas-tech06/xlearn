import { useState } from 'react';
import { useApp } from '../../context/AppContext';
import LLMStatusPanel from '../analytics/LLMStatusPanel';


const MENTOR_ICONS = { direct: '🎯', socratic: '🧠', storyteller: '📖', motivator: '🚀' };

const NAV_ITEMS = [
  { id: 'chat', icon: '💬', label: 'AI Chat' },
  { id: 'roadmap', icon: '🗺️', label: 'Roadmap' },
  { id: 'progress', icon: '📈', label: 'Progress' },
  { id: 'analytics', icon: '🔬', label: 'Analytics' },
];

export default function Sidebar() {
  const { state, actions } = useApp();
  const { currentPage, user, focusMode, mentor } = state;

  if (focusMode) return null;

  const xp = user?.xp || 0;
  const level = user?.level || 1;
  const xpInLevel = xp % 100;
  const levelTitles = { 1:'Novice',2:'Apprentice',3:'Scholar',4:'Practitioner',5:'Expert',6:'Master',7:'Grandmaster',8:'Legend' };
  const levelTitle = levelTitles[Math.min(level, 8)] || 'Legend';

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <div className="logo-icon">🧠</div>
        <span className="logo-text">AI Learning</span>
      </div>

      <nav className="sidebar-nav">
        {NAV_ITEMS.map(item => (
          <button
            key={item.id}
            className={`nav-item ${currentPage === item.id ? 'active' : ''}`}
            onClick={() => actions.setPage(item.id)}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
            {item.id === 'analytics' && (
              <span style={{ marginLeft: 'auto', fontSize:'0.6rem', background:'rgba(124,58,237,0.3)', padding:'2px 6px', borderRadius:'4px', color:'#c4b5fd' }}>NEW</span>
            )}
          </button>
        ))}
      </nav>

      {/* Mentor indicator */}
      <div className="sidebar-mentor-bar" onClick={() => actions.setPage('chat')}>
        <span className="smb-icon">{MENTOR_ICONS[mentor] || '🎯'}</span>
        <span className="smb-label">Mentor: <strong>{mentor.charAt(0).toUpperCase() + mentor.slice(1)}</strong></span>
      </div>

      {/* Focus Mode toggle */}
      <button className="focus-mode-btn" onClick={actions.toggleFocusMode}>
        🎯 Focus Mode
      </button>

      {/* XP bar */}
      <div className="sidebar-footer">
        <div className="sidebar-xp">
          <div className="xp-header">
            <span className="xp-level">LVL {level} — {levelTitle}</span>
            <span className="xp-value">{xpInLevel}/100 XP</span>
          </div>
          <div className="xp-bar-track">
            <div className="xp-bar-fill" style={{ width: `${xpInLevel}%` }} />
          </div>
        </div>
      </div>
    </aside>
  );
}
