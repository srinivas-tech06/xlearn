import { useState } from 'react';
import { useApp } from '../../context/AppContext';

const MENTORS = [
  {
    id: 'direct',
    name: 'Direct',
    icon: '🎯',
    tagline: 'Precise & Structured',
    description: 'Clear bullet points, facts first, no fluff. Perfect for efficient learning.',
    color: '#06b6d4',
    gradient: 'linear-gradient(135deg, #0891b2, #06b6d4)',
  },
  {
    id: 'socratic',
    name: 'Socratic',
    icon: '🧠',
    tagline: 'Guided Discovery',
    description: 'Learns through questions. Never gives answers — you discover them yourself.',
    color: '#7c3aed',
    gradient: 'linear-gradient(135deg, #6d28d9, #7c3aed)',
  },
  {
    id: 'storyteller',
    name: 'Storyteller',
    icon: '📖',
    tagline: 'Analogies & Stories',
    description: 'Explains through vivid real-world analogies and memorable narratives.',
    color: '#f59e0b',
    gradient: 'linear-gradient(135deg, #d97706, #f59e0b)',
  },
  {
    id: 'motivator',
    name: 'Motivator',
    icon: '🚀',
    tagline: 'Energetic & Uplifting',
    description: 'Builds confidence first. Celebrates wins and pushes through struggles.',
    color: '#10b981',
    gradient: 'linear-gradient(135deg, #059669, #10b981)',
  },
];

export default function MentorSelector({ onClose }) {
  const { state, actions } = useApp();
  const { mentor: activeMentor } = state;

  return (
    <div className="mentor-overlay" onClick={onClose}>
      <div className="mentor-panel" onClick={(e) => e.stopPropagation()}>
        <div className="mentor-panel-header">
          <h2>Choose Your AI Mentor</h2>
          <p>Your mentor's personality shapes how the AI teaches you.</p>
          <button className="mentor-close-btn" onClick={onClose}>✕</button>
        </div>
        <div className="mentor-grid">
          {MENTORS.map((m) => (
            <button
              key={m.id}
              className={`mentor-card ${activeMentor === m.id ? 'active' : ''}`}
              style={{ '--mentor-color': m.color, '--mentor-gradient': m.gradient }}
              onClick={() => { actions.setMentor(m.id); onClose(); }}
            >
              <div className="mentor-avatar">{m.icon}</div>
              <div className="mentor-info">
                <div className="mentor-name">{m.name}</div>
                <div className="mentor-tagline">{m.tagline}</div>
                <div className="mentor-desc">{m.description}</div>
              </div>
              {activeMentor === m.id && (
                <div className="mentor-active-badge">✓ Active</div>
              )}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
