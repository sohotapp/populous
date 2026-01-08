'use client'

import * as React from 'react'
import { Sparkles } from 'lucide-react'
import { Button } from '@/components/ui/button'
import type { AISuggestion } from '@/types'

/**
 * AI Suggestion Banner matching Figma (Screenshot 4.31.08):
 *
 * Light blue background (#EFF6FF)
 * Sparkles icon + "AI Suggestion" label
 * Suggestion text
 * "Add Suggested Question" button + "Dismiss" link
 */

interface AISuggestionBannerProps {
  suggestion: AISuggestion
  onAccept: () => void
  onDismiss: () => void
}

export function AISuggestionBanner({
  suggestion,
  onAccept,
  onDismiss,
}: AISuggestionBannerProps) {
  return (
    <div className="ai-suggestion mb-4">
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <Sparkles className="w-4 h-4 text-primary-600" />
        <span className="text-sm font-medium text-primary-700">AI Suggestion</span>
      </div>

      {/* Content */}
      <p className="text-sm text-gray-700 mb-3">
        {suggestion.text}
      </p>

      {suggestion.reasoning && (
        <p className="text-xs text-gray-500 mb-3 italic">
          {suggestion.reasoning}
        </p>
      )}

      {/* Actions */}
      <div className="flex items-center gap-3">
        <Button size="sm" onClick={onAccept}>
          Add Suggested Question
        </Button>
        <button
          onClick={onDismiss}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          Dismiss
        </button>
      </div>
    </div>
  )
}
