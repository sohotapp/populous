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

// ============================================================================
// DECISION INTELLIGENCE TYPES
// ============================================================================

export type DecisionStatus = 'draft' | 'analyzing' | 'simulating' | 'ready' | 'executed'

export interface DecisionOption {
  id: string
  name: string
  description: string
  parameters: Record<string, number | string | boolean>
}

export interface DecisionConstraint {
  id: string
  metric: string
  operator: '>=' | '<=' | '==' | '>' | '<'
  value: number
  description: string
}

export interface SuccessCriteria {
  primary_metric: string
  target_value: number
  secondary_metrics: Record<string, number>
  time_horizon_days: number
}

export interface Decision {
  id: string
  title: string
  description: string
  options: DecisionOption[]
  constraints: DecisionConstraint[]
  success_criteria: SuccessCriteria
  status: DecisionStatus
  world_id?: string
  audience_id?: string
  simulation_id?: string
  created_at: string
  updated_at: string
}

export interface CreateDecisionInput {
  title: string
  description: string
  options: Omit<DecisionOption, 'id'>[]
  constraints?: Omit<DecisionConstraint, 'id'>[]
  success_criteria: SuccessCriteria
}

// ============================================================================
// WORLD TYPES (Market Context)
// ============================================================================

export interface Segment {
  id: string
  name: string
  size: number
  price_sensitivity: number
  brand_loyalty: number
  risk_tolerance: number
  description: string
}

export interface Competitor {
  id: string
  name: string
  market_share: number
  positioning: string
  strengths: string[]
  weaknesses: string[]
}

export interface Product {
  id: string
  name: string
  base_price: number
  features: string[]
  strengths: string[]
  weaknesses: string[]
}

export interface World {
  id: string
  name: string
  description: string
  total_addressable_market: number
  market_growth_rate: number
  segments: Segment[]
  competitors: Competitor[]
  your_product: Product
  your_market_share: number
  created_at: string
}

export interface CreateWorldInput {
  name: string
  description: string
  total_addressable_market: number
  market_growth_rate: number
  segments: Omit<Segment, 'id'>[]
  competitors: Omit<Competitor, 'id'>[]
  your_product: Omit<Product, 'id'>
  your_market_share: number
}

// ============================================================================
// GENERATIVE AGENT TYPES (Stanford Architecture)
// ============================================================================

export type AgentState = 'unaware' | 'aware' | 'interested' | 'considering' | 'evaluating' | 'decided' | 'churned' | 'retained'

export interface AgentMemory {
  timestamp: number
  description: string
  importance: number
  memory_type: 'observation' | 'reflection' | 'plan'
}

export interface AgentReflection {
  timestamp: number
  insight: string
  evidence_memories: string[]
  importance: number
}

export interface GenerativeAgent {
  id: string
  name: string
  age: number
  occupation: string
  income: number
  location: string
  education: string
  segment_id: string
  personality: {
    openness: number
    conscientiousness: number
    extraversion: number
    agreeableness: number
    neuroticism: number
  }
  values: string[]
  pain_points: string[]
  goals: string[]
  price_sensitivity: number
  brand_loyalty: number
  risk_tolerance: number
  social_influence: number
  decision_style: 'analytical' | 'intuitive' | 'social' | 'habitual'
  state: AgentState
  memory_stream: AgentMemory[]
  reflections: AgentReflection[]
}

export interface DIAudience {
  id: string
  size: number
  status: 'generating' | 'ready'
  agents: GenerativeAgent[]
}

// ============================================================================
// SIMULATION TYPES
// ============================================================================

export type SimulationStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface DailySnapshot {
  day: number
  metrics: Record<string, number>
  state_distribution: Record<AgentState, number>
  events: string[]
}

export interface BranchResult {
  branch_id: number
  final_metrics: Record<string, number>
  timeline: DailySnapshot[]
  key_events: string[]
}

export interface AggregateResults {
  retention: {
    mean: number
    std: number
    p5: number
    p25: number
    p75: number
    p95: number
  }
  churn: {
    mean: number
    std: number
    p5: number
    p25: number
    p75: number
    p95: number
  }
  confidence: number
}

export interface TemporalSimulation {
  id: string
  decision_id: string
  option_id: string
  config: {
    num_branches: number
    days_to_simulate: number
    seed?: number
  }
  status: SimulationStatus
  progress: number
  branch_results: BranchResult[]
  aggregate_results?: AggregateResults
  created_at: string
  completed_at?: string
}

// ============================================================================
// CAUSAL TRACE TYPES
// ============================================================================

export interface TraceNode {
  id: string
  node_type: 'event' | 'decision' | 'outcome' | 'belief_change'
  label: string
  timestamp: number
  agent_ids: string[]
  metrics: Record<string, number>
}

export interface TraceEdge {
  source: string
  target: string
  relationship: 'causes' | 'influences' | 'enables' | 'prevents'
  strength: number
}

export interface Counterfactual {
  description: string
  original_outcome: number
  counterfactual_outcome: number
  difference: number
  confidence: number
}

export interface Sensitivity {
  factor: string
  range: [number, number]
  outcome_range: [number, number]
  elasticity: number
}

export interface Trace {
  id: string
  simulation_id: string
  nodes: TraceNode[]
  edges: TraceEdge[]
  root_causes: string[]
  key_drivers: string[]
  counterfactuals: Counterfactual[]
  sensitivities: Sensitivity[]
}

// ============================================================================
// RECOMMENDATION TYPES
// ============================================================================

export interface ActionItem {
  id: string
  action: string
  description: string
  owner: string
  due_date: string
  phase: string
  dependencies: string[]
  approval_required: boolean
}

export interface Contingency {
  id: string
  trigger: string
  detection: string
  response: string
  escalation: string
  timeframe: string
}

export interface ApprovalGate {
  id: string
  condition: string
  approver: string
  threshold: string
}

export interface Recommendation {
  decision_id: string
  recommended_option_id: string
  recommended_option_name: string
  confidence: number
  expected_outcome: {
    retention_rate: number
    churn_rate: number
    confidence_interval: string
  }
  reasoning: string
  comparison_to_alternatives: Array<{
    option_id: string
    retention: string
    why_not: string
  }>
  execution_plan: ActionItem[]
  contingencies: Contingency[]
  approval_gates: ApprovalGate[]
  key_risks: string[]
  monitoring_metrics: Array<{
    metric: string
    frequency: string
    threshold: string
    owner: string
  }>
  executive_summary: string
}

// ============================================================================
// AGENT CHAT TYPES
// ============================================================================

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface AgentChatResponse {
  agent_id: string
  response: string
  agent_name: string
  agent_state: AgentState
}

export interface DecisionJourneyEvent {
  timestamp: number
  type: string
  description?: string
  choice?: string
  reasoning?: string
  confidence?: number
  importance?: number
}
