'use client'

import * as React from 'react'
import { PageContainer, PageHeader } from '@/components/layout'
import { ProjectCard, ProjectCardSkeleton, ProjectFilters } from '@/components/projects'
import type { Project, ProjectStatus } from '@/types'

/**
 * Projects Dashboard matching Figma (Screenshot 4.29.56):
 * - Page title: "All Projects"
 * - Filter tabs below title
 * - 2-column grid of project cards
 * - Right sidebar with Team Activities (optional for now)
 */

// Mock data matching Figma screenshots
const mockProjects: Project[] = [
  {
    id: '1',
    name: 'SparkZero Pricing Study',
    description: 'Consumer Test • Value Sat • Shipping',
    status: 'running',
    responsesCollected: 3000,
    responsesTarget: 5000,
    tags: ['Consumer', 'Pricing'],
    createdAt: '2024-01-15T10:00:00Z',
    updatedAt: '2024-01-20T14:30:00Z',
  },
  {
    id: '2',
    name: 'SparkZero Pricing Study',
    description: 'Consumer Test • Value Sat • Shipping',
    status: 'completed',
    responsesCollected: 5000,
    responsesTarget: 5000,
    tags: ['Consumer', 'Research'],
    createdAt: '2024-01-10T10:00:00Z',
    updatedAt: '2024-01-18T16:00:00Z',
  },
  {
    id: '3',
    name: 'EcoSpark Launch Test',
    description: 'Product Launch • Market Fit • Segments',
    status: 'running',
    responsesCollected: 2400,
    responsesTarget: 3000,
    tags: ['Launch', 'B2B'],
    createdAt: '2024-01-12T10:00:00Z',
    updatedAt: '2024-01-19T11:00:00Z',
  },
  {
    id: '4',
    name: 'EcoSpark Launch Test',
    description: 'Product Launch • Market Fit • Segments',
    status: 'completed',
    responsesCollected: 3000,
    responsesTarget: 3000,
    tags: ['Launch'],
    createdAt: '2024-01-08T10:00:00Z',
    updatedAt: '2024-01-15T09:00:00Z',
  },
  {
    id: '5',
    name: 'EcoSpark Launch Test',
    description: 'Product Launch • Market Fit • Segments',
    status: 'running',
    responsesCollected: 1800,
    responsesTarget: 2500,
    tags: ['Launch', 'Startup'],
    createdAt: '2024-01-14T10:00:00Z',
    updatedAt: '2024-01-20T08:00:00Z',
  },
  {
    id: '6',
    name: 'SparkZero Pricing Study',
    description: 'Consumer Test • Value Sat • Shipping',
    status: 'draft',
    responsesCollected: 0,
    responsesTarget: 2000,
    tags: ['Consumer', 'Draft'],
    createdAt: '2024-01-20T10:00:00Z',
    updatedAt: '2024-01-20T10:00:00Z',
  },
  {
    id: '7',
    name: 'EcoSpark Launch Test',
    description: 'Product Launch • Market Fit • Segments',
    status: 'completed',
    responsesCollected: 4500,
    responsesTarget: 4500,
    tags: ['Complete'],
    createdAt: '2024-01-05T10:00:00Z',
    updatedAt: '2024-01-12T14:00:00Z',
  },
  {
    id: '8',
    name: 'EcoSpark Launch Test',
    description: 'Product Launch • Market Fit • Segments',
    status: 'running',
    responsesCollected: 2100,
    responsesTarget: 3500,
    tags: ['Active', 'Priority'],
    createdAt: '2024-01-16T10:00:00Z',
    updatedAt: '2024-01-20T12:00:00Z',
  },
]

export default function ProjectsPage() {
  const [activeFilter, setActiveFilter] = React.useState<'all' | ProjectStatus>('all')
  const [sortBy, setSortBy] = React.useState('updated')
  const [isLoading, setIsLoading] = React.useState(false)

  // Filter projects
  const filteredProjects = React.useMemo(() => {
    let filtered = mockProjects
    if (activeFilter !== 'all') {
      filtered = filtered.filter((p) => p.status === activeFilter)
    }
    return filtered
  }, [activeFilter])

  // Calculate counts
  const projectCounts = React.useMemo(() => ({
    all: mockProjects.length,
    draft: mockProjects.filter((p) => p.status === 'draft').length,
    running: mockProjects.filter((p) => p.status === 'running').length,
    completed: mockProjects.filter((p) => p.status === 'completed').length,
    paused: mockProjects.filter((p) => p.status === 'paused').length,
  }), [])

  return (
    <PageContainer>
      <PageHeader title="All Projects" />

      <ProjectFilters
        activeFilter={activeFilter}
        onFilterChange={setActiveFilter}
        sortBy={sortBy}
        onSortChange={setSortBy}
        projectCounts={projectCounts}
      />

      {/* Project Grid - 2 columns matching Figma */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {isLoading
          ? Array.from({ length: 6 }).map((_, i) => (
              <ProjectCardSkeleton key={i} />
            ))
          : filteredProjects.map((project) => (
              <ProjectCard key={project.id} project={project} />
            ))}
      </div>

      {!isLoading && filteredProjects.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-500">No projects found</p>
        </div>
      )}
    </PageContainer>
  )
}
