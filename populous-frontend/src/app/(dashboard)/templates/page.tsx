'use client'

import * as React from 'react'
import { PageContainer, PageHeader } from '@/components/layout'
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'
import type { Template, TemplateType } from '@/types'

/**
 * Templates Library Page matching Figma (Screenshots 4.30.47, 4.30.52, 4.30.56):
 *
 * Header:
 * - "Templates" title
 *
 * Content:
 * - Tab filters: Audiences, Projects, Scenarios
 * - 4-column grid of template cards
 * - Each card: title, description bullets, action button
 */

// Mock templates matching Figma
const mockTemplates: Template[] = [
  // Audiences
  {
    id: 'a1',
    type: 'audience',
    name: 'Urban Gen Z Shoppers',
    description: 'Young urban consumers with moderate income',
    features: ['Ages 18-32', 'Urban locations', 'Sustainability-focused'],
    category: 'Consumer',
    popularity: 95,
  },
  {
    id: 'a2',
    type: 'audience',
    name: 'Tech Early Adopters',
    description: 'Technology enthusiasts who try new products first',
    features: ['High income', 'Innovation-driven', 'Brand loyal'],
    category: 'Tech',
    popularity: 88,
  },
  {
    id: 'a3',
    type: 'audience',
    name: 'Budget Conscious Parents',
    description: 'Parents focused on value and family needs',
    features: ['Ages 28-45', 'Price sensitive', 'Quality aware'],
    category: 'Family',
    popularity: 82,
  },
  {
    id: 'a4',
    type: 'audience',
    name: 'Health & Wellness Enthusiasts',
    description: 'Consumers prioritizing health and wellness',
    features: ['Active lifestyle', 'Premium products', 'Organic preference'],
    category: 'Health',
    popularity: 78,
  },
  // Projects
  {
    id: 'p1',
    type: 'project',
    name: 'Pricing Sensitivity Study',
    description: 'Understand how price changes affect purchase intent',
    features: ['Van Westendorp analysis', 'Price elasticity', 'Willingness to pay'],
    category: 'Pricing',
    popularity: 92,
  },
  {
    id: 'p2',
    type: 'project',
    name: 'Product Concept Test',
    description: 'Validate new product ideas before development',
    features: ['Concept appeal', 'Purchase intent', 'Feature prioritization'],
    category: 'Product',
    popularity: 89,
  },
  {
    id: 'p3',
    type: 'project',
    name: 'Brand Perception Survey',
    description: 'Measure brand awareness and sentiment',
    features: ['Brand recognition', 'Attribute association', 'NPS measurement'],
    category: 'Brand',
    popularity: 85,
  },
  {
    id: 'p4',
    type: 'project',
    name: 'Customer Satisfaction Study',
    description: 'Track satisfaction and identify improvement areas',
    features: ['CSAT scoring', 'Feedback collection', 'Loyalty drivers'],
    category: 'Experience',
    popularity: 91,
  },
  // Scenarios
  {
    id: 's1',
    type: 'scenario',
    name: 'Price Increase Stress Test',
    description: 'Simulate customer response to price increases',
    features: ['Churn prediction', 'Price sensitivity', 'Competitive switching'],
    category: 'Pricing',
    popularity: 87,
  },
  {
    id: 's2',
    type: 'scenario',
    name: 'Market Entry Simulation',
    description: 'Model entry into new market segments',
    features: ['Adoption modeling', 'Competitive response', 'Share prediction'],
    category: 'Strategy',
    popularity: 83,
  },
  {
    id: 's3',
    type: 'scenario',
    name: 'Feature Launch Impact',
    description: 'Predict impact of new feature releases',
    features: ['Adoption curve', 'Satisfaction impact', 'Revenue projection'],
    category: 'Product',
    popularity: 80,
  },
  {
    id: 's4',
    type: 'scenario',
    name: 'Competitive Threat Analysis',
    description: 'Model response to competitive actions',
    features: ['Market share shift', 'Customer migration', 'Defense strategies'],
    category: 'Strategy',
    popularity: 76,
  },
]

export default function TemplatesPage() {
  const [activeTab, setActiveTab] = React.useState<TemplateType>('audience')

  const filteredTemplates = mockTemplates.filter((t) => t.type === activeTab)

  const handleUseTemplate = (template: Template) => {
    console.log('Using template:', template)
    // Navigate to create page with template data
  }

  return (
    <PageContainer>
      <PageHeader title="Templates" />

      <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as TemplateType)}>
        <TabsList className="mb-6">
          <TabsTrigger value="audience">Audiences</TabsTrigger>
          <TabsTrigger value="project">Projects</TabsTrigger>
          <TabsTrigger value="scenario">Scenarios</TabsTrigger>
        </TabsList>

        <TabsContent value={activeTab}>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {filteredTemplates.map((template) => (
              <TemplateCard
                key={template.id}
                template={template}
                onUse={() => handleUseTemplate(template)}
              />
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </PageContainer>
  )
}

/**
 * Template card component
 */
interface TemplateCardProps {
  template: Template
  onUse: () => void
}

function TemplateCard({ template, onUse }: TemplateCardProps) {
  const buttonText = {
    audience: 'Use Audience',
    project: 'Use Project',
    scenario: 'Use Scenario',
  }[template.type]

  return (
    <Card className="flex flex-col">
      <CardHeader className="pb-2">
        <CardTitle className="text-base">{template.name}</CardTitle>
        <CardDescription>{template.description}</CardDescription>
      </CardHeader>
      <CardContent className="flex-1">
        <ul className="space-y-1 mb-4">
          {template.features.map((feature, i) => (
            <li key={i} className="text-sm text-gray-600 flex items-start gap-2">
              <span className="text-gray-400 mt-1">•</span>
              {feature}
            </li>
          ))}
        </ul>
        <Button variant="secondary" className="w-full" onClick={onUse}>
          {buttonText}
        </Button>
      </CardContent>
    </Card>
  )
}
