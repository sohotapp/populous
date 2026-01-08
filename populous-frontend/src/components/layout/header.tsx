'use client'

import * as React from 'react'
import Link from 'next/link'
import { useRouter } from 'next/navigation'
import {
  Search,
  Bell,
  Settings,
  Plus,
  LayoutGrid,
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { UserAvatar } from '@/components/ui/avatar'
import { cn } from '@/lib/utils'

/**
 * Header component matching Figma exactly:
 * - Height: 64px
 * - White background
 * - Border-bottom: 1px solid gray-200
 *
 * Layout (left to right):
 * - Logo: POPULOUS with grid icon
 * - Search bar
 * - Spacer
 * - Notification bell
 * - Settings gear
 * - User avatar
 * - "+ New Project" button
 */

interface HeaderProps {
  onNewProject?: () => void
  user?: {
    name: string
    avatarUrl?: string
  }
  className?: string
}

export function Header({ onNewProject, user, className }: HeaderProps) {
  const router = useRouter()
  const [searchQuery, setSearchQuery] = React.useState('')

  const handleNewProject = () => {
    if (onNewProject) {
      onNewProject()
    } else {
      router.push('/projects/new')
    }
  }

  return (
    <header
      className={cn(
        'h-16 bg-white border-b border-gray-200 flex items-center px-4 gap-4',
        className
      )}
    >
      {/* Logo */}
      <Link href="/projects" className="flex items-center gap-2 shrink-0">
        <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
          <LayoutGrid className="w-5 h-5 text-white" />
        </div>
      </Link>

      {/* Search Bar */}
      <div className="relative flex-1 max-w-md">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
        <Input
          type="search"
          placeholder="Search anything..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="pl-9 h-9 bg-gray-50 border-gray-200"
        />
      </div>

      {/* Spacer */}
      <div className="flex-1" />

      {/* Right Section */}
      <div className="flex items-center gap-2">
        {/* Notification Bell */}
        <Button variant="ghost" size="icon" className="text-gray-500 hover:text-gray-700">
          <Bell className="h-5 w-5" />
        </Button>

        {/* Settings */}
        <Button variant="ghost" size="icon" className="text-gray-500 hover:text-gray-700">
          <Settings className="h-5 w-5" />
        </Button>

        {/* User Avatar */}
        <UserAvatar
          name={user?.name || 'User'}
          src={user?.avatarUrl}
          size="sm"
          className="cursor-pointer"
        />

        {/* New Project Button */}
        <Button onClick={handleNewProject} className="gap-1.5">
          <Plus className="h-4 w-4" />
          New Project
        </Button>
      </div>
    </header>
  )
}
