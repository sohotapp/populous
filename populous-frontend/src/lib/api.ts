import axios, { AxiosInstance } from 'axios'
import type {
  Project,
  Audience,
  Survey,
  SurveyPredictions,
  Template,
  AISuggestion,
  BiasWarning,
  CreateAudienceInput,
  Question,
  Decision,
  CreateDecisionInput,
  World,
  CreateWorldInput,
  DIAudience,
  GenerativeAgent,
  TemporalSimulation,
  Trace,
  Recommendation,
  ChatMessage,
  AgentChatResponse,
} from '@/types'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// ============================================================================
// PROJECTS API
// ============================================================================

export const projectsApi = {
  list: async (): Promise<Project[]> => {
    const response = await apiClient.get('/projects')
    return response.data
  },

  get: async (id: string): Promise<Project> => {
    const response = await apiClient.get(`/projects/${id}`)
    return response.data
  },

  create: async (data: Partial<Project>): Promise<Project> => {
    const response = await apiClient.post('/projects', data)
    return response.data
  },

  update: async (id: string, data: Partial<Project>): Promise<Project> => {
    const response = await apiClient.put(`/projects/${id}`, data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/projects/${id}`)
  },
}

// ============================================================================
// AUDIENCES API
// ============================================================================

export const audiencesApi = {
  list: async (): Promise<Audience[]> => {
    const response = await apiClient.get('/audiences')
    return response.data
  },

  get: async (id: string): Promise<Audience> => {
    const response = await apiClient.get(`/audiences/${id}`)
    return response.data
  },

  create: async (data: CreateAudienceInput): Promise<Audience> => {
    const response = await apiClient.post('/audiences', data)
    return response.data
  },

  generate: async (data: CreateAudienceInput): Promise<Audience> => {
    const response = await apiClient.post('/audiences/generate', data)
    return response.data
  },

  delete: async (id: string): Promise<void> => {
    await apiClient.delete(`/audiences/${id}`)
  },

  importCsv: async (id: string, file: File): Promise<Audience> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post(`/audiences/${id}/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },
}

// ============================================================================
// SURVEYS API
// ============================================================================

export const surveysApi = {
  get: async (projectId: string): Promise<Survey> => {
    const response = await apiClient.get(`/projects/${projectId}/survey`)
    return response.data
  },

  update: async (projectId: string, questions: Question[]): Promise<Survey> => {
    const response = await apiClient.put(`/projects/${projectId}/survey`, { questions })
    return response.data
  },

  predict: async (projectId: string): Promise<SurveyPredictions> => {
    const response = await apiClient.post(`/projects/${projectId}/survey/predict`)
    return response.data
  },
}

// ============================================================================
// AI FEATURES API
// ============================================================================

export const aiApi = {
  suggestQuestion: async (
    surveyId: string,
    context: { questions: Question[]; goal?: string }
  ): Promise<AISuggestion> => {
    const response = await apiClient.post('/ai/suggest-question', {
      surveyId,
      ...context,
    })
    return response.data
  },

  checkBias: async (question: Question): Promise<BiasWarning | null> => {
    const response = await apiClient.post('/ai/check-bias', { question })
    return response.data
  },
}

// ============================================================================
// TEMPLATES API
// ============================================================================

export const templatesApi = {
  list: async (type?: string): Promise<Template[]> => {
    const params = type ? { type } : {}
    const response = await apiClient.get('/templates', { params })
    return response.data
  },

  get: async (id: string): Promise<Template> => {
    const response = await apiClient.get(`/templates/${id}`)
    return response.data
  },

  use: async (id: string): Promise<{ type: string; created: unknown }> => {
    const response = await apiClient.post(`/templates/${id}/use`)
    return response.data
  },
}

// ============================================================================
// HEALTH CHECK
// ============================================================================

export const healthApi = {
  check: async (): Promise<{ status: string }> => {
    const response = await apiClient.get('/health')
    return response.data
  },
}

// ============================================================================
// DECISION INTELLIGENCE API
// ============================================================================

export const decisionIntelligenceApi = {
  // Decisions
  createDecision: async (data: CreateDecisionInput): Promise<{ id: string; decision: Decision }> => {
    const response = await apiClient.post('/api/di/decisions', data)
    return response.data
  },

  listDecisions: async (): Promise<{ decisions: Decision[] }> => {
    const response = await apiClient.get('/api/di/decisions')
    return response.data
  },

  getDecision: async (id: string): Promise<Decision> => {
    const response = await apiClient.get(`/api/di/decisions/${id}`)
    return response.data
  },

  // Worlds
  createWorld: async (data: CreateWorldInput): Promise<{ id: string; world: World }> => {
    const response = await apiClient.post('/api/di/worlds', data)
    return response.data
  },

  listWorlds: async (): Promise<{ worlds: World[] }> => {
    const response = await apiClient.get('/api/di/worlds')
    return response.data
  },

  getWorld: async (id: string): Promise<World> => {
    const response = await apiClient.get(`/api/di/worlds/${id}`)
    return response.data
  },

  // Audiences (DI-specific generative agents)
  createAudience: async (data: {
    name: string
    description: string
    size: number
    world_id: string
    segment_distribution?: Record<string, number>
  }): Promise<{ id: string; status: string; size: number }> => {
    const response = await apiClient.post('/api/di/audiences', data)
    return response.data
  },

  listAudiences: async (): Promise<{ audiences: Array<{ id: string; size: number; status: string }> }> => {
    const response = await apiClient.get('/api/di/audiences')
    return response.data
  },

  getAudience: async (id: string, limit?: number): Promise<DIAudience> => {
    const params = limit ? { limit } : {}
    const response = await apiClient.get(`/api/di/audiences/${id}`, { params })
    return response.data
  },

  // Agent Chat
  chatWithAgent: async (
    audienceId: string,
    agentId: string,
    message: string,
    conversationHistory: ChatMessage[] = []
  ): Promise<AgentChatResponse> => {
    const response = await apiClient.post(
      `/api/di/audiences/${audienceId}/agents/${agentId}/chat`,
      { message, conversation_history: conversationHistory }
    )
    return response.data
  },

  // Predictions
  predictSurveyResponses: async (
    audienceId: string,
    questions: Array<{ text: string; type: string; options?: string[]; scale?: number }>
  ): Promise<{
    overall_confidence: string
    predictions: Array<{
      question: string
      type: string
      distribution?: Record<string, number>
      mean?: number
      themes?: Array<{ theme: string; percent: number }>
      confidence: string
    }>
  }> => {
    const response = await apiClient.post('/api/di/predictions/survey', {
      audience_id: audienceId,
      questions,
    })
    return response.data
  },

  // Bias Check
  checkBias: async (
    question: string,
    options?: string[]
  ): Promise<{
    has_bias: boolean
    issues: Array<{ type: string; description: string; severity: string }>
    suggestion?: string
  }> => {
    const response = await apiClient.post('/api/di/bias/check', {
      question,
      options: options || [],
    })
    return response.data
  },

  // Templates
  getAudienceTemplates: async (): Promise<{
    templates: Array<{
      id: string
      name: string
      description: string
      size: number
      segments: string[]
    }>
  }> => {
    const response = await apiClient.get('/api/di/templates/audiences')
    return response.data
  },

  getScenarioTemplates: async (): Promise<{
    templates: Array<{
      id: string
      name: string
      description: string
      decision_type: string
    }>
  }> => {
    const response = await apiClient.get('/api/di/templates/scenarios')
    return response.data
  },

  // Health
  healthCheck: async (): Promise<{
    status: string
    decisions: number
    worlds: number
    audiences: number
    simulations: number
  }> => {
    const response = await apiClient.get('/api/di/health')
    return response.data
  },
}

export default apiClient
