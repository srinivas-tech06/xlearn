import { useEffect, useState } from 'react';
import { useApp } from '../../context/AppContext';

const LEVEL_TITLES = {
  1: 'Novice', 2: 'Apprentice', 3: 'Scholar', 4: 'Practitioner',
  5: 'Expert', 6: 'Master', 7: 'Grandmaster', 8: 'Legend'
};

const CONFETTI_COLORS = ['#7c3aed', '#06b6d4', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#8b5cf6'];

export default function LevelUpModal() {
  const { state, actions } = useApp();
  const { levelUp } = state;
  const [confetti, setConfetti] = useState([]);

  useEffect(() => {
    if (levelUp) {
      const pieces = [];
      for (let i = 0; i < 60; i++) {
        pieces.push({
          id: i,
          left: Math.random() * 100,
          color: CONFETTI_COLORS[Math.floor(Math.random() * CONFETTI_COLORS.length)],
          delay: Math.random() * 2,
          duration: 2 + Math.random() * 3,
          size: 6 + Math.random() * 8,
        });
      }
      setConfetti(pieces);
    }
  }, [levelUp]);

  if (!levelUp) return null;

  const title = LEVEL_TITLES[Math.min(levelUp, 8)] || 'Legend';

  return (
    <>
      <div className="confetti-container">
        {confetti.map(c => (
          <div
            key={c.id}
            className="confetti"
            style={{
              left: `${c.left}%`,
              backgroundColor: c.color,
              width: `${c.size}px`,
              height: `${c.size}px`,
              animationDelay: `${c.delay}s`,
              animationDuration: `${c.duration}s`,
            }}
          />
        ))}
      </div>
      <div className="level-up-overlay" onClick={() => actions.hideLevelUp()}>
        <div className="level-up-modal" onClick={(e) => e.stopPropagation()}>
          <div className="level-up-icon">🏆</div>
          <div className="level-up-title">Level Up!</div>
          <div className="level-up-subtitle">
            You've reached <strong>Level {levelUp} — {title}</strong>
          </div>
          <p style={{ color: 'var(--text-tertiary)', fontSize: '0.9rem', marginBottom: '20px' }}>
            Keep up the amazing work! 🚀
          </p>
          <button className="btn btn-primary btn-lg" onClick={() => actions.hideLevelUp()}>
            Continue Learning
          </button>
        </div>
      </div>
    </>
  );
}
