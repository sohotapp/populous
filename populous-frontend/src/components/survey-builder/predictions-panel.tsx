'use client'

import * as React from 'react'
import { Sparkles, AlertCircle, Loader2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { cn } from '@/lib/utils'
import type { Question, SurveyPredictions, ConfidenceLevel } from '@/types'

/**
 * Response Predictions Panel matching Figma (Screenshots 4.31.04, 4.31.08):
 *
 * Header:
 * - "Response Predictions" title
 * - "AI-powered insights" subtitle
 *
 * Content:
 * - Overall Confidence badge
 * - Per-question prediction cards with:
 *   - Question label + confidence badge
 *   - Horizontal bar charts for options
 *   - Percentages
 *   - Mean score for rating questions
 *
 * Footer note:
 * - "Predictions based on similar surveys..."
 */

interface PredictionsPanelProps {
  questions: Question[]
  predictions?: SurveyPredictions
  isLoading?: boolean
}

const confidenceConfig: Record<ConfidenceLevel, { label: string; variant: 'default' | 'primary' | 'success' }> = {
  low: { label: 'Low', variant: 'default' },
  medium: { label: 'Medium', variant: 'primary' },
  high: { label: 'High', variant: 'success' },
}

export function PredictionsPanel({
  questions,
  predictions,
  isLoading = false,
}: PredictionsPanelProps) {
  const hasQuestions = questions.length > 0

  return (
    <div className="panel flex flex-col h-full">
      {/* Header */}
      <div className="panel-header">
        <h2 className="panel-header-title">Response Predictions</h2>
        <p className="panel-header-subtitle">AI-powered insights</p>
      </div>

      {/* Content */}
      <div className="panel-content flex-1 overflow-auto">
        {!hasQuestions ? (
          <PredictionsEmptyState />
        ) : isLoading ? (
          <PredictionsLoading />
        ) : predictions ? (
          <div className="space-y-6">
            {/* Overall Confidence */}
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700">
                Overall Confidence
              </span>
              <Badge variant={confidenceConfig[predictions.overallConfidence].variant}>
                {confidenceConfig[predictions.overallConfidence].label}
              </Badge>
            </div>

            <p className="text-sm text-gray-500">
              Predictions will improve as you add more context and questions.
            </p>

            {/* Per-question predictions */}
            <div className="space-y-4">
              {predictions.questions.map((questionPred, index) => {
                const question = questions.find((q) => q.id === questionPred.questionId)
                if (!question) return null

                return (
                  <QuestionPredictionCard
                    key={questionPred.questionId}
                    questionNumber={index + 1}
                    questionText={question.text}
                    questionType={question.type}
                    confidence={questionPred.confidence}
                    predictions={questionPred.predictions}
                    meanScore={questionPred.meanScore}
                    distribution={questionPred.distribution}
                    isUpdating={predictions.isUpdating}
                  />
                )
              })}
            </div>

            {/* Footer note */}
            <div className="flex items-start gap-2 text-xs text-gray-500 pt-4 border-t border-gray-100">
              <AlertCircle className="w-4 h-4 shrink-0 mt-0.5" />
              <p>
                Predictions based on similar surveys and general audience patterns.
              </p>
            </div>
          </div>
        ) : (
          <PredictionsEmptyState />
        )}
      </div>
    </div>
  )
}

/**
 * Empty state
 */
function PredictionsEmptyState() {
  return (
    <div className="empty-state flex-1">
      <Sparkles className="empty-state-icon" />
      <h3 className="empty-state-title">Predictions will appear here</h3>
      <p className="empty-state-description">
        Once you add questions, our AI will predict how your audience will
        respond in real-time.
      </p>
    </div>
  )
}

/**
 * Loading state
 */
function PredictionsLoading() {
  return (
    <div className="flex-1 flex items-center justify-center">
      <div className="text-center">
        <Loader2 className="w-8 h-8 text-primary-600 animate-spin mx-auto mb-3" />
        <p className="text-sm text-gray-500">Updating predictions...</p>
      </div>
    </div>
  )
}

/**
 * Single question prediction card
 */
interface QuestionPredictionCardProps {
  questionNumber: number
  questionText: string
  questionType: string
  confidence: ConfidenceLevel
  predictions: Record<string, number>
  meanScore?: number
  distribution?: string
  isUpdating?: boolean
}

function QuestionPredictionCard({
  questionNumber,
  questionText,
  questionType,
  confidence,
  predictions,
  meanScore,
  distribution,
  isUpdating,
}: QuestionPredictionCardProps) {
  // Get a friendly name for the question
  const questionLabel = questionType === 'rating_scale'
    ? `Q${questionNumber}: ${questionText.slice(0, 30)}...`
    : `Q${questionNumber}: ${questionText.slice(0, 30)}...`

  return (
    <div className="rounded-lg border border-gray-200 p-4">
      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm font-medium text-gray-700 truncate pr-2">
          {questionLabel}
        </span>
        <Badge variant={confidenceConfig[confidence].variant} size="sm">
          {confidenceConfig[confidence].label}
        </Badge>
      </div>

      {/* Prediction bars or mean score */}
      {isUpdating ? (
        <div className="text-sm text-gray-500 italic">Updating predictions...</div>
      ) : questionType === 'rating_scale' && meanScore !== undefined ? (
        <div>
          <div className="text-lg font-semibold text-gray-900 mb-1">
            Mean Score: {meanScore.toFixed(1)}/5.0
          </div>
          {distribution && (
            <p className="text-sm text-gray-500">
              Distribution: {distribution}
            </p>
          )}
        </div>
      ) : (
        <div className="space-y-2">
          {Object.entries(predictions)
            .sort(([, a], [, b]) => b - a)
            .map(([option, percentage]) => (
              <PredictionBar
                key={option}
                label={option}
                percentage={percentage}
              />
            ))}
        </div>
      )}
    </div>
  )
}

/**
 * Horizontal prediction bar
 */
interface PredictionBarProps {
  label: string
  percentage: number
}

function PredictionBar({ label, percentage }: PredictionBarProps) {
  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-600 w-28 truncate">{label}</span>
      <div className="flex-1 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div
          className={cn(
            'h-full rounded-full transition-all duration-500',
            percentage >= 70 ? 'bg-primary-600' :
            percentage >= 40 ? 'bg-primary-400' : 'bg-primary-300'
          )}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-sm font-medium text-gray-700 w-12 text-right">
        {percentage}%
      </span>
    </div>
  )
}
