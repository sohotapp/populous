'use client'

import * as React from 'react'
import Link from 'next/link'
import { usePathname } from 'next/navigation'
import {
  LayoutGrid,
  Users,
  Compass,
  BarChart3,
  FolderOpen,
  Settings,
} from 'lucide-react'
import { cn } from '@/lib/utils'

/**
 * Sidebar navigation matching Figma exactly:
 * - Width: 64px (collapsed)
 * - White background
 * - Border-right: 1px solid gray-200
 * - Icons: 20px, centered
 * - Active state: blue icon, blue left border
 *
 * Navigation items (from Figma):
 * 1. Projects (grid icon)
 * 2. Audiences (users icon)
 * 3. Templates (compass icon)
 * 4. Analytics (bar chart icon)
 * 5. Assets (folder icon)
 * 6. Settings (cog icon)
 */

interface NavItem {
  href: string
  icon: React.ElementType
  label: string
}

const navItems: NavItem[] = [
  { href: '/projects', icon: LayoutGrid, label: 'Projects' },
  { href: '/audiences', icon: Users, label: 'Audiences' },
  { href: '/templates', icon: Compass, label: 'Templates' },
  { href: '/analytics', icon: BarChart3, label: 'Analytics' },
  { href: '/assets', icon: FolderOpen, label: 'Assets' },
  { href: '/settings', icon: Settings, label: 'Settings' },
]

interface SidebarProps {
  className?: string
}

export function Sidebar({ className }: SidebarProps) {
  const pathname = usePathname()

  const isActive = (href: string) => {
    if (href === '/projects') {
      return pathname === '/projects' || pathname.startsWith('/projects/')
    }
    return pathname.startsWith(href)
  }

  return (
    <aside
      className={cn(
        'w-16 bg-white border-r border-gray-200 flex flex-col py-4',
        className
      )}
    >
      <nav className="flex flex-col gap-1 px-2">
        {navItems.map((item) => {
          const active = isActive(item.href)
          const Icon = item.icon

          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                'relative flex items-center justify-center w-12 h-12 rounded-lg transition-colors',
                'hover:bg-gray-100',
                active && 'bg-primary-50'
              )}
              title={item.label}
            >
              {/* Active indicator - left border */}
              {active && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-6 bg-primary-600 rounded-r" />
              )}

              <Icon
                className={cn(
                  'w-5 h-5 transition-colors',
                  active ? 'text-primary-600' : 'text-gray-500 hover:text-gray-700'
                )}
              />
            </Link>
          )
        })}
      </nav>
    </aside>
  )
}
