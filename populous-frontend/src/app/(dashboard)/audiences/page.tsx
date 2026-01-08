'use client'

import * as React from 'react'
import { useRouter } from 'next/navigation'
import {
  AudienceList,
  AudienceDetail,
  AudienceDetailEmpty,
} from '@/components/audiences'
import type { Audience } from '@/types'

/**
 * Audiences Page matching Figma (Screenshot 4.30.22):
 * - Left sidebar with audience list
 * - Main area with selected audience detail
 */

// Mock data matching Figma screenshots
const mockAudiences: Audience[] = [
  {
    id: '1',
    name: 'Urban Gen Z Shoppers (US)',
    description: 'Young urban consumers aged 18-32 in the United States with moderate income levels, urban sustainability and active environmentalist values.',
    purpose: 'pricing_analysis',
    ageRange: [18, 32],
    genderRatio: { male: 30, female: 70 },
    incomeLevel: 'middle',
    decisionFactors: ['Price', 'Quality', 'Sustainability'],
    precision: 'specific',
    profileCount: 150,
    profiles: [
      { id: 'p1', name: 'Ryan S.', age: 24, gender: 'male', education: 'Undergraduate Student', occupation: 'College Student', income: '$40,000', location: 'Austin, TX' },
      { id: 'p2', name: 'Mark H.', age: 27, gender: 'male', education: 'High School Diploma', occupation: 'Bartender', income: '$35,000', location: 'Miami, FL' },
      { id: 'p3', name: 'Kendall J.', age: 22, gender: 'female', education: "Bachelor's Degree", occupation: 'Marketing Assistant', income: '$45,000', location: 'Los Angeles, CA' },
      { id: 'p4', name: 'Taylor M.', age: 29, gender: 'female', education: 'Undergraduate Student', occupation: 'Retail Associate', income: '$32,000', location: 'Chicago, IL' },
      { id: 'p5', name: 'Jordan K.', age: 26, gender: 'female', education: "Bachelor's Degree", occupation: 'Social Media Manager', income: '$55,000', location: 'New York, NY' },
      { id: 'p6', name: 'Alex P.', age: 31, gender: 'male', education: "Master's Degree", occupation: 'UX Designer', income: '$75,000', location: 'San Francisco, CA' },
      { id: 'p7', name: 'Sam R.', age: 23, gender: 'female', education: 'High School Diploma', occupation: 'Server', income: '$28,000', location: 'Denver, CO' },
      { id: 'p8', name: 'Chris W.', age: 28, gender: 'male', education: "Bachelor's Degree", occupation: 'Sales Rep', income: '$52,000', location: 'Seattle, WA' },
    ],
    createdAt: '2024-01-15T10:00:00Z',
  },
  {
    id: '2',
    name: 'Millennial Pet Owners',
    description: 'Pet owners aged 25-40 with disposable income for premium pet products.',
    purpose: 'product_launch',
    ageRange: [25, 40],
    genderRatio: { male: 45, female: 55 },
    incomeLevel: 'upper_middle',
    decisionFactors: ['Quality', 'Brand Trust', 'Pet Health'],
    precision: 'general',
    profileCount: 200,
    profiles: [],
    createdAt: '2024-01-10T10:00:00Z',
  },
  {
    id: '3',
    name: 'Tech Enthusiasts',
    description: 'Early adopters interested in new technology products.',
    purpose: 'concept_testing',
    ageRange: [22, 45],
    genderRatio: { male: 65, female: 35 },
    incomeLevel: 'high',
    decisionFactors: ['Innovation', 'Features', 'Brand'],
    precision: 'specific',
    profileCount: 175,
    profiles: [],
    createdAt: '2024-01-08T10:00:00Z',
  },
  {
    id: '4',
    name: 'Budget Conscious Millennials',
    description: 'Price-sensitive consumers looking for value.',
    purpose: 'pricing_analysis',
    ageRange: [28, 40],
    genderRatio: { male: 50, female: 50 },
    incomeLevel: 'low',
    decisionFactors: ['Price', 'Value', 'Reviews'],
    precision: 'general',
    profileCount: 300,
    profiles: [],
    createdAt: '2024-01-05T10:00:00Z',
  },
  {
    id: '5',
    name: 'Urban Foodies',
    description: 'Food enthusiasts in metropolitan areas.',
    purpose: 'market_expansion',
    ageRange: [25, 45],
    genderRatio: { male: 40, female: 60 },
    incomeLevel: 'middle',
    decisionFactors: ['Quality', 'Experience', 'Convenience'],
    precision: 'specific',
    profileCount: 125,
    profiles: [],
    createdAt: '2024-01-03T10:00:00Z',
  },
  {
    id: '6',
    name: 'Remote Workers',
    description: 'Professionals working from home needing productivity tools.',
    purpose: 'product_launch',
    ageRange: [28, 50],
    genderRatio: { male: 55, female: 45 },
    incomeLevel: 'upper_middle',
    decisionFactors: ['Productivity', 'Ease of Use', 'Integration'],
    precision: 'general',
    profileCount: 180,
    profiles: [],
    createdAt: '2024-01-01T10:00:00Z',
  },
  {
    id: '7',
    name: 'College Students',
    description: 'University students aged 18-24.',
    purpose: 'general_exploration',
    ageRange: [18, 24],
    genderRatio: { male: 48, female: 52 },
    incomeLevel: 'low',
    decisionFactors: ['Price', 'Convenience', 'Social Proof'],
    precision: 'general',
    profileCount: 250,
    profiles: [],
    createdAt: '2023-12-28T10:00:00Z',
  },
]

export default function AudiencesPage() {
  const router = useRouter()
  const [selectedAudience, setSelectedAudience] = React.useState<Audience | null>(
    mockAudiences[0] || null
  )

  const handleNewAudience = () => {
    router.push('/audiences/create')
  }

  return (
    <div className="flex h-[calc(100vh-64px)]">
      {/* Audience List Sidebar */}
      <AudienceList
        audiences={mockAudiences}
        selectedId={selectedAudience?.id}
        onSelect={setSelectedAudience}
        onNewAudience={handleNewAudience}
      />

      {/* Audience Detail View */}
      {selectedAudience ? (
        <AudienceDetail
          audience={selectedAudience}
          onEdit={() => console.log('Edit audience')}
          onDelete={() => console.log('Delete audience')}
        />
      ) : (
        <AudienceDetailEmpty />
      )}
    </div>
  )
}
