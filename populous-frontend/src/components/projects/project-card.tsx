'use client'

import * as React from 'react'
import Link from 'next/link'
import { Card } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { cn, formatNumber } from '@/lib/utils'
import type { Project, ProjectStatus } from '@/types'

/**
 * Project Card matching Figma design exactly (Screenshot 4.29.56):
 *
 * ┌──────────────────────────────────────┐
 * │ SparkZero Pricing Study              │  <- Title (font-semibold)
 * │ Consumer Test • Value Sat • Shipping │  <- Description (text-gray-500)
 * │                                      │
 * │ 3000          ████████████░░░░  82%  │  <- Metrics row
 * │               [progress bar]         │
 * │                                      │
 * │ [Running] [+2 tags]                  │  <- Status badge + tags
 * └──────────────────────────────────────┘
 */

interface ProjectCardProps {
  project: Project
  className?: string
}

const statusConfig: Record<ProjectStatus, { label: string; variant: 'default' | 'primary' | 'success' | 'warning' }> = {
  draft: { label: 'Draft', variant: 'default' },
  running: { label: 'Running', variant: 'primary' },
  completed: { label: 'Completed', variant: 'success' },
  paused: { label: 'Paused', variant: 'warning' },
}

export function ProjectCard({ project, className }: ProjectCardProps) {
  const { label, variant } = statusConfig[project.status]
  const completionPercentage = project.responsesTarget > 0
    ? Math.round((project.responsesCollected / project.responsesTarget) * 100)
    : 0

  return (
    <Link href={`/projects/${project.id}`}>
      <Card hoverable className={cn('p-5', className)}>
        {/* Title */}
        <h3 className="text-base font-semibold text-gray-900 mb-1">
          {project.name}
        </h3>

        {/* Description */}
        <p className="text-sm text-gray-500 mb-4 line-clamp-1">
          {project.description}
        </p>

        {/* Metrics Row */}
        <div className="flex items-center justify-between mb-2">
          <span className="text-2xl font-semibold text-gray-900">
            {formatNumber(project.responsesCollected)}
          </span>
          <span className="text-lg font-semibold text-gray-900">
            {completionPercentage}%
          </span>
        </div>

        {/* Progress Bar */}
        <Progress value={completionPercentage} className="mb-4" />

        {/* Tags Row */}
        <div className="flex items-center gap-2 flex-wrap">
          <Badge variant={variant}>{label}</Badge>
          {project.tags.slice(0, 2).map((tag) => (
            <Badge key={tag} variant="outline" size="sm">
              {tag}
            </Badge>
          ))}
          {project.tags.length > 2 && (
            <Badge variant="outline" size="sm">
              +{project.tags.length - 2}
            </Badge>
          )}
        </div>
      </Card>
    </Link>
  )
}

/**
 * Skeleton loader for project cards
 */
export function ProjectCardSkeleton() {
  return (
    <Card className="p-5 animate-pulse">
      <div className="h-5 bg-gray-200 rounded w-3/4 mb-2" />
      <div className="h-4 bg-gray-200 rounded w-full mb-4" />
      <div className="flex justify-between mb-2">
        <div className="h-8 bg-gray-200 rounded w-16" />
        <div className="h-6 bg-gray-200 rounded w-12" />
      </div>
      <div className="h-2 bg-gray-200 rounded mb-4" />
      <div className="flex gap-2">
        <div className="h-5 bg-gray-200 rounded w-16" />
        <div className="h-5 bg-gray-200 rounded w-20" />
      </div>
    </Card>
  )
}
