'use client';

import React from 'react';
import { QuestionDifficulty, QuestionType, Category } from '@/types/questions';

interface QuestionFilterBarProps {
  categories: Category[];
  selectedCategory: string | null;
  selectedDifficulty: QuestionDifficulty | null;
  selectedType: QuestionType | null;
  onCategoryChange: (category: string | null) => void;
  onDifficultyChange: (difficulty: QuestionDifficulty | null) => void;
  onTypeChange: (type: QuestionType | null) => void;
  onSearchChange: (search: string) => void;
}

const QuestionFilterBar: React.FC<QuestionFilterBarProps> = ({
  categories,
  selectedCategory,
  selectedDifficulty,
  selectedType,
  onCategoryChange,
  onDifficultyChange,
  onTypeChange,
  onSearchChange,
}) => {
  const difficulties: QuestionDifficulty[] = ['easy', 'medium', 'hard'];
  const types: QuestionType[] = ['technical', 'behavioral', 'system_design', 'coding', 'general'];

  return (
    <div className="bg-white rounded-lg shadow p-4 mb-6">
      <div className="mb-4">
        <input
          type="text"
          placeholder="Search questions..."
          className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          onChange={(e) => onSearchChange(e.target.value)}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Category Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Category
          </label>
          <select
            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={selectedCategory || ''}
            onChange={(e) => onCategoryChange(e.target.value || null)}
          >
            <option value="">All Categories</option>
            {categories.map((category) => (
              <option key={category.id} value={category.id}>
                {category.name} {category.questionCount && `(${category.questionCount})`}
              </option>
            ))}
          </select>
        </div>

        {/* Difficulty Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Difficulty
          </label>
          <select
            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={selectedDifficulty || ''}
            onChange={(e) => 
              onDifficultyChange(e.target.value as QuestionDifficulty || null)
            }
          >
            <option value="">All Difficulties</option>
            {difficulties.map((difficulty) => (
              <option key={difficulty} value={difficulty}>
                {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
              </option>
            ))}
          </select>
        </div>

        {/* Question Type Filter */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Question Type
          </label>
          <select
            className="w-full px-3 py-2 bg-white border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={selectedType || ''}
            onChange={(e) => 
              onTypeChange(e.target.value as QuestionType || null)
            }
          >
            <option value="">All Types</option>
            {types.map((type) => (
              <option key={type} value={type}>
                {type.split('_').map(word => 
                  word.charAt(0).toUpperCase() + word.slice(1)
                ).join(' ')}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
};

export default QuestionFilterBar;
