'use client';

import React from 'react';
import { Button } from '@/components/ui/Button';
import { QuestionDifficulty, QuestionType } from '@/types/questions';

interface QuestionCardProps {
  id: string;
  content: string;
  questionType: QuestionType;
  difficulty: QuestionDifficulty;
  category: string;
  onSelect: (id: string) => void;
}

const QuestionCard: React.FC<QuestionCardProps> = ({
  id,
  content,
  questionType,
  difficulty,
  category,
  onSelect,
}) => {
  const getDifficultyColor = (difficulty: QuestionDifficulty) => {
    switch (difficulty) {
      case 'easy':
        return 'bg-green-100 text-green-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'hard':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getTypeColor = (type: QuestionType) => {
    switch (type) {
      case 'technical':
        return 'bg-purple-100 text-purple-800';
      case 'behavioral':
        return 'bg-blue-100 text-blue-800';
      case 'system_design':
        return 'bg-indigo-100 text-indigo-800';
      case 'coding':
        return 'bg-cyan-100 text-cyan-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-2">
        <div className="flex flex-wrap gap-2">
          <span className={`text-xs px-2 py-1 rounded ${getDifficultyColor(difficulty)}`}>
            {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
          </span>
          <span className={`text-xs px-2 py-1 rounded ${getTypeColor(questionType)}`}>
            {questionType.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
          </span>
          {category && (
            <span className="text-xs px-2 py-1 rounded bg-gray-100 text-gray-800">
              {category}
            </span>
          )}
        </div>
      </div>
      <p className="text-gray-800 mb-4 line-clamp-3">{content}</p>
      <Button 
        size="sm" 
        onClick={() => onSelect(id)}
        className="w-full"
      >
        Practice Question
      </Button>
    </div>
  );
};

export default QuestionCard;
