'use client';

import React, { useState, useEffect } from 'react';
import { Question, QuestionDifficulty, QuestionType, Category } from '@/types/questions';
import QuestionCard from './QuestionCard';
import QuestionFilterBar from './QuestionFilterBar';

// Mock data - in a real application, this would come from an API
const mockCategories: Category[] = [
  { id: 'algorithms', name: 'Algorithms', questionCount: 15 },
  { id: 'data-structures', name: 'Data Structures', questionCount: 12 },
  { id: 'system-design', name: 'System Design', questionCount: 8 },
  { id: 'leadership', name: 'Leadership', questionCount: 10 },
  { id: 'problem-solving', name: 'Problem Solving', questionCount: 14 },
];

interface QuestionSelectionInterfaceProps {
  onSelectQuestion?: (questionId: string) => void;
  initialQuestions?: Question[];
  isLoading?: boolean;
}

const QuestionSelectionInterface: React.FC<QuestionSelectionInterfaceProps> = ({
  onSelectQuestion,
  initialQuestions = [],
  isLoading = false,
}) => {
  // State for filtering and questions
  const [questions, setQuestions] = useState<Question[]>(initialQuestions);
  const [filteredQuestions, setFilteredQuestions] = useState<Question[]>(initialQuestions);
  const [categories, setCategories] = useState<Category[]>(mockCategories);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [selectedDifficulty, setSelectedDifficulty] = useState<QuestionDifficulty | null>(null);
  const [selectedType, setSelectedType] = useState<QuestionType | null>(null);

  // In a real app, this would fetch questions from an API
  useEffect(() => {
    // If no initialQuestions provided, we would fetch them here
    if (initialQuestions.length === 0 && !isLoading) {
      // fetchQuestions().then(data => setQuestions(data));
      // For now, use mock data
      const mockQuestions: Question[] = [
        {
          id: '1',
          content: 'Implement a function to reverse a linked list',
          questionType: 'coding',
          difficulty: 'medium',
          category: 'data-structures',
          interviewId: 'interview1',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: '2',
          content: 'Describe a time when you had to deal with a team conflict',
          questionType: 'behavioral',
          difficulty: 'easy',
          category: 'leadership',
          interviewId: 'interview1',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: '3',
          content: 'Design a distributed cache system',
          questionType: 'system_design',
          difficulty: 'hard',
          category: 'system-design',
          interviewId: 'interview1',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
        {
          id: '4',
          content: 'Implement a function to find the longest common subsequence of two strings',
          questionType: 'coding',
          difficulty: 'hard',
          category: 'algorithms',
          interviewId: 'interview1',
          createdAt: new Date().toISOString(),
          updatedAt: new Date().toISOString(),
        },
      ];
      setQuestions(mockQuestions);
      setFilteredQuestions(mockQuestions);
    }
  }, [initialQuestions, isLoading]);

  // Apply filters when filter states change
  useEffect(() => {
    let filtered = [...questions];

    // Apply search filter
    if (searchQuery) {
      filtered = filtered.filter(question =>
        question.content.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    // Apply category filter
    if (selectedCategory) {
      filtered = filtered.filter(question => question.category === selectedCategory);
    }

    // Apply difficulty filter
    if (selectedDifficulty) {
      filtered = filtered.filter(question => question.difficulty === selectedDifficulty);
    }

    // Apply type filter
    if (selectedType) {
      filtered = filtered.filter(question => question.questionType === selectedType);
    }

    setFilteredQuestions(filtered);
  }, [questions, searchQuery, selectedCategory, selectedDifficulty, selectedType]);

  const handleQuestionSelect = (questionId: string) => {
    if (onSelectQuestion) {
      onSelectQuestion(questionId);
    }
  };

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold text-gray-800">Practice Questions</h2>
      <p className="text-gray-600">
        Select a question to practice your interview skills. Use the filters to find the right type of questions.
      </p>

      {/* Filters */}
      <QuestionFilterBar
        categories={categories}
        selectedCategory={selectedCategory}
        selectedDifficulty={selectedDifficulty}
        selectedType={selectedType}
        onCategoryChange={setSelectedCategory}
        onDifficultyChange={setSelectedDifficulty}
        onTypeChange={setSelectedType}
        onSearchChange={setSearchQuery}
      />

      {/* Loading state */}
      {isLoading && (
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
        </div>
      )}

      {/* Questions grid */}
      {!isLoading && (
        <>
          {filteredQuestions.length === 0 ? (
            <div className="bg-white rounded-lg shadow p-8 text-center">
              <p className="text-gray-600">No questions match your filters. Try adjusting your criteria.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {filteredQuestions.map((question) => (
                <QuestionCard
                  key={question.id}
                  id={question.id}
                  content={question.content}
                  questionType={question.questionType}
                  difficulty={question.difficulty}
                  category={question.category}
                  onSelect={handleQuestionSelect}
                />
              ))}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default QuestionSelectionInterface;
