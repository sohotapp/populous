'use client'

import * as React from 'react'
import { Checkbox } from '@/components/ui/checkbox'
import { UserAvatar } from '@/components/ui/avatar'
import type { AudienceProfile } from '@/types'

/**
 * Audience Profiles Table matching Figma (Screenshot 4.30.22):
 *
 * ┌──┬────────┬─────┬────────────┬────────────┬─────────┬──────────┐
 * │☐ │ Name   │ Age │ Education  │ Occupation │ Income  │ Location │
 * ├──┼────────┼─────┼────────────┼────────────┼─────────┼──────────┤
 * │☐ │○ Ryan S│ 24  │ Undergrad  │ College St │ $40,000 │ Austin   │
 * │☐ │○ Mark H│ 27  │ High School│ Bartender  │ $35,000 │ Miami    │
 * └──┴────────┴─────┴────────────┴────────────┴─────────┴──────────┘
 */

interface AudienceProfilesTableProps {
  profiles: AudienceProfile[]
  selectedIds?: string[]
  onSelectionChange?: (ids: string[]) => void
}

export function AudienceProfilesTable({
  profiles,
  selectedIds = [],
  onSelectionChange,
}: AudienceProfilesTableProps) {
  const allSelected = profiles.length > 0 && selectedIds.length === profiles.length

  const toggleAll = () => {
    if (onSelectionChange) {
      if (allSelected) {
        onSelectionChange([])
      } else {
        onSelectionChange(profiles.map((p) => p.id))
      }
    }
  }

  const toggleOne = (id: string) => {
    if (onSelectionChange) {
      if (selectedIds.includes(id)) {
        onSelectionChange(selectedIds.filter((i) => i !== id))
      } else {
        onSelectionChange([...selectedIds, id])
      }
    }
  }

  if (profiles.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        No profiles in this audience
      </div>
    )
  }

  return (
    <div className="border border-gray-200 rounded-lg overflow-hidden">
      <table className="w-full">
        <thead>
          <tr className="bg-gray-50 border-b border-gray-200">
            <th className="w-12 px-4 py-3">
              <Checkbox
                checked={allSelected}
                onCheckedChange={toggleAll}
                aria-label="Select all"
              />
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Name
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Age
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Education
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Occupation
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Income
            </th>
            <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              Location
            </th>
          </tr>
        </thead>
        <tbody>
          {profiles.map((profile) => (
            <tr
              key={profile.id}
              className="border-b border-gray-200 last:border-b-0 hover:bg-gray-50 transition-colors"
            >
              <td className="px-4 py-4">
                <Checkbox
                  checked={selectedIds.includes(profile.id)}
                  onCheckedChange={() => toggleOne(profile.id)}
                  aria-label={`Select ${profile.name}`}
                />
              </td>
              <td className="px-4 py-4">
                <div className="flex items-center gap-3">
                  <UserAvatar name={profile.name} src={profile.avatarUrl} size="sm" />
                  <span className="text-sm font-medium text-gray-900">
                    {profile.name}
                  </span>
                </div>
              </td>
              <td className="px-4 py-4 text-sm text-gray-600">
                {profile.age} Years
              </td>
              <td className="px-4 py-4 text-sm text-gray-600">
                {profile.education}
              </td>
              <td className="px-4 py-4 text-sm text-gray-600">
                {profile.occupation}
              </td>
              <td className="px-4 py-4 text-sm text-gray-600">
                {profile.income}
              </td>
              <td className="px-4 py-4 text-sm text-gray-600">
                {profile.location}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
