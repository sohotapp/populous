'use client'

import * as React from 'react'
import { Plus, GripVertical, Pencil, Trash2, ClipboardList } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { cn } from '@/lib/utils'
import type { Question, QuestionType } from '@/types'

/**
 * Question Builder Panel matching Figma (Screenshots 4.31.04, 4.31.08):
 *
 * Header:
 * - "Question Builder" title
 * - "Build your survey questions" subtitle
 * - "+ Add Question" button
 *
 * Question List:
 * - Drag handle
 * - Question number badge
 * - Type badge (Single choice, Rating scale, etc.)
 * - Question text
 * - Edit/Delete icons
 *
 * Edit Question Form:
 * - Question Type dropdown
 * - Question Text input
 * - Answer Options list
 * - + Add Option button
 */

interface QuestionBuilderProps {
  questions: Question[]
  selectedQuestionId?: string
  onSelectQuestion: (id: string) => void
  onAddQuestion: () => void
  onUpdateQuestion: (id: string, updates: Partial<Question>) => void
  onDeleteQuestion: (id: string) => void
  onReorderQuestions: (questions: Question[]) => void
}

const questionTypeLabels: Record<QuestionType, string> = {
  single_choice: 'Single choice',
  multiple_choice: 'Multiple choice',
  rating_scale: 'Rating scale',
  open_text: 'Open text',
  ranking: 'Ranking',
}

export function QuestionBuilder({
  questions,
  selectedQuestionId,
  onSelectQuestion,
  onAddQuestion,
  onUpdateQuestion,
  onDeleteQuestion,
}: QuestionBuilderProps) {
  const selectedQuestion = questions.find((q) => q.id === selectedQuestionId)

  return (
    <div className="panel flex flex-col h-full">
      {/* Header */}
      <div className="panel-header flex items-center justify-between">
        <div>
          <h2 className="panel-header-title">Question Builder</h2>
          <p className="panel-header-subtitle">Build your survey questions</p>
        </div>
        <Button variant="secondary" size="sm" onClick={onAddQuestion}>
          <Plus className="h-4 w-4 mr-1" />
          Add Question
        </Button>
      </div>

      {/* Content */}
      <div className="panel-content flex-1 overflow-auto">
        {questions.length === 0 ? (
          <QuestionBuilderEmptyState onAdd={onAddQuestion} />
        ) : (
          <div className="space-y-4">
            {/* Question List */}
            <div className="space-y-2">
              {questions.map((question, index) => (
                <QuestionListItem
                  key={question.id}
                  question={question}
                  index={index}
                  isSelected={question.id === selectedQuestionId}
                  onSelect={() => onSelectQuestion(question.id)}
                  onDelete={() => onDeleteQuestion(question.id)}
                />
              ))}
            </div>

            {/* Edit Form */}
            {selectedQuestion && (
              <QuestionEditForm
                question={selectedQuestion}
                onUpdate={(updates) => onUpdateQuestion(selectedQuestion.id, updates)}
              />
            )}
          </div>
        )}
      </div>
    </div>
  )
}

/**
 * Empty state for question builder
 */
function QuestionBuilderEmptyState({ onAdd }: { onAdd: () => void }) {
  return (
    <div className="empty-state">
      <ClipboardList className="empty-state-icon" />
      <h3 className="empty-state-title">No questions yet</h3>
      <p className="empty-state-description">
        Start building your survey by adding your first question. Choose from
        multiple question types to gather the insights you need.
      </p>
      <Button onClick={onAdd} variant="secondary" className="mt-4">
        <Plus className="h-4 w-4 mr-1.5" />
        Add Your First Question
      </Button>
    </div>
  )
}

/**
 * Question list item
 */
interface QuestionListItemProps {
  question: Question
  index: number
  isSelected: boolean
  onSelect: () => void
  onDelete: () => void
}

