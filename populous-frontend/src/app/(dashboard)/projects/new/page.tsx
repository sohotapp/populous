'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { Play } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import {
  QuestionBuilder,
  SurveyPreview,
  PredictionsPanel,
  AISuggestionBanner,
  BiasWarningBanner,
} from '@/components/survey-builder'
import { generateId } from '@/lib/utils'
import type { Question, SurveyPredictions, AISuggestion, BiasWarning } from '@/types'

/**
 * New Project Page (Survey Builder) matching Figma (Screenshots 4.30.59, 4.31.04, 4.31.08):
 *
 * Layout:
 * - Three-panel layout: Question Builder | Survey Preview | Response Predictions
 * - Footer: Audience dropdown, Sample Size dropdown, Run Survey button
 */

// Mock audiences for dropdown
const mockAudiences = [
  { id: '1', name: 'General Consumer (18-65)' },
  { id: '2', name: 'Urban Gen Z Shoppers (US)' },
  { id: '3', name: 'Tech Enthusiasts' },
  { id: '4', name: 'Budget Conscious Millennials' },
]

// Sample sizes
const sampleSizes = [50, 100, 200, 500, 1000]

// Mock AI suggestion
const mockSuggestion: AISuggestion = {
  id: 'sug1',
  type: 'question',
  text: 'Based on your goal to understand product usage, consider asking about price sensitivity to get deeper insights into purchasing decisions.',
  reasoning: 'This helps correlate satisfaction with price perception.',
  suggestedQuestion: {
    type: 'rating_scale',
    text: 'How satisfied are you with the product\'s current pricing?',
    scaleMin: 1,
    scaleMax: 5,
    scaleLabels: { min: 'Very Dissatisfied', max: 'Very Satisfied' },
  },
}

// Mock bias warning
const mockBiasWarning: BiasWarning = {
  questionId: 'q2',
  severity: 'warning',
  issue: 'This question may be leading. Consider rephrasing to avoid suggesting a preferred answer.',
  suggestion: 'How would you rate the product\'s pricing?',
}

