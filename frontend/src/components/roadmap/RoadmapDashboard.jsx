import { useEffect } from 'react';
import { useApp } from '../../context/AppContext';

export default function RoadmapDashboard() {
  const { state, actions } = useApp();
  const { roadmap } = state;

  useEffect(() => {
    actions.loadRoadmap();
  }, []);

  if (!roadmap) {
    return (
      <div style={{ textAlign: 'center', padding: '80px 20px', color: 'var(--text-tertiary)' }}>
        <div style={{ fontSize: '4rem', marginBottom: '16px' }}>🗺️</div>
        <h2 style={{ color: 'var(--text-secondary)', marginBottom: '8px' }}>No Roadmap Yet</h2>
        <p>Set a learning goal from the onboarding to generate your roadmap.</p>
      </div>
    );
  }

  const overallProgress = roadmap.overall_progress || 0;

  return (
    <div>
      <div className="roadmap-header">
        <div>
          <h1>🗺️ {roadmap.goal}</h1>
          <p style={{ color: 'var(--text-tertiary)', marginTop: '4px', fontSize: '0.9rem' }}>
            {roadmap.timeframe} • {roadmap.modules?.length || 0} modules
          </p>
        </div>
        <div className="roadmap-progress-overview">
          <span style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', whiteSpace: 'nowrap' }}>
            Overall: {Math.round(overallProgress)}%
          </span>
          <div className="roadmap-progress-bar-container">
            <div className="module-progress-bar">
              <div className="module-progress-fill" style={{ width: `${overallProgress}%` }} />
            </div>
          </div>
        </div>
      </div>

      <div className="roadmap-timeline">
        {(roadmap.modules || []).map((module, idx) => (
          <div key={idx} className={`module-card ${module.status}`} style={{ animationDelay: `${idx * 0.1}s` }}>
            <div className="module-card-header">
              <div>
                <div className="module-title">{module.title}</div>
                <div className="module-description">{module.description}</div>
              </div>
              <span className={`module-status-badge ${module.status}`}>
                {module.status === 'active' ? '▶ Active' : module.status === 'completed' ? '✓ Done' : '🔒 Locked'}
              </span>
            </div>

            <div className="module-progress-bar">
              <div className="module-progress-fill" style={{ width: `${module.progress || 0}%` }} />
            </div>

            <div className="module-topics">
              {(module.topics || []).map((topic, tidx) => (
                <div key={tidx} className="topic-item">
                  <div className={`topic-status-icon ${topic.status}`}>
                    {topic.status === 'completed' ? '✓' : ''}
                  </div>
                  <div className="topic-info">
                    <div className="topic-title">{topic.title}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
                      {topic.description}
                    </div>
                  </div>
                  <span className="topic-xp">+{topic.xp_reward} XP</span>
                </div>
              ))}
            </div>

            <div className="module-meta">
              <span>⏱️ ~{module.estimated_hours}h</span>
              <span>📖 {module.topics?.length || 0} topics</span>
              <span>📈 {Math.round(module.progress || 0)}% complete</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
