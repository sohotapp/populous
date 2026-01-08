'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import { X } from 'lucide-react'
import { Button } from '@/components/ui/button'
import {
  CreateAudienceForm,
  CreateAudienceEmptyState,
  type CreateAudienceFormData,
} from '@/components/audiences/create-audience-form'

/**
 * Create Audience Page matching Figma (Screenshots 4.30.30, 4.30.36, 4.30.39):
 * - Full-page modal style
 * - Left: Form
 * - Right: Empty state or preview
 */

export default function CreateAudiencePage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = React.useState(false)
  const [generatedAudience, setGeneratedAudience] = React.useState<unknown>(null)

  const handleSubmit = async (data: CreateAudienceFormData) => {
    setIsLoading(true)

    // Simulate API call
    await new Promise((resolve) => setTimeout(resolve, 3000))

    // Mock generated audience
    setGeneratedAudience({
      name: data.name,
      profileCount: 150,
    })

    setIsLoading(false)
  }

  const handleCancel = () => {
    router.back()
  }

  const handleClose = () => {
    router.push('/audiences')
  }

  return (
    <div className="fixed inset-0 bg-white z-50 flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200">
        <h1 className="text-lg font-semibold text-gray-900">Create Audience</h1>
        <div className="flex items-center gap-3">
          <Button variant="primary" size="sm">
            Create Audience
          </Button>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Form */}
        <div className="w-[440px] border-r border-gray-200 overflow-auto p-6">
          <CreateAudienceForm
            onSubmit={handleSubmit}
            onCancel={handleCancel}
            isLoading={isLoading}
          />
        </div>

        {/* Right Panel - Preview/Empty State */}
        {isLoading ? (
          <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
            <div className="text-center">
              <div className="w-16 h-16 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                Generating your Audience
              </h2>
              <p className="text-sm text-gray-500 mb-4">
                Creating synthetic profiles based on your criteria...
              </p>
              <Button variant="secondary" onClick={() => setIsLoading(false)}>
                Cancel
              </Button>
            </div>
          </div>
        ) : generatedAudience ? (
          <div className="flex-1 p-6 bg-gray-50 overflow-auto">
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-2">
                Audience Generated!
              </h2>
              <p className="text-sm text-gray-500">
                Your audience has been created successfully.
              </p>
              <Button onClick={handleClose} className="mt-4">
                View Audience
              </Button>
            </div>
          </div>
        ) : (
          <CreateAudienceEmptyState />
        )}
      </div>
    </div>
  )
}