export default function NewProjectPage() {
  const router = useRouter()

  // State
  const [questions, setQuestions] = React.useState<Question[]>([])
  const [selectedQuestionId, setSelectedQuestionId] = React.useState<string>()
  const [currentPreviewIndex, setCurrentPreviewIndex] = React.useState(0)
  const [selectedAnswers, setSelectedAnswers] = React.useState<Record<string, string | string[] | number>>({})

  // Footer state
  const [selectedAudience, setSelectedAudience] = React.useState('')
  const [sampleSize, setSampleSize] = React.useState('100')
  const [isRunning, setIsRunning] = React.useState(false)

  // AI features state
  const [showSuggestion, setShowSuggestion] = React.useState(false)
  const [showBiasWarning, setShowBiasWarning] = React.useState(false)

  // Mock predictions
  const [predictions, setPredictions] = React.useState<SurveyPredictions | undefined>()

  // Add new question
  const handleAddQuestion = () => {
    const newQuestion: Question = {
      id: generateId(),
      type: 'single_choice',
      text: 'What is your primary reason for using our product?',
      options: ['Better Features', 'Lower price', 'Ease of use', 'Customer support'],
      required: true,
      order: questions.length,
    }
    setQuestions([...questions, newQuestion])
    setSelectedQuestionId(newQuestion.id)

    // Show AI suggestion after first question
    if (questions.length === 0) {
      setTimeout(() => setShowSuggestion(true), 1000)
    }

    // Generate mock predictions
    updatePredictions([...questions, newQuestion])
  }

  // Update question
  const handleUpdateQuestion = (id: string, updates: Partial<Question>) => {
    setQuestions(questions.map((q) =>
      q.id === id ? { ...q, ...updates } : q
    ))

    // Show bias warning on certain updates
    if (updates.text?.toLowerCase().includes('best') || updates.text?.toLowerCase().includes('amazing')) {
      setShowBiasWarning(true)
    }

    // Update predictions
    updatePredictions(questions.map((q) => q.id === id ? { ...q, ...updates } : q))
  }

  // Delete question
  const handleDeleteQuestion = (id: string) => {
    const newQuestions = questions.filter((q) => q.id !== id)
    setQuestions(newQuestions)
    if (selectedQuestionId === id) {
      setSelectedQuestionId(newQuestions[0]?.id)
    }
    updatePredictions(newQuestions)
  }

  // Update predictions (mock)
  const updatePredictions = (qs: Question[]) => {
    if (qs.length === 0) {
      setPredictions(undefined)
      return
    }

    setPredictions({
      overallConfidence: qs.length >= 2 ? 'medium' : 'low',
      isUpdating: false,
      questions: qs.map((q, i) => ({
        questionId: q.id,
        confidence: i === 0 ? 'low' : 'medium',
        predictions: q.type === 'single_choice' || q.type === 'multiple_choice'
          ? Object.fromEntries(
              q.options.map((opt, j) => [opt, Math.max(20, 85 - j * 15)])
            )
          : {},
        meanScore: q.type === 'rating_scale' ? 3.2 : undefined,
        distribution: q.type === 'rating_scale' ? 'Slightly negative skew expected' : undefined,
      })),
    })
  }

  // Accept AI suggestion
  const handleAcceptSuggestion = () => {
    if (mockSuggestion.suggestedQuestion) {
      const newQuestion: Question = {
        id: generateId(),
        type: mockSuggestion.suggestedQuestion.type || 'rating_scale',
        text: mockSuggestion.suggestedQuestion.text || '',
        options: mockSuggestion.suggestedQuestion.options || [],
        scaleMin: mockSuggestion.suggestedQuestion.scaleMin,
        scaleMax: mockSuggestion.suggestedQuestion.scaleMax,
        scaleLabels: mockSuggestion.suggestedQuestion.scaleLabels,
        required: true,
        order: questions.length,
      }
      setQuestions([...questions, newQuestion])
      updatePredictions([...questions, newQuestion])
    }
    setShowSuggestion(false)
  }

  // Run survey
  const handleRunSurvey = async () => {
    setIsRunning(true)
    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 2000))
    setIsRunning(false)
    router.push('/projects')
  }

  // Estimated runtime
  const estimatedRuntime = Math.ceil((Number(sampleSize) * questions.length) / 100 * 10)

  return (
    <div className="flex flex-col h-[calc(100vh-64px)]">
      {/* Page Header */}
      <div className="px-6 py-4 border-b border-gray-200 bg-white">
        <h1 className="text-xl font-semibold text-gray-900">New Project</h1>
      </div>

      {/* Three-Panel Layout */}
      <div className="flex-1 flex gap-4 p-4 overflow-hidden">
        {/* Question Builder Panel */}
        <div className="flex-1 min-w-panel">
          {/* AI Suggestion */}
          {showSuggestion && (
            <AISuggestionBanner
              suggestion={mockSuggestion}
              onAccept={handleAcceptSuggestion}
              onDismiss={() => setShowSuggestion(false)}
            />
          )}

          {/* Bias Warning */}
          {showBiasWarning && questions.length > 1 && (
            <BiasWarningBanner
              warning={mockBiasWarning}
              onApply={() => setShowBiasWarning(false)}
            />
          )}

          <QuestionBuilder
            questions={questions}
            selectedQuestionId={selectedQuestionId}
            onSelectQuestion={setSelectedQuestionId}
            onAddQuestion={handleAddQuestion}
            onUpdateQuestion={handleUpdateQuestion}
            onDeleteQuestion={handleDeleteQuestion}
            onReorderQuestions={setQuestions}
          />
        </div>

        {/* Survey Preview Panel */}
        <div className="flex-1 min-w-panel">
          <SurveyPreview
            questions={questions}
            currentQuestionIndex={currentPreviewIndex}
            onQuestionChange={setCurrentPreviewIndex}
            selectedAnswers={selectedAnswers}
            onAnswerChange={(qId, answer) =>
              setSelectedAnswers({ ...selectedAnswers, [qId]: answer })
            }
          />
        </div>

        {/* Response Predictions Panel */}
        <div className="flex-1 min-w-panel">
          <PredictionsPanel
            questions={questions}
            predictions={predictions}
            isLoading={false}
          />
        </div>
      </div>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-gray-200 bg-white flex items-center gap-6">
        {/* Audience Selector */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Audience</span>
          <Select value={selectedAudience} onValueChange={setSelectedAudience}>
            <SelectTrigger className="w-52">
              <SelectValue placeholder="Select an audience" />
            </SelectTrigger>
            <SelectContent>
              {mockAudiences.map((audience) => (
                <SelectItem key={audience.id} value={audience.id}>
                  {audience.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Sample Size */}
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600">Sample Size</span>
          <Select value={sampleSize} onValueChange={setSampleSize}>
            <SelectTrigger className="w-24">
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {sampleSizes.map((size) => (
                <SelectItem key={size} value={String(size)}>
                  {size}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Estimated Runtime */}
        {questions.length > 0 && (
          <span className="text-sm text-gray-500">
            Estimated runtime: ~{estimatedRuntime} Seconds
          </span>
        )}

        {/* Spacer */}
        <div className="flex-1" />

        {/* Run Survey Button */}
        <Button
          onClick={handleRunSurvey}
          disabled={questions.length === 0 || !selectedAudience || isRunning}
          loading={isRunning}
        >
          <Play className="h-4 w-4 mr-1.5" />
          Run Survey
        </Button>
      </div>
    </div>
  )
}
