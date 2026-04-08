import { useApp } from '../../context/AppContext';

const PRIORITY_STYLES = {
  urgent: { color: '#ef4444', bg: 'rgba(239,68,68,0.1)', label: '🔴 Overdue', border: 'rgba(239,68,68,0.3)' },
  today: { color: '#f59e0b', bg: 'rgba(245,158,11,0.1)', label: '🟡 Due Today', border: 'rgba(245,158,11,0.3)' },
  upcoming: { color: '#06b6d4', bg: 'rgba(6,182,212,0.1)', label: '🔵 Coming Up', border: 'rgba(6,182,212,0.3)' },
};

export default function SpacedRepCard({ reviews, weakTopics }) {
  const { actions } = useApp();

  const handleStartReview = (topic) => {
    actions.sendMessage(`Review and quiz me on: ${topic}`);
  };

  if ((!reviews || reviews.length === 0) && (!weakTopics || weakTopics.length === 0)) {
    return null;
  }

  return (
    <div className="spaced-rep-card">
      <div className="spc-header">
        <div className="spc-icon">🔄</div>
        <div>
          <div className="spc-title">Spaced Repetition</div>
          <div className="spc-subtitle">Topics due for review</div>
        </div>
      </div>

      {reviews && reviews.length > 0 && (
        <div className="spc-reviews">
          {reviews.slice(0, 3).map((review, i) => {
            const style = PRIORITY_STYLES[review.priority] || PRIORITY_STYLES.upcoming;
            return (
              <div key={i} className="spc-review-item" style={{ borderColor: style.border, background: style.bg }}>
                <div className="spc-review-top">
                  <span className="spc-priority-badge" style={{ color: style.color }}>{style.label}</span>
                  <span className="spc-strength">💪 {Math.round(review.strength * 100)}%</span>
                </div>
                <div className="spc-topic">{review.topic}</div>
                <button
                  className="spc-review-btn"
                  style={{ background: style.color }}
                  onClick={() => handleStartReview(review.topic)}
                >
                  Start Review →
                </button>
              </div>
            );
          })}
        </div>
      )}

      {weakTopics && weakTopics.length > 0 && (
        <div className="spc-weak">
          <div className="spc-weak-title">⚠️ Needs Attention</div>
          {weakTopics.slice(0, 3).map((t, i) => (
            <div key={i} className="spc-weak-item">
              <span className="spc-weak-topic">{t.topic}</span>
              <div className="spc-weak-bar">
                <div className="spc-weak-fill" style={{ width: `${t.strength * 100}%` }} />
              </div>
              <button className="spc-weak-btn" onClick={() => handleStartReview(t.topic)}>Review</button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
