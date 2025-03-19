'use client';

import React, { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Question, QuestionDifficulty, QuestionType, Category } from '@/types/questions';

interface QuestionManagementProps {
  questions: Question[];
  categories: Category[];
  onAddQuestion: (question: Omit<Question, 'id' | 'createdAt' | 'updatedAt'>) => void;
  onUpdateQuestion: (id: string, question: Partial<Question>) => void;
  onDeleteQuestion: (id: string) => void;
  onAddCategory: (category: Omit<Category, 'id'>) => void;
  onUpdateCategory: (id: string, category: Partial<Category>) => void;
  onDeleteCategory: (id: string) => void;
  isLoading?: boolean;
}

const QuestionManagement: React.FC<QuestionManagementProps> = ({
  questions,
  categories,
  onAddQuestion,
  onUpdateQuestion,
  onDeleteQuestion,
  onAddCategory,
  onUpdateCategory,
  onDeleteCategory,
  isLoading = false,
}) => {
  // State for the active tab
  const [activeTab, setActiveTab] = useState<'questions' | 'categories'>('questions');
  
  // State for filtering and sorting questions
  const [questionFilter, setQuestionFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [difficultyFilter, setDifficultyFilter] = useState('');
  
  // State for the question and category being edited
  const [editingQuestion, setEditingQuestion] = useState<Question | null>(null);
  const [editingCategory, setEditingCategory] = useState<Category | null>(null);
  
  // State for the new question and category forms
  const [newQuestion, setNewQuestion] = useState<{
    content: string;
    questionType: QuestionType;
    difficulty: QuestionDifficulty;
    category: string;
    expectedAnswer?: string;
    interviewId: string;
  }>({
    content: '',
    questionType: 'technical',
    difficulty: 'medium',
    category: '',
    expectedAnswer: '',
    interviewId: '', // This would typically be selected or generated
  });
  
  const [newCategory, setNewCategory] = useState<{
    name: string;
    description: string;
  }>({
    name: '',
    description: '',
  });

  // Filter questions based on the filters
  const filteredQuestions = questions.filter(question => {
    let matches = true;
    
    if (questionFilter) {
      matches = matches && question.content.toLowerCase().includes(questionFilter.toLowerCase());
    }
    
    if (categoryFilter) {
      matches = matches && question.category === categoryFilter;
    }
    
    if (typeFilter) {
      matches = matches && question.questionType === typeFilter;
    }
    
    if (difficultyFilter) {
      matches = matches && question.difficulty === difficultyFilter;
    }
    
    return matches;
  });

  // Handler for adding a new question
  const handleAddQuestion = () => {
    onAddQuestion(newQuestion);
    setNewQuestion({
      content: '',
      questionType: 'technical',
      difficulty: 'medium',
      category: '',
      expectedAnswer: '',
      interviewId: '',
    });
  };

  // Handler for updating a question
  const handleUpdateQuestion = () => {
    if (editingQuestion) {
      onUpdateQuestion(editingQuestion.id, editingQuestion);
      setEditingQuestion(null);
    }
  };

  // Handler for adding a new category
  const handleAddCategory = () => {
    onAddCategory(newCategory);
    setNewCategory({
      name: '',
      description: '',
    });
  };

  // Handler for updating a category
  const handleUpdateCategory = () => {
    if (editingCategory) {
      onUpdateCategory(editingCategory.id, editingCategory);
      setEditingCategory(null);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Tabs */}
      <div className="flex border-b border-gray-200">
        <button
          className={`px-6 py-3 font-medium text-sm focus:outline-none ${
            activeTab === 'questions'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('questions')}
        >
          Questions
        </button>
        <button
          className={`px-6 py-3 font-medium text-sm focus:outline-none ${
            activeTab === 'categories'
              ? 'border-b-2 border-blue-500 text-blue-600'
              : 'text-gray-500 hover:text-gray-700'
          }`}
          onClick={() => setActiveTab('categories')}
        >
          Categories
        </button>
      </div>

      {/* Content based on active tab */}
      <div className="p-6">
        {activeTab === 'questions' ? (
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Manage Questions</h2>
            
            {/* Filters */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Search</label>
                <input
                  type="text"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Search questions..."
                  value={questionFilter}
                  onChange={(e) => setQuestionFilter(e.target.value)}
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={categoryFilter}
                  onChange={(e) => setCategoryFilter(e.target.value)}
                >
                  <option value="">All Categories</option>
                  {categories.map((category) => (
                    <option key={category.id} value={category.id}>
                      {category.name}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={typeFilter}
                  onChange={(e) => setTypeFilter(e.target.value)}
                >
                  <option value="">All Types</option>
                  <option value="technical">Technical</option>
                  <option value="behavioral">Behavioral</option>
                  <option value="system_design">System Design</option>
                  <option value="coding">Coding</option>
                  <option value="general">General</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Difficulty</label>
                <select
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  value={difficultyFilter}
                  onChange={(e) => setDifficultyFilter(e.target.value)}
                >
                  <option value="">All Difficulties</option>
                  <option value="easy">Easy</option>
                  <option value="medium">Medium</option>
                  <option value="hard">Hard</option>
                </select>
              </div>
            </div>

            {/* Questions List */}
            <div className="mb-6">
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Question
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Category
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Type
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Difficulty
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {isLoading ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500">
                          Loading...
                        </td>
                      </tr>
                    ) : filteredQuestions.length === 0 ? (
                      <tr>
                        <td colSpan={5} className="px-6 py-4 text-center text-sm text-gray-500">
                          No questions found
                        </td>
                      </tr>
                    ) : (
                      filteredQuestions.map((question) => (
                        <tr key={question.id}>
                          <td className="px-6 py-4 text-sm text-gray-900 truncate max-w-md">
                            {question.content}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500">
                            {categories.find(c => c.id === question.category)?.name || question.category}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500">
                            {question.questionType.split('_').map(word => 
                              word.charAt(0).toUpperCase() + word.slice(1)
                            ).join(' ')}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500">
                            {question.difficulty.charAt(0).toUpperCase() + question.difficulty.slice(1)}
                          </td>
                          <td className="px-6 py-4 text-right text-sm font-medium space-x-2">
                            <button
                              onClick={() => setEditingQuestion(question)}
                              className="text-blue-600 hover:text-blue-900"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => onDeleteQuestion(question.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Add New Question Form */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-gray-800 mb-4">Add New Question</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div className="col-span-1 md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Question Content
                  </label>
                  <textarea
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="Enter the question..."
                    value={newQuestion.content}
                    onChange={(e) => setNewQuestion({ ...newQuestion, content: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category
                  </label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={newQuestion.category}
                    onChange={(e) => setNewQuestion({ ...newQuestion, category: e.target.value })}
                  >
                    <option value="">Select Category</option>
                    {categories.map((category) => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Type
                  </label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={newQuestion.questionType}
                    onChange={(e) => setNewQuestion({ ...newQuestion, questionType: e.target.value as QuestionType })}
                  >
                    <option value="technical">Technical</option>
                    <option value="behavioral">Behavioral</option>
                    <option value="system_design">System Design</option>
                    <option value="coding">Coding</option>
                    <option value="general">General</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Difficulty
                  </label>
                  <select
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={newQuestion.difficulty}
                    onChange={(e) => setNewQuestion({ ...newQuestion, difficulty: e.target.value as QuestionDifficulty })}
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
                <div className="col-span-1 md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Expected Answer (Optional)
                  </label>
                  <textarea
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="Enter an expected or example answer..."
                    value={newQuestion.expectedAnswer || ''}
                    onChange={(e) => setNewQuestion({ ...newQuestion, expectedAnswer: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex justify-end">
                <Button onClick={handleAddQuestion}>
                  Add Question
                </Button>
              </div>
            </div>

            {/* Edit Question Modal (simplified) */}
            {editingQuestion && (
              <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center p-4 z-50">
                <div className="bg-white rounded-lg max-w-2xl w-full p-6">
                  <h3 className="text-lg font-medium text-gray-800 mb-4">Edit Question</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                    <div className="col-span-1 md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Question Content
                      </label>
                      <textarea
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows={3}
                        value={editingQuestion.content}
                        onChange={(e) => setEditingQuestion({ ...editingQuestion, content: e.target.value })}
                      />
                    </div>
                    {/* Other fields similar to the add form */}
                    <div className="col-span-1 md:col-span-2 flex justify-end space-x-3">
                      <Button variant="outline" onClick={() => setEditingQuestion(null)}>
                        Cancel
                      </Button>
                      <Button onClick={handleUpdateQuestion}>
                        Save Changes
                      </Button>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        ) : (
          <div>
            <h2 className="text-xl font-semibold text-gray-800 mb-4">Manage Categories</h2>
            
            {/* Categories List */}
            <div className="mb-6">
              <div className="border border-gray-200 rounded-lg overflow-hidden">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Name
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Description
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Question Count
                      </th>
                      <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                        Actions
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {isLoading ? (
                      <tr>
                        <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                          Loading...
                        </td>
                      </tr>
                    ) : categories.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="px-6 py-4 text-center text-sm text-gray-500">
                          No categories found
                        </td>
                      </tr>
                    ) : (
                      categories.map((category) => (
                        <tr key={category.id}>
                          <td className="px-6 py-4 text-sm font-medium text-gray-900">
                            {category.name}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500 truncate max-w-xs">
                            {category.description}
                          </td>
                          <td className="px-6 py-4 text-sm text-gray-500">
                            {category.questionCount || 0}
                          </td>
                          <td className="px-6 py-4 text-right text-sm font-medium space-x-2">
                            <button
                              onClick={() => setEditingCategory(category)}
                              className="text-blue-600 hover:text-blue-900"
                            >
                              Edit
                            </button>
                            <button
                              onClick={() => onDeleteCategory(category.id)}
                              className="text-red-600 hover:text-red-900"
                            >
                              Delete
                            </button>
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Add New Category Form */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h3 className="text-lg font-medium text-gray-800 mb-4">Add New Category</h3>
              <div className="grid grid-cols-1 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Category Name
                  </label>
                  <input
                    type="text"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="E.g., Algorithms, Leadership, etc."
                    value={newCategory.name}
                    onChange={(e) => setNewCategory({ ...newCategory, name: e.target.value })}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Description
                  </label>
                  <textarea
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    rows={3}
                    placeholder="Describe the category..."
                    value={newCategory.description}
                    onChange={(e) => setNewCategory({ ...newCategory, description: e.target.value })}
                  />
                </div>
              </div>
              <div className="flex justify-end">
                <Button onClick={handleAddCategory}>
                  Add Category
                </Button>
              </div>
            </div>

            {/* Edit Category Modal (simplified) */}
            {editingCategory && (
              <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center p-4 z-50">
                <div className="bg-white rounded-lg max-w-lg w-full p-6">
                  <h3 className="text-lg font-medium text-gray-800 mb-4">Edit Category</h3>
                  <div className="grid grid-cols-1 gap-4 mb-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Category Name
                      </label>
                      <input
                        type="text"
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        value={editingCategory.name}
                        onChange={(e) => setEditingCategory({ ...editingCategory, name: e.target.value })}
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Description
                      </label>
                      <textarea
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        rows={3}
                        value={editingCategory.description || ''}
                        onChange={(e) => setEditingCategory({ ...editingCategory, description: e.target.value })}
                      />
                    </div>
                  </div>
                  <div className="flex justify-end space-x-3">
                    <Button variant="outline" onClick={() => setEditingCategory(null)}>
                      Cancel
                    </Button>
                    <Button onClick={handleUpdateCategory}>
                      Save Changes
                    </Button>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default QuestionManagement;
