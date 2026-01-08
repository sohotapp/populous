'use client'

import * as React from 'react'
import { Plus, Users } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import type { Audience } from '@/types'

/**
 * Audience list sidebar matching Figma (Screenshot 4.30.22):
 * - Header with "Audiences" title and "+ New Audience" button
 * - List of audience items with name and profile count
 * - Selected state: blue background tint
 */

interface AudienceListProps {
  audiences: Audience[]
  selectedId?: string
  onSelect: (audience: Audience) => void
  onNewAudience: () => void
  className?: string
}

export function AudienceList({
  audiences,
  selectedId,
  onSelect,
  onNewAudience,
  className,
}: AudienceListProps) {
  return (
    <div className={cn('w-72 bg-white border-r border-gray-200 flex flex-col', className)}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-900">Audiences</h2>
        </div>
        <Button onClick={onNewAudience} className="w-full gap-1.5" size="sm">
          <Plus className="h-4 w-4" />
          New Audience
        </Button>
      </div>

      {/* Audience List */}
      <div className="flex-1 overflow-auto py-2">
        {audiences.map((audience) => (
          <AudienceListItem
            key={audience.id}
            audience={audience}
            isSelected={audience.id === selectedId}
            onClick={() => onSelect(audience)}
          />
        ))}

        {audiences.length === 0 && (
          <div className="px-4 py-8 text-center">
            <Users className="w-8 h-8 text-gray-300 mx-auto mb-2" />
            <p className="text-sm text-gray-500">No audiences yet</p>
          </div>
        )}
      </div>
    </div>
  )
}

interface AudienceListItemProps {
  audience: Audience
  isSelected: boolean
  onClick: () => void
}

function AudienceListItem({ audience, isSelected, onClick }: AudienceListItemProps) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'w-full px-4 py-3 text-left transition-colors',
        'hover:bg-gray-50',
        isSelected && 'bg-primary-50 border-l-2 border-primary-600'
      )}
    >
      <div className="flex items-center justify-between">
        <div className="min-w-0 flex-1">
          <p className={cn(
            'text-sm font-medium truncate',
            isSelected ? 'text-primary-700' : 'text-gray-900'
          )}>
            {audience.name}
          </p>
          <p className="text-xs text-gray-500 mt-0.5">
            {audience.profileCount} Profiles
          </p>
        </div>
      </div>
    </button>
  )
}
