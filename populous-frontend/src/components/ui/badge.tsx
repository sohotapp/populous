import * as React from 'react'
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

/**
 * Badge variants matching Figma designs:
 * - Default: Gray background
 * - Primary: Blue background/text
 * - Success: Green for completed states
 * - Warning: Yellow for alerts
 * - Outline: Border only, no fill
 */
const badgeVariants = cva(
  'inline-flex items-center rounded font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-gray-100 text-gray-700',
        primary: 'bg-primary-100 text-primary-700',
        success: 'bg-green-100 text-green-700',
        warning: 'bg-yellow-100 text-yellow-700',
        error: 'bg-red-100 text-red-700',
        outline: 'border border-gray-300 text-gray-700 bg-transparent',
        'outline-primary': 'border border-primary-300 text-primary-600 bg-transparent',
      },
      size: {
        sm: 'px-1.5 py-0.5 text-xs',
        md: 'px-2 py-0.5 text-xs',
        lg: 'px-2.5 py-1 text-sm',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  }
)

export interface BadgeProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof badgeVariants> {}

function Badge({ className, variant, size, ...props }: BadgeProps) {
  return (
    <div className={cn(badgeVariants({ variant, size }), className)} {...props} />
  )
}

export { Badge, badgeVariants }
