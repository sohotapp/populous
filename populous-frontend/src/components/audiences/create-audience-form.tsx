'use client'

import * as React from 'react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Upload, Users, X } from 'lucide-react'
import { cn } from '@/lib/utils'
import type { AudiencePurpose, IncomeLevel, PrecisionLevel } from '@/types'

/**
 * Create Audience Form matching Figma exactly (Screenshot 4.30.30):
 *
 * Left side (form):
 * 1. Audience Title
 * 2. Describe your audience
 * 3. Purpose pills (2 rows x 3)
 * 4. Age range (dual inputs)
 * 5. Gender ratio slider
 * 6. Income level pills
 * 7. Decision factors dropdown
 * 8. Precision dropdown
 * 9. CSV upload zone
 * 10. Generate Audience button
 *
 * Right side:
 * - Empty state OR generated audience preview
 */

// Purpose options matching Figma
const purposeOptions: { value: AudiencePurpose; label: string }[] = [
  { value: 'pricing_analysis', label: 'Pricing analysis' },
  { value: 'product_launch', label: 'Product launch' },
  { value: 'concept_testing', label: 'Concept testing' },
  { value: 'positioning', label: 'Positioning' },
  { value: 'market_expansion', label: 'Market expansion' },
  { value: 'general_exploration', label: 'General exploration' },
]

// Income level options matching Figma
const incomeOptions: { value: IncomeLevel; label: string }[] = [
  { value: 'low', label: 'Low' },
  { value: 'middle', label: 'Middle' },
  { value: 'upper_middle', label: 'Upper-middle' },
  { value: 'high', label: 'High' },
]

// Decision factors options
const decisionFactorOptions = [
  'Price',
  'Quality',
  'Brand Trust',
  'Convenience',
  'Sustainability',
  'Social Proof',
  'Features',
  'Customer Service',
]

// Precision options
const precisionOptions: { value: PrecisionLevel; label: string }[] = [
  { value: 'general', label: 'General - Broader demographic matching' },
  { value: 'specific', label: 'Specific - Tighter criteria matching' },
  { value: 'exact', label: 'Exact - Precise attribute matching' },
]

interface CreateAudienceFormProps {
  onSubmit: (data: CreateAudienceFormData) => void
  onCancel: () => void
  isLoading?: boolean
}

export interface CreateAudienceFormData {
  name: string
  description: string
  purpose: AudiencePurpose
  ageMin: number
  ageMax: number
  genderRatio: number // 0-100 (male percentage)
  incomeLevel: IncomeLevel
  decisionFactors: string[]
  precision: PrecisionLevel
  csvFile?: File
}