function QuestionListItem({
  question,
  index,
  isSelected,
  onSelect,
  onDelete,
}: QuestionListItemProps) {
  return (
    <div
      onClick={onSelect}
      className={cn(
        'flex items-start gap-3 p-3 rounded-lg border cursor-pointer transition-colors',
        isSelected
          ? 'border-primary-300 bg-primary-50'
          : 'border-gray-200 hover:border-gray-300 bg-white'
      )}
    >
      <GripVertical className="h-5 w-5 text-gray-400 mt-0.5 cursor-grab" />

      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <Badge variant="outline" size="sm">
            Question {String(index + 1).padStart(2, '0')}
          </Badge>
          <Badge variant="outline-primary" size="sm">
            {questionTypeLabels[question.type]}
          </Badge>
        </div>
        <p className="text-sm text-gray-700 truncate">{question.text}</p>
      </div>

      <div className="flex items-center gap-1">
        <button
          onClick={(e) => {
            e.stopPropagation()
            onSelect()
          }}
          className="p-1.5 text-gray-400 hover:text-gray-600 rounded"
        >
          <Pencil className="h-4 w-4" />
        </button>
        <button
          onClick={(e) => {
            e.stopPropagation()
            onDelete()
          }}
          className="p-1.5 text-gray-400 hover:text-error-600 rounded"
        >
          <Trash2 className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
}

/**
 * Question edit form
 */
interface QuestionEditFormProps {
  question: Question
  onUpdate: (updates: Partial<Question>) => void
}

function QuestionEditForm({ question, onUpdate }: QuestionEditFormProps) {
  const [newOption, setNewOption] = React.useState('')

  const addOption = () => {
    if (newOption.trim()) {
      onUpdate({ options: [...question.options, newOption.trim()] })
      setNewOption('')
    }
  }

  const removeOption = (index: number) => {
    onUpdate({ options: question.options.filter((_, i) => i !== index) })
  }

  const updateOption = (index: number, value: string) => {
    const newOptions = [...question.options]
    newOptions[index] = value
    onUpdate({ options: newOptions })
  }

  return (
    <div className="border-t border-gray-200 pt-4 mt-4">
      <h3 className="text-sm font-medium text-gray-900 mb-4">Edit Question</h3>

      <div className="space-y-4">
        {/* Question Type */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Question Type
          </label>
          <Select
            value={question.type}
            onValueChange={(v) => onUpdate({ type: v as QuestionType })}
          >
            <SelectTrigger>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="single_choice">Single Choice (Radio Button)</SelectItem>
              <SelectItem value="multiple_choice">Multiple Choice</SelectItem>
              <SelectItem value="rating_scale">Rating Scale</SelectItem>
              <SelectItem value="open_text">Open Text</SelectItem>
              <SelectItem value="ranking">Ranking</SelectItem>
            </SelectContent>
          </Select>
        </div>

        {/* Question Text */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1.5">
            Question Text
          </label>
          <Input
            value={question.text}
            onChange={(e) => onUpdate({ text: e.target.value })}
            placeholder="Enter your question..."
          />
        </div>

        {/* Answer Options (for choice questions) */}
        {(question.type === 'single_choice' || question.type === 'multiple_choice') && (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1.5">
              Answer Options
            </label>
            <div className="space-y-2">
              {question.options.map((option, index) => (
                <div key={index} className="flex items-center gap-2">
                  <Input
                    value={option}
                    onChange={(e) => updateOption(index, e.target.value)}
                    className="flex-1"
                  />
                  <button
                    onClick={() => removeOption(index)}
                    className="p-2 text-gray-400 hover:text-error-600"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              ))}

              <div className="flex items-center gap-2">
                <Input
                  value={newOption}
                  onChange={(e) => setNewOption(e.target.value)}
                  placeholder="Add new option..."
                  onKeyDown={(e) => e.key === 'Enter' && addOption()}
                  className="flex-1"
                />
                <Button variant="secondary" size="sm" onClick={addOption}>
                  <Plus className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        )}

        {/* Scale options for rating scale */}
        {question.type === 'rating_scale' && (
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Min Label
              </label>
              <Input
                value={question.scaleLabels?.min || ''}
                onChange={(e) =>
                  onUpdate({
                    scaleLabels: { ...question.scaleLabels, min: e.target.value } as { min: string; max: string },
                  })
                }
                placeholder="Very Dissatisfied"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1.5">
                Max Label
              </label>
              <Input
                value={question.scaleLabels?.max || ''}
                onChange={(e) =>
                  onUpdate({
                    scaleLabels: { ...question.scaleLabels, max: e.target.value } as { min: string; max: string },
                  })
                }
                placeholder="Very Satisfied"
              />
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
