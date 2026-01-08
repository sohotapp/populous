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

export default apiClient
