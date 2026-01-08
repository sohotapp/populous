'use client'

import * as React from 'react'
import { AlertTriangle } from 'lucide-react'
import { Checkbox } from '@/components/ui/checkbox'
import type { BiasWarning } from '@/types'

/**
 * Bias Warning Banner matching Figma (Screenshot 4.31.08):
 *
 * Yellow/orange background (#FFFBEB)
 * Warning icon + "Potential Bias Detected" label
 * Issue description
 * Suggestion text
 * "Apply Suggestions" checkbox
 */

interface BiasWarningBannerProps {
  warning: BiasWarning
  onApply: () => void
}

export function BiasWarningBanner({
  warning,
  onApply,
}: BiasWarningBannerProps) {
  const [shouldApply, setShouldApply] = React.useState(false)

  return (
    <div className="bias-warning mb-4">
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <AlertTriangle className="w-4 h-4 text-warning-600" />
        <span className="text-sm font-medium text-warning-700">
          Potential Bias Detected
        </span>
      </div>

      {/* Content */}
      <p className="text-sm text-gray-700 mb-2">
        {warning.issue}
      </p>

      {warning.suggestion && (
        <p className="text-sm text-gray-600 mb-3">
          Consider rephrasing to: &ldquo;{warning.suggestion}&rdquo;
        </p>
      )}

      {/* Apply checkbox */}
      <label className="flex items-center gap-2 cursor-pointer">
        <Checkbox
          checked={shouldApply}
          onCheckedChange={(checked) => {
            setShouldApply(!!checked)
            if (checked) onApply()
          }}
        />
        <span className="text-sm text-gray-700">Apply Suggestions</span>
      </label>
    </div>
  )
}
