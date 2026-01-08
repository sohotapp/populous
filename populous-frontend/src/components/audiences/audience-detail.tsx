'use client'

import * as React from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { AudienceProfilesTable } from './audience-table'
import { Edit, Trash2 } from 'lucide-react'
import type { Audience } from '@/types'

/**
 * Audience detail view matching Figma (Screenshot 4.30.22):
 * - Title and description at top
 * - Stats row with badges (age range, income, gender split)
 * - "Audience Profiles" section header
 * - Profiles data table
 */

interface AudienceDetailProps {
  audience: Audience
  onEdit?: () => void
  onDelete?: () => void
}

export function AudienceDetail({ audience, onEdit, onDelete }: AudienceDetailProps) {
  // Format gender ratio display
  const genderDisplay = `${audience.genderRatio.male}% Male • ${audience.genderRatio.female}% Female`

  // Format age range
  const ageDisplay = `${audience.ageRange[0]}-${audience.ageRange[1]} Years`

  // Format income level
  const incomeLabels: Record<string, string> = {
    low: 'Low Income',
    middle: 'Middle Income',
    upper_middle: 'Upper-Middle Income',
    high: 'High Income',
  }
  const incomeDisplay = incomeLabels[audience.incomeLevel] || audience.incomeLevel

  return (
    <div className="flex-1 p-6 overflow-auto">
      {/* Header Section */}
      <div className="flex items-start justify-between mb-4">
        <div>
          <h1 className="text-xl font-semibold text-gray-900 mb-1">
            {audience.name}
          </h1>
          <p className="text-sm text-gray-500 max-w-2xl">
            {audience.description}
          </p>
        </div>

        <div className="flex items-center gap-2">
          {onEdit && (
            <Button variant="secondary" size="sm" onClick={onEdit}>
              <Edit className="h-4 w-4 mr-1.5" />
              Edit
            </Button>
          )}
          {onDelete && (
            <Button variant="ghost" size="sm" onClick={onDelete} className="text-gray-500 hover:text-error-600">
              <Trash2 className="h-4 w-4" />
            </Button>
          )}
        </div>
      </div>

      {/* Stats Row */}
      <div className="flex items-center gap-3 mb-6 flex-wrap">
        <Badge variant="outline" size="lg">
          {ageDisplay}
        </Badge>
        <Badge variant="outline" size="lg">
          {incomeDisplay}
        </Badge>
        <Badge variant="outline" size="lg">
          {genderDisplay}
        </Badge>
        <Badge variant="outline" size="lg">
          {audience.profileCount} Profiles
        </Badge>
      </div>

      {/* Profiles Section */}
      <div>
        <h2 className="text-base font-semibold text-gray-900 mb-4">
          Audience Profiles
        </h2>
        <AudienceProfilesTable profiles={audience.profiles} />
      </div>
    </div>
  )
}

/**
 * Empty state when no audience is selected
 */
export function AudienceDetailEmpty() {
  return (
    <div className="flex-1 flex items-center justify-center p-6">
      <div className="text-center">
        <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg
            className="w-8 h-8 text-gray-400"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={1.5}
              d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
            />
          </svg>
        </div>
        <h3 className="text-base font-medium text-gray-900 mb-1">
          Select an audience
        </h3>
        <p className="text-sm text-gray-500 max-w-sm">
          Choose an audience from the list to view its profiles and details
        </p>
      </div>
    </div>
  )
}