export function CreateAudienceForm({
  onSubmit,
  onCancel,
  isLoading = false,
}: CreateAudienceFormProps) {
  const [name, setName] = React.useState('')
  const [description, setDescription] = React.useState('')
  const [purpose, setPurpose] = React.useState<AudiencePurpose>('pricing_analysis')
  const [ageMin, setAgeMin] = React.useState(18)
  const [ageMax, setAgeMax] = React.useState(32)
  const [genderRatio, setGenderRatio] = React.useState(30) // Male percentage
  const [incomeLevel, setIncomeLevel] = React.useState<IncomeLevel>('middle')
  const [decisionFactors, setDecisionFactors] = React.useState<string>('')
  const [precision, setPrecision] = React.useState<PrecisionLevel>('general')
  const [csvFile, setCsvFile] = React.useState<File | null>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSubmit({
      name,
      description,
      purpose,
      ageMin,
      ageMax,
      genderRatio,
      incomeLevel,
      decisionFactors: decisionFactors ? [decisionFactors] : [],
      precision,
      csvFile: csvFile || undefined,
    })
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      setCsvFile(file)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Audience Title */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          Audience Title
        </label>
        <Input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="e.g Millennial Pet Owners"
          required
        />
      </div>

      {/* Description */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          Describe your audience
        </label>
        <Textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="e.g BCT attack to seize OBJ IRON, enemy reinforced BN with armor company defending in depth. 72-hour timeline, limited CAS, MSR TAMPA must remain open."
          rows={4}
        />
      </div>

      {/* Purpose Pills */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          What are you creating this audience for?
        </label>
        <div className="grid grid-cols-3 gap-2">
          {purposeOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => setPurpose(option.value)}
              className={cn(
                'px-4 py-2 text-sm font-medium rounded-md border transition-colors',
                purpose === option.value
                  ? 'bg-primary-600 text-white border-primary-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              )}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Age Range */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          How old are the people in this audience?
        </label>
        <div className="flex items-center gap-3">
          <Input
            type="number"
            value={ageMin}
            onChange={(e) => setAgeMin(Number(e.target.value))}
            placeholder="18 Years"
            min={13}
            max={100}
            className="w-32"
          />
          <span className="text-gray-500">to</span>
          <Input
            type="number"
            value={ageMax}
            onChange={(e) => setAgeMax(Number(e.target.value))}
            placeholder="32 Years"
            min={13}
            max={100}
            className="w-32"
          />
        </div>
      </div>

      {/* Gender Ratio Slider */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          What should be the Gender Ratio?
        </label>
        <div className="flex items-center justify-between text-sm text-gray-600 mb-2">
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-blue-500" />
            Male ({genderRatio}%)
          </span>
          <span className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full bg-pink-500" />
            Female ({100 - genderRatio}%)
          </span>
        </div>
        <input
          type="range"
          min="0"
          max="100"
          value={genderRatio}
          onChange={(e) => setGenderRatio(Number(e.target.value))}
          className="w-full h-2 rounded-full appearance-none cursor-pointer"
          style={{
            background: `linear-gradient(90deg, #3B82F6 ${genderRatio}%, #EC4899 ${genderRatio}%)`,
          }}
        />
      </div>

      {/* Income Level Pills */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          How would you describe their income level?
        </label>
        <div className="flex gap-2">
          {incomeOptions.map((option) => (
            <button
              key={option.value}
              type="button"
              onClick={() => setIncomeLevel(option.value)}
              className={cn(
                'px-4 py-2 text-sm font-medium rounded-md border transition-colors',
                incomeLevel === option.value
                  ? 'bg-primary-600 text-white border-primary-600'
                  : 'bg-white text-gray-700 border-gray-300 hover:bg-gray-50'
              )}
            >
              {option.label}
            </button>
          ))}
        </div>
      </div>

      {/* Decision Factors */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          What matters most when they make decisions?
        </label>
        <Select value={decisionFactors} onValueChange={setDecisionFactors}>
          <SelectTrigger>
            <SelectValue placeholder="Select Option" />
          </SelectTrigger>
          <SelectContent>
            {decisionFactorOptions.map((factor) => (
              <SelectItem key={factor} value={factor}>
                {factor}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Precision */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          How precise does this audience need to be?
        </label>
        <Select value={precision} onValueChange={(v) => setPrecision(v as PrecisionLevel)}>
          <SelectTrigger>
            <SelectValue placeholder="Select Option" />
          </SelectTrigger>
          <SelectContent>
            {precisionOptions.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* CSV Upload */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          Upload CSV of real customer attributes
        </label>
        <div
          className={cn(
            'border-2 border-dashed rounded-lg p-6 text-center transition-colors',
            csvFile ? 'border-primary-300 bg-primary-50' : 'border-gray-300 hover:border-gray-400'
          )}
        >
          {csvFile ? (
            <div className="flex items-center justify-center gap-2">
              <span className="text-sm text-gray-700">{csvFile.name}</span>
              <button
                type="button"
                onClick={() => setCsvFile(null)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          ) : (
            <label className="cursor-pointer">
              <Upload className="w-6 h-6 text-gray-400 mx-auto mb-2" />
              <span className="text-sm text-gray-600">
                Drag and drop or <span className="text-primary-600">Choose File</span>
              </span>
              <input
                type="file"
                accept=".csv"
                onChange={handleFileChange}
                className="hidden"
              />
            </label>
          )}
        </div>
      </div>

      {/* Generate Button */}
      <Button type="submit" className="w-full" size="lg" loading={isLoading}>
        Generate Audience
      </Button>
    </form>
  )
}

/**
 * Empty state for right panel
 */
export function CreateAudienceEmptyState() {
  return (
    <div className="flex-1 flex items-center justify-center p-8 bg-gray-50">
      <div className="text-center">
        <div className="w-16 h-16 bg-gray-200 rounded-full flex items-center justify-center mx-auto mb-4">
          <Users className="w-8 h-8 text-gray-400" />
        </div>
        <p className="text-sm text-gray-500 max-w-xs">
          Create your first audience by answering few questions.
        </p>
      </div>
    </div>
  )
}
