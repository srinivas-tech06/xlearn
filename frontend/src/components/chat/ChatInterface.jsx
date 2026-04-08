import { useState, useRef, useEffect } from 'react';
import { useApp } from '../../context/AppContext';
import QuizCard from '../learning/QuizCard';
import FeedbackCard from '../learning/FeedbackCard';
import SpacedRepCard from '../learning/SpacedRepCard';
import MentorSelector from './MentorSelector';

const QUICK_ACTIONS = [
  { label: '📚 Explain', message: 'Explain the next topic in my roadmap' },
  { label: '🧠 Quiz me', message: 'Quiz me on what I just learned' },
  { label: '🔥 Challenge', message: 'Give me an advanced challenge question' },
  { label: '📝 Review', message: 'Let me review previous concepts' },
  { label: '🔄 Revise', message: 'Start a spaced repetition revision session' },
  { label: '💪 Motivate', message: 'I need some motivation to keep going' },
];

const MENTOR_COLORS = { direct: '#06b6d4', socratic: '#7c3aed', storyteller: '#f59e0b', motivator: '#10b981' };

export default function ChatInterface() {
  const { state, actions } = useApp();
  const { chatMessages, loading, currentQuiz, studentState, mentor, memoryData, focusMode } = state;
  const [input, setInput] = useState('');
  const [showMentorSelector, setShowMentorSelector] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages, loading]);

  useEffect(() => {
    // Load memory on mount
    actions.loadMemory();
  }, []);

  const handleSend = async () => {
    if (!input.trim() || loading) return;
    const msg = input.trim();
    setInput('');
    await actions.sendMessage(msg);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const renderMessageContent = (msg) => {
    const content = msg.content || '';
    const lines = content.split('\n');
    const elements = [];
    let i = 0;

    for (const line of lines) {
      i++;
      if (line.startsWith('🧠 **EXPLANATION**') || line.startsWith('❓ **QUICK CHECK**') || line.startsWith('📊 **YOUR PROGRESS**') || line.startsWith('⚡ **NEXT STEP**')) {
        elements.push(
          <div key={i} className="response-section-header">
            {line.replace(/\*\*/g, '')}
          </div>
        );
      } else if (line.startsWith('## ')) {
        elements.push(<h2 key={i}>{line.replace(/^##\s+/, '')}</h2>);
      } else if (line.startsWith('# ')) {
        elements.push(<h1 key={i} style={{fontSize:'1.1rem',fontWeight:700,color:'var(--accent-tertiary)',margin:'12px 0 6px'}}>{line.replace(/^#\s+/, '')}</h1>);
      } else if (line.startsWith('> ')) {
        elements.push(
          <blockquote key={i} style={{ borderLeft: '3px solid var(--accent-primary)', paddingLeft: '12px', color: 'var(--text-secondary)', fontStyle: 'italic', margin: '8px 0' }}>
            {line.slice(2)}
          </blockquote>
        );
      } else if (line.startsWith('```')) {
        continue;
      } else if (line.startsWith('- ') || line.startsWith('* ')) {
        const text = line.slice(2);
        const parts = text.split(/(\*\*.*?\*\*)/g);
        elements.push(
          <p key={i} style={{ paddingLeft: '16px', margin: '2px 0' }}>
            • {parts.map((p, j) => p.startsWith('**') && p.endsWith('**') ? <strong key={j}>{p.slice(2,-2)}</strong> : p)}
          </p>
        );
      } else if (line.match(/^\d+\.\s/)) {
        elements.push(<p key={i} style={{ paddingLeft: '16px', margin: '2px 0' }}>{line}</p>);
      } else if (line.startsWith('→ ')) {
        elements.push(
          <div key={i} className="next-step-action">
            {line}
          </div>
        );
      } else if (line.trim()) {
        const parts = line.split(/(\*\*.*?\*\*)/g);
        elements.push(
          <p key={i} style={{ margin: '3px 0' }}>
            {parts.map((p, j) => p.startsWith('**') && p.endsWith('**') ? <strong key={j}>{p.slice(2,-2)}</strong> : p)}
          </p>
        );
      } else {
        elements.push(<br key={i} />);
      }
    }
    return elements;
  };

  const dueReviews = memoryData?.due_reviews || [];
  const weakTopics = memoryData?.weak_topics || [];
  const mentorColor = MENTOR_COLORS[mentor] || '#06b6d4';
  const urgentReviews = dueReviews.filter(r => r.priority === 'urgent');

  return (
    <>
      {showMentorSelector && <MentorSelector onClose={() => setShowMentorSelector(false)} />}

      <div className={`chat-container ${focusMode ? 'focus-mode-chat' : ''}`}>
        <div className="chat-main">
          {/* Mentor header bar */}
          <div className="chat-mentor-bar" style={{ '--mentor-color': mentorColor }}>
            <button className="cmb-mentor-btn" onClick={() => setShowMentorSelector(true)}>
              <span className="cmb-icon">{['direct','socratic','storyteller','motivator'].includes(mentor) ? {direct:'🎯',socratic:'🧠',storyteller:'📖',motivator:'🚀'}[mentor] : '🎯'}</span>
              <span className="cmb-name">{mentor.charAt(0).toUpperCase()+mentor.slice(1)} Mentor</span>
              <span className="cmb-change">Change ↓</span>
            </button>
            {urgentReviews.length > 0 && (
              <div className="cmb-review-alert">
                ⚠️ {urgentReviews.length} review{urgentReviews.length > 1 ? 's' : ''} overdue
              </div>
            )}
          </div>

          <div className="chat-messages">
            {chatMessages.length === 0 && (
              <div className="chat-welcome">
                <div className="cw-brain">🧠</div>
                <h2>Welcome to AI Powered Learning</h2>
                <p>Powered by RAG • Long-term Memory • Spaced Repetition</p>
                <div className="cw-tags">
                  <span>🎯 Adaptive</span>
                  <span>📚 RAG Knowledge</span>
                  <span>🔄 Spaced Repetition</span>
                  <span>🧠 Memory</span>
                </div>
              </div>
            )}

            {chatMessages.map((msg, idx) => (
              <div key={idx} className={`chat-bubble ${msg.role}`}>
                <div className="bubble-header">
                  {msg.role === 'assistant' ? '🧠 AI Mentor' : '👤 You'}
                  {msg.ragSources && msg.ragSources.length > 0 && (
                    <span className="rag-badge" title={msg.ragSources.map(s=>s.topic).join(', ')}>
                      ⚡ RAG
                    </span>
                  )}
                  <span style={{ marginLeft: 'auto', fontSize: '0.65rem' }}>
                    {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </span>
                </div>
                <div className="bubble-content">{renderMessageContent(msg)}</div>
              </div>
            ))}

            {loading && (
              <div className="typing-indicator">
                <div className="typing-dot" />
                <div className="typing-dot" />
                <div className="typing-dot" />
                <span style={{marginLeft:'8px',fontSize:'0.75rem',color:'var(--text-tertiary)'}}>
                  AI thinking...
                </span>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {!currentQuiz && (
            <div className="quick-actions">
              {QUICK_ACTIONS.map((action, idx) => (
                <button key={idx} className="quick-action-chip" onClick={() => actions.sendMessage(action.message)}>
                  {action.label}
                </button>
              ))}
            </div>
          )}

          <div className="chat-input-area">
            <input
              id="chat-input"
              className="chat-input"
              type="text"
              placeholder={`Ask your ${mentor} mentor anything... (e.g., 'Explain Python loops')`}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading}
            />
            <button id="chat-send" className="chat-send-btn" onClick={handleSend} disabled={loading}>
              {loading ? '⏳' : '➤'}
            </button>
          </div>
        </div>

        {!focusMode && (
          <div className="chat-sidebar">
            {currentQuiz && <QuizCard quiz={currentQuiz} />}
            <FeedbackCard state={studentState} />
            {(dueReviews.length > 0 || weakTopics.length > 0) && (
              <SpacedRepCard reviews={dueReviews} weakTopics={weakTopics} />
            )}
          </div>
        )}
      </div>
    </>
  );
}
