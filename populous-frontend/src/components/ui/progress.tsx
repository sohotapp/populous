import * as React from 'react'
import * as ProgressPrimitive from '@radix-ui/react-progress'
import { cn } from '@/lib/utils'

/**
 * Progress bar matching Figma project card progress bars:
 * - Track: gray-200 background
 * - Fill: primary-600 (blue)
 * - Height: 8px (h-2)
 * - Border radius: full (rounded-full)
 */
const Progress = React.forwardRef<
  React.ElementRef<typeof ProgressPrimitive.Root>,
  React.ComponentPropsWithoutRef<typeof ProgressPrimitive.Root> & {
    indicatorClassName?: string
  }
>(({ className, value, indicatorClassName, ...props }, ref) => (
  <ProgressPrimitive.Root
    ref={ref}
    className={cn(
      'relative h-2 w-full overflow-hidden rounded-full bg-gray-200',
      className
    )}
    {...props}
  >
    <ProgressPrimitive.Indicator
      className={cn(
        'h-full rounded-full bg-primary-600 transition-all duration-300 ease-in-out',
        indicatorClassName
      )}
      style={{ width: `${value || 0}%` }}
    />
  </ProgressPrimitive.Root>
))
Progress.displayName = ProgressPrimitive.Root.displayName

// Thin variant for survey progress
const ProgressThin = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & { value: number }
>(({ className, value, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('relative h-1 w-full overflow-hidden rounded-full bg-gray-200', className)}
    {...props}
  >
    <div
      className="h-full rounded-full bg-primary-600 transition-all duration-300 ease-in-out"
      style={{ width: `${value}%` }}
    />
  </div>
))
ProgressThin.displayName = 'ProgressThin'

export { Progress, ProgressThin }
