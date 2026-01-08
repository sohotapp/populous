import * as React from 'react'
import { cn } from '@/lib/utils'

/**
 * Input component matching Figma design:
 * - Border: 1px solid #D1D5DB (gray-300)
 * - Border radius: 6px
 * - Padding: 8px 12px
 * - Focus: ring-2 primary-500
 * - Placeholder: #9CA3AF (gray-400)
 */
export interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  error?: boolean
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, error, ...props }, ref) => {
    return (
      <input
        type={type}
        className={cn(
          'flex h-9 w-full rounded-md border bg-white px-3 py-2 text-sm',
          'border-gray-300 placeholder:text-gray-400',
          'focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
          'disabled:cursor-not-allowed disabled:opacity-50 disabled:bg-gray-50',
          error && 'border-error-500 focus:ring-error-500 focus:border-error-500',
          className
        )}
        ref={ref}
        {...props}
      />
    )
  }
)
Input.displayName = 'Input'

export { Input }
