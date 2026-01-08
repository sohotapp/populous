import * as React from 'react'
import { cn } from '@/lib/utils'

/**
 * Page container for main content area
 * Provides consistent padding and max-width
 */

interface PageContainerProps {
  children: React.ReactNode
  className?: string
}

export function PageContainer({ children, className }: PageContainerProps) {
  return (
    <main
      className={cn(
        'flex-1 overflow-auto bg-gray-50 p-6',
        className
      )}
    >
      <div className="max-w-7xl mx-auto">
        {children}
      </div>
    </main>
  )
}

/**
 * Page header with title and optional actions
 */
interface PageHeaderProps {
  title: string
  description?: string
  actions?: React.ReactNode
  className?: string
}

export function PageHeader({ title, description, actions, className }: PageHeaderProps) {
  return (
    <div className={cn('flex items-start justify-between mb-6', className)}>
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">{title}</h1>
        {description && (
          <p className="mt-1 text-sm text-gray-500">{description}</p>
        )}
      </div>
      {actions && <div className="flex items-center gap-3">{actions}</div>}
    </div>
  )
}

/**
 * Section within a page
 */
interface PageSectionProps {
  title?: string
  description?: string
  children: React.ReactNode
  className?: string
}

export function PageSection({ title, description, children, className }: PageSectionProps) {
  return (
    <section className={cn('mb-8', className)}>
      {(title || description) && (
        <div className="mb-4">
          {title && <h2 className="text-lg font-semibold text-gray-900">{title}</h2>}
          {description && <p className="mt-1 text-sm text-gray-500">{description}</p>}
        </div>
      )}
      {children}
    </section>
  )
}
