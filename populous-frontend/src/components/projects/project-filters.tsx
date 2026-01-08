'use client'

import * as React from 'react'
import { Tabs, TabsList, TabsTrigger } from '@/components/ui/tabs'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import type { ProjectStatus } from '@/types'

/**
 * Project filters matching Figma design (Screenshot 4.29.56):
 * - Tab filters: All Projects, Active, Running, Completed
 * - Sort dropdown on the right
 */

interface ProjectFiltersProps {
  activeFilter: 'all' | ProjectStatus
  onFilterChange: (filter: 'all' | ProjectStatus) => void
  sortBy: string
  onSortChange: (sort: string) => void
  projectCounts?: {
    all: number
    draft: number
    running: number
    completed: number
    paused: number
  }
}

export function ProjectFilters({
  activeFilter,
  onFilterChange,
  sortBy,
  onSortChange,
  projectCounts,
}: ProjectFiltersProps) {
  return (
    <div className="flex items-center justify-between mb-6">
      {/* Filter Tabs */}
      <Tabs value={activeFilter} onValueChange={(v) => onFilterChange(v as 'all' | ProjectStatus)}>
        <TabsList>
          <TabsTrigger value="all">
            All Projects
            {projectCounts && (
              <span className="ml-1.5 text-gray-400">({projectCounts.all})</span>
            )}
          </TabsTrigger>
          <TabsTrigger value="draft">Active</TabsTrigger>
          <TabsTrigger value="running">Running</TabsTrigger>
          <TabsTrigger value="completed">Completed</TabsTrigger>
        </TabsList>
      </Tabs>

      {/* Sort Dropdown */}
      <Select value={sortBy} onValueChange={onSortChange}>
        <SelectTrigger className="w-40">
          <SelectValue placeholder="Sort by" />
        </SelectTrigger>
        <SelectContent>
          <SelectItem value="updated">Last Updated</SelectItem>
          <SelectItem value="created">Date Created</SelectItem>
          <SelectItem value="name">Name</SelectItem>
          <SelectItem value="progress">Progress</SelectItem>
        </SelectContent>
      </Select>
    </div>
  )
}
