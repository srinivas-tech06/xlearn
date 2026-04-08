import { useState } from 'react';
import { useApp } from '../../context/AppContext';

export default function QuizCard({ quiz }) {
  const { actions } = useApp();
  const [selected, setSelected] = useState(null);
  const [answered, setAnswered] = useState(false);
  const [showExplanation, setShowExplanation] = useState(false);

  if (!quiz) return null;

  const correctOption = quiz.options.find(o => o.is_correct);
  const correctId = correctOption?.id || 'a';

  const handleSelect = async (optionId) => {
    if (answered) return;
    setSelected(optionId);
    setAnswered(true);
    setShowExplanation(true);

    await actions.submitQuizAnswer(
      quiz.question,
      optionId,
      correctId,
      ''
    );
  };

  const getOptionClass = (option) => {
    if (!answered) return selected === option.id ? 'selected' : '';
    if (option.is_correct) return 'correct';
    if (selected === option.id && !option.is_correct) return 'wrong';
    return '';
  };

  return (
    <div className="learning-card quiz-card">
      <div className="learning-card-header">
        <div className="learning-card-icon" style={{ background: 'rgba(124, 58, 237, 0.2)' }}>
          ❓
        </div>
        <div>
          <div className="learning-card-title">Quick Check</div>
          <div className="learning-card-subtitle">+{quiz.xp_reward} XP</div>
        </div>
      </div>

      <p style={{ fontSize: '0.9rem', fontWeight: 500, marginBottom: '4px' }}>
        {quiz.question}
      </p>

      <div className="quiz-options">
        {quiz.options.map((option) => (
          <button
            key={option.id}
            className={`quiz-option ${getOptionClass(option)}`}
            onClick={() => handleSelect(option.id)}
            disabled={answered}
          >
            <span className="quiz-option-letter">
              {answered && option.is_correct ? '✓' : answered && selected === option.id && !option.is_correct ? '✗' : option.id.toUpperCase()}
            </span>
            <span>{option.text}</span>
          </button>
        ))}
      </div>

      {showExplanation && quiz.explanation && (
        <div className="quiz-explanation">
          💡 {quiz.explanation}
        </div>
      )}
    </div>
  );
}
