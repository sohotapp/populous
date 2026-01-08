'use client'

import { Header } from '@/components/layout/header'
import { Sidebar } from '@/components/layout/sidebar'

/**
 * Dashboard layout matching Figma:
 * - Header: 64px height, fixed top
 * - Sidebar: 64px width, fixed left
 * - Content: fills remaining space
 */
export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode
}) {
  // Mock user for now - will come from auth
  const user = {
    name: 'John Doe',
    avatarUrl: undefined,
  }

  return (
    <div className="min-h-screen flex flex-col">
      {/* Header - fixed at top */}
      <Header user={user} />

      {/* Main area with sidebar */}
      <div className="flex flex-1">
        {/* Sidebar - fixed width */}
        <Sidebar />

        {/* Main content area */}
        <main className="flex-1 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  )
}
