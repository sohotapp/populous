'use client'

import * as React from 'react'
import { Eye, ChevronLeft, ChevronRight } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { ProgressThin } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import type { Question } from '@/types'

/**
 * Survey Preview Panel matching Figma (Screenshots 4.31.04, 4.31.08):
 *
 * Header:
 * - "Survey Preview" title
 * - "Live respondent view" subtitle
 *
 * Content:
 * - Progress: "Question X of Y" with progress bar and percentage
 * - Question display
 * - Answer options (radio buttons, rating scale, etc.)
 * - Navigation: Back / Next buttons
 */

interface SurveyPreviewProps {
  questions: Question[]
  currentQuestionIndex: number
  onQuestionChange: (index: number) => void
  selectedAnswers: Record<string, string | string[] | number>
  onAnswerChange: (questionId: string, answer: string | string[] | number) => void
}

export function SurveyPreview({
  questions,
  currentQuestionIndex,
  onQuestionChange,
  selectedAnswers,
  onAnswerChange,
}: SurveyPreviewProps) {
  const currentQuestion = questions[currentQuestionIndex]
  const progress = questions.length > 0
    ? Math.round(((currentQuestionIndex + 1) / questions.length) * 100)
    : 0

  const canGoBack = currentQuestionIndex > 0
  const canGoNext = currentQuestionIndex < questions.length - 1
  const isLastQuestion = currentQuestionIndex === questions.length - 1

  return (
    <div className="panel flex flex-col h-full">
      {/* Header */}
      <div className="panel-header">
        <h2 className="panel-header-title">Survey Preview</h2>
        <p className="panel-header-subtitle">Live respondent view</p>
      </div>

      {/* Content */}
      <div className="panel-content flex-1 flex flex-col">
        {questions.length === 0 ? (
          <SurveyPreviewEmptyState />
        ) : (
          <>
            {/* Progress */}
            <div className="mb-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-600">
                  Question {currentQuestionIndex + 1} of {questions.length}
                </span>
                <span className="text-sm font-medium text-gray-900">
                  {progress}%
                </span>
              </div>
              <ProgressThin value={progress} />
            </div>

            {/* Question */}
            {currentQuestion && (
              <div className="flex-1">
                <h3 className="text-base font-medium text-gray-900 mb-6">
                  {currentQuestion.text}
                </h3>

                {/* Answer Options */}
                <QuestionRenderer
                  question={currentQuestion}
                  selectedAnswer={selectedAnswers[currentQuestion.id]}
                  onAnswerChange={(answer) =>
                    onAnswerChange(currentQuestion.id, answer)
                  }
                />
              </div>
            )}

            {/* Navigation */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-200 mt-auto">
              <Button
                variant="ghost"
                disabled={!canGoBack}
                onClick={() => onQuestionChange(currentQuestionIndex - 1)}
              >
                <ChevronLeft className="h-4 w-4 mr-1" />
                Back
              </Button>

              <Button
                onClick={() =>
                  canGoNext
                    ? onQuestionChange(currentQuestionIndex + 1)
                    : console.log('Submit')
                }
              >
                {isLastQuestion ? 'Submit' : 'Next'}
                {!isLastQuestion && <ChevronRight className="h-4 w-4 ml-1" />}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  )
}

/**
 * Empty state
 */
function SurveyPreviewEmptyState() {
  return (
    <div className="empty-state flex-1">
      <Eye className="empty-state-icon" />
      <h3 className="empty-state-title">Preview will appear here</h3>
      <p className="empty-state-description">
        As you build your survey, you&apos;ll see a live preview of how
        respondents will experience it.
      </p>
    </div>
  )
}

/**
 * Question renderer based on type
 */
interface QuestionRendererProps {
  question: Question
  selectedAnswer?: string | string[] | number
  onAnswerChange: (answer: string | string[] | number) => void
}

function QuestionRenderer({
  question,
  selectedAnswer,
  onAnswerChange,
}: QuestionRendererProps) {
  switch (question.type) {
    case 'single_choice':
      return (
        <SingleChoiceQuestion
          options={question.options}
          selectedOption={selectedAnswer as string}
          onSelect={onAnswerChange}
        />
      )
    case 'multiple_choice':
      return (
        <MultipleChoiceQuestion
          options={question.options}
          selectedOptions={(selectedAnswer as string[]) || []}
          onSelect={onAnswerChange}
        />
      )
    case 'rating_scale':
      return (
        <RatingScaleQuestion
          min={question.scaleMin || 1}
          max={question.scaleMax || 5}
          minLabel={question.scaleLabels?.min || 'Very Dissatisfied'}
          maxLabel={question.scaleLabels?.max || 'Very Satisfied'}
          selectedValue={selectedAnswer as number}
          onSelect={onAnswerChange}
        />
      )
    default:
      return null
  }
}

/**
 * Single choice (radio buttons)
 */
interface SingleChoiceQuestionProps {
  options: string[]
  selectedOption?: string
  onSelect: (option: string) => void
}

function SingleChoiceQuestion({
  options,
  selectedOption,
  onSelect,
}: SingleChoiceQuestionProps) {
  return (
    <div className="space-y-3">
      {options.map((option) => (
        <label
          key={option}
          className={cn(
            'flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors',
            selectedOption === option
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-gray-300'
          )}
        >
          <div
            className={cn(
              'w-5 h-5 rounded-full border-2 flex items-center justify-center',
              selectedOption === option
                ? 'border-primary-600 bg-primary-600'
                : 'border-gray-300'
            )}
          >
            {selectedOption === option && (
              <div className="w-2 h-2 bg-white rounded-full" />
            )}
          </div>
          <span className="text-sm text-gray-700">{option}</span>
        </label>
      ))}
    </div>
  )
}

/**
 * Multiple choice (checkboxes)
 */
interface MultipleChoiceQuestionProps {
  options: string[]
  selectedOptions: string[]
  onSelect: (options: string[]) => void
}

function MultipleChoiceQuestion({
  options,
  selectedOptions,
  onSelect,
}: MultipleChoiceQuestionProps) {
  const toggleOption = (option: string) => {
    if (selectedOptions.includes(option)) {
      onSelect(selectedOptions.filter((o) => o !== option))
    } else {
      onSelect([...selectedOptions, option])
    }
  }

  return (
    <div className="space-y-3">
      {options.map((option) => (
        <label
          key={option}
          className={cn(
            'flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors',
            selectedOptions.includes(option)
              ? 'border-primary-500 bg-primary-50'
              : 'border-gray-200 hover:border-gray-300'
          )}
          onClick={() => toggleOption(option)}
        >
          <div
            className={cn(
              'w-5 h-5 rounded border-2 flex items-center justify-center',
              selectedOptions.includes(option)
                ? 'border-primary-600 bg-primary-600'
                : 'border-gray-300'
            )}
          >
            {selectedOptions.includes(option) && (
              <svg className="w-3 h-3 text-white" viewBox="0 0 12 12" fill="none">
                <path
                  d="M2 6L5 9L10 3"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                />
              </svg>
            )}
          </div>
          <span className="text-sm text-gray-700">{option}</span>
        </label>
      ))}
    </div>
  )
}

/**
 * Rating scale (1-5 dots)
 */
interface RatingScaleQuestionProps {
  min: number
  max: number
  minLabel: string
  maxLabel: string
  selectedValue?: number
  onSelect: (value: number) => void
}

function RatingScaleQuestion({
  min,
  max,
  minLabel,
  maxLabel,
  selectedValue,
  onSelect,
}: RatingScaleQuestionProps) {
  const range = Array.from({ length: max - min + 1 }, (_, i) => min + i)

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <span className="text-sm text-gray-500">{minLabel}</span>
        <span className="text-sm text-gray-500">{maxLabel}</span>
      </div>
      <div className="flex items-center justify-between px-4">
        {range.map((value) => (
          <button
            key={value}
            onClick={() => onSelect(value)}
            className="flex flex-col items-center gap-2"
          >
            <div
              className={cn(
                'w-8 h-8 rounded-full border-2 transition-all',
                selectedValue === value
                  ? 'border-primary-600 bg-primary-600'
                  : 'border-gray-300 hover:border-gray-400'
              )}
            />
            <span className="text-sm text-gray-600">{value}</span>
          </button>
        ))}
      </div>
    </div>
  )
}
