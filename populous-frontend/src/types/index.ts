// ============================================================================
// PROJECT TYPES
// ============================================================================

export type ProjectStatus = 'draft' | 'running' | 'completed' | 'paused'

export interface Project {
  id: string
  name: string
  description: string
  status: ProjectStatus
  audienceId?: string
  surveyId?: string
  responsesCollected: number
  responsesTarget: number
  tags: string[]
  createdAt: string
  updatedAt: string
}

// ============================================================================
// AUDIENCE TYPES
// ============================================================================

export type AudiencePurpose =
  | 'pricing_analysis'
  | 'product_launch'
  | 'concept_testing'
  | 'positioning'
  | 'market_expansion'
  | 'general_exploration'

export type IncomeLevel = 'low' | 'middle' | 'upper_middle' | 'high'

export type PrecisionLevel = 'general' | 'specific' | 'exact'

export interface AudienceProfile {
  id: string
  name: string
  age: number
  gender: 'male' | 'female' | 'other'
  education: string
  occupation: string
  income: string
  location: string
  avatarUrl?: string
}

export interface Audience {
  id: string
  name: string
  description: string
  purpose: AudiencePurpose
  ageRange: [number, number]
  genderRatio: {
    male: number
    female: number
  }
  incomeLevel: IncomeLevel
  decisionFactors: string[]
  precision: PrecisionLevel
  profileCount: number
  profiles: AudienceProfile[]
  createdAt: string
}

export interface CreateAudienceInput {
  name: string
  description: string
  purpose: AudiencePurpose
  ageRange: [number, number]
  genderRatio: {
    male: number
    female: number
  }
  incomeLevel: IncomeLevel
  decisionFactors: string[]
  precision: PrecisionLevel
}

// ============================================================================
// SURVEY TYPES
// ============================================================================

export type QuestionType =
  | 'single_choice'
  | 'multiple_choice'
  | 'rating_scale'
  | 'open_text'
  | 'ranking'

export interface Question {
  id: string
  type: QuestionType
  text: string
  options: string[]
  scaleMin?: number
  scaleMax?: number
  scaleLabels?: {
    min: string
    max: string
  }
  required: boolean
  order: number
}

export interface Survey {
  id: string
  projectId: string
  questions: Question[]
  createdAt: string
  updatedAt: string
}

// ============================================================================
// PREDICTION TYPES
// ============================================================================

export type ConfidenceLevel = 'low' | 'medium' | 'high'

export interface QuestionPrediction {
  questionId: string
  confidence: ConfidenceLevel
  predictions: Record<string, number>
  meanScore?: number
  distribution?: string
}

export interface SurveyPredictions {
  overallConfidence: ConfidenceLevel
  questions: QuestionPrediction[]
  isUpdating: boolean
}

// ============================================================================
// AI FEATURE TYPES
// ============================================================================

export interface AISuggestion {
  id: string
  type: 'question' | 'improvement'
  text: string
  reasoning: string
  suggestedQuestion?: Partial<Question>
}

export interface BiasWarning {
  questionId: string
  severity: 'warning' | 'error'
  issue: string
  suggestion: string
}

// ============================================================================
// TEMPLATE TYPES
// ============================================================================

export type TemplateType = 'audience' | 'project' | 'scenario'

export interface Template {
  id: string
  type: TemplateType
  name: string
  description: string
  features: string[]
  category: string
  popularity: number
}

// ============================================================================
// ACTIVITY TYPES
// ============================================================================

export type ActivityAction =
  | 'created'
  | 'updated'
  | 'completed'
  | 'started'
  | 'paused'
  | 'deleted'

export interface Activity {
  id: string
  userId: string
  userName: string
  userAvatar?: string
  action: ActivityAction
  targetType: 'project' | 'audience' | 'survey' | 'template'
  targetId: string
  targetName: string
  timestamp: string
}

export interface Alert {
  id: string
  severity: 'info' | 'warning' | 'error'
  title: string
  description: string
  targetType?: string
  targetId?: string
  dismissed: boolean
}

// ============================================================================
// API TYPES
// ============================================================================

export interface ApiResponse<T> {
  data: T
  success: boolean
  message?: string
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  pageSize: number
  totalPages: number
}
