import * as React from 'react'
import { cn } from '@/lib/utils'

/**
 * Textarea component matching Figma design
 */
export interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  error?: boolean
}

const Textarea = React.forwardRef<HTMLTextAreaElement, TextareaProps>(
  ({ className, error, ...props }, ref) => {
    return (
      <textarea
        className={cn(
          'flex min-h-[100px] w-full rounded-md border bg-white px-3 py-2 text-sm',
          'border-gray-300 placeholder:text-gray-400 resize-none',
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
Textarea.displayName = 'Textarea'

export { Textarea }
