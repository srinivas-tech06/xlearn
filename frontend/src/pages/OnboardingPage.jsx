import { useState } from 'react';
import { useApp } from '../context/AppContext';

const SUGGESTIONS = [
  { label: '🐍 Python Programming', value: 'Learn Python Programming' },
  { label: '🌐 Web Development', value: 'Learn Web Development' },
  { label: '🤖 Machine Learning', value: 'Learn Machine Learning' },
  { label: '📱 React.js', value: 'Learn React.js' },
  { label: '🗃️ SQL & Databases', value: 'Learn SQL and Databases' },
  { label: '☁️ Cloud Computing', value: 'Learn Cloud Computing' },
];

export default function OnboardingPage() {
  const { actions } = useApp();
  const [goal, setGoal] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState(1);

  const handleStart = async () => {
    if (!goal.trim()) return;
    setLoading(true);

    try {
      // Create user
      actions.setUser({ id: 1, name: name || 'Learner', level: 1, xp: 0, streak: 0, total_sessions: 0, current_goal: goal });

      // Generate roadmap
      await actions.generateRoadmap(goal);

      // Navigate to chat
      actions.setPage('chat');
    } catch (e) {
      console.error('Onboarding error:', e);
      // Even if backend fails, proceed to chat
      actions.setPage('chat');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="onboarding-container">
      <div className="onboarding-card">
        <div className="onboarding-logo">
          <div className="logo-icon">🧠</div>
          <span className="logo-text">AI Learning</span>
        </div>

        {step === 1 && (
          <>
            <h2 className="onboarding-title">Welcome, Future Expert! 🚀</h2>
            <p className="onboarding-subtitle">
              Your AI-powered learning journey starts here. Let's personalize your experience.
            </p>

            <input
              id="onboarding-name"
              className="onboarding-input"
              type="text"
              placeholder="What's your name?"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />

            <button
              className="onboarding-start-btn"
              onClick={() => setStep(2)}
              style={{ marginTop: '8px' }}
            >
              Continue →
            </button>
          </>
        )}

        {step === 2 && (
          <>
            <h2 className="onboarding-title">
              {name ? `Hey ${name}!` : 'Hey!'} What do you want to learn? 🎯
            </h2>
            <p className="onboarding-subtitle">
              Tell us your learning goal and we'll create a personalized roadmap with AI-powered guidance.
            </p>

            <input
              id="onboarding-goal"
              className="onboarding-input"
              type="text"
              placeholder="e.g., Learn Python Programming"
              value={goal}
              onChange={(e) => setGoal(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleStart()}
            />

            <div className="onboarding-suggestions">
              {SUGGESTIONS.map((s, i) => (
                <button
                  key={i}
                  className="suggestion-chip"
                  onClick={() => setGoal(s.value)}
                >
                  {s.label}
                </button>
              ))}
            </div>

            <button
              id="onboarding-start"
              className="onboarding-start-btn"
              onClick={handleStart}
              disabled={!goal.trim() || loading}
            >
              {loading ? '🧠 Creating your roadmap...' : '🚀 Start Learning'}
            </button>
          </>
        )}

        <div style={{ textAlign: 'center', marginTop: '24px' }}>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-tertiary)' }}>
            Powered by 6 coordinated AI agents • Adaptive learning • Gamified experience
          </p>
        </div>
      </div>
    </div>
  );
}
