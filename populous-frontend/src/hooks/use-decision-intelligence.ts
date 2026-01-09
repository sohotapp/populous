'use client'

import { useState, useCallback } from 'react'
import { decisionIntelligenceApi } from '@/lib/api'
import type {
  Decision,
  CreateDecisionInput,
  World,
  CreateWorldInput,
  DIAudience,
  GenerativeAgent,
  ChatMessage,
  AgentChatResponse,
} from '@/types'

// ============================================================================
// useDecisions Hook
// ============================================================================

export function useDecisions() {
  const [decisions, setDecisions] = useState<Decision[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchDecisions = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await decisionIntelligenceApi.listDecisions()
      setDecisions(result.decisions)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch decisions')
    } finally {
      setLoading(false)
    }
  }, [])

  const createDecision = useCallback(async (data: CreateDecisionInput) => {
    setLoading(true)
    setError(null)
    try {
      const result = await decisionIntelligenceApi.createDecision(data)
      setDecisions(prev => [...prev, result.decision])
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create decision')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    decisions,
    loading,
    error,
    fetchDecisions,
    createDecision,
  }
}

// ============================================================================
// useWorlds Hook
// ============================================================================

export function useWorlds() {
  const [worlds, setWorlds] = useState<World[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchWorlds = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await decisionIntelligenceApi.listWorlds()
      setWorlds(result.worlds)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch worlds')
    } finally {
      setLoading(false)
    }
  }, [])

  const createWorld = useCallback(async (data: CreateWorldInput) => {
    setLoading(true)
    setError(null)
    try {
      const result = await decisionIntelligenceApi.createWorld(data)
      setWorlds(prev => [...prev, result.world])
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create world')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    worlds,
    loading,
    error,
    fetchWorlds,
    createWorld,
  }
}

// ============================================================================
// useDIAudience Hook
// ============================================================================

export function useDIAudience(audienceId?: string) {
  const [audience, setAudience] = useState<DIAudience | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchAudience = useCallback(async (id: string, limit?: number) => {
    setLoading(true)
    setError(null)
    try {
      const result = await decisionIntelligenceApi.getAudience(id, limit)
      setAudience(result)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch audience')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const createAudience = useCallback(async (data: {
    name: string
    description: string
    size: number
    world_id: string
    segment_distribution?: Record<string, number>
  }) => {
    setLoading(true)
    setError(null)
    try {
      const result = await decisionIntelligenceApi.createAudience(data)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create audience')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    audience,
    loading,
    error,
    fetchAudience,
    createAudience,
  }
}

// ============================================================================
// useAgentChat Hook
// ============================================================================

export function useAgentChat(audienceId: string, agentId: string) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [agent, setAgent] = useState<GenerativeAgent | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const sendMessage = useCallback(async (message: string): Promise<AgentChatResponse> => {
    setLoading(true)
    setError(null)

    // Add user message to local state
    const userMessage: ChatMessage = { role: 'user', content: message }
    setMessages(prev => [...prev, userMessage])

    try {
      const response = await decisionIntelligenceApi.chatWithAgent(
        audienceId,
        agentId,
        message,
        messages
      )

      // Add assistant response to local state
      const assistantMessage: ChatMessage = { role: 'assistant', content: response.response }
      setMessages(prev => [...prev, assistantMessage])

      return response
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to send message')
      // Remove the optimistic user message on error
      setMessages(prev => prev.slice(0, -1))
      throw err
    } finally {
      setLoading(false)
    }
  }, [audienceId, agentId, messages])

  const clearChat = useCallback(() => {
    setMessages([])
    setError(null)
  }, [])

  return {
    messages,
    agent,
    loading,
    error,
    sendMessage,
    clearChat,
  }
}

// ============================================================================
// usePredictions Hook
// ============================================================================

export function usePredictions() {
  const [predictions, setPredictions] = useState<{
    overall_confidence: string
    predictions: Array<{
      question: string
      type: string
      distribution?: Record<string, number>
      mean?: number
      themes?: Array<{ theme: string; percent: number }>
      confidence: string
    }>
  } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const predict = useCallback(async (
    audienceId: string,
    questions: Array<{ text: string; type: string; options?: string[]; scale?: number }>
  ) => {
    setLoading(true)
    setError(null)
    try {
      const result = await decisionIntelligenceApi.predictSurveyResponses(audienceId, questions)
      setPredictions(result)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate predictions')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    predictions,
    loading,
    error,
    predict,
  }
}

// ============================================================================
// useBiasCheck Hook
// ============================================================================

export function useBiasCheck() {
  const [result, setResult] = useState<{
    has_bias: boolean
    issues: Array<{ type: string; description: string; severity: string }>
    suggestion?: string
  } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const checkBias = useCallback(async (question: string, options?: string[]) => {
    setLoading(true)
    setError(null)
    try {
      const result = await decisionIntelligenceApi.checkBias(question, options)
      setResult(result)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to check bias')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const clearResult = useCallback(() => {
    setResult(null)
    setError(null)
  }, [])

  return {
    result,
    loading,
    error,
    checkBias,
    clearResult,
  }
}

// ============================================================================
// useTemplates Hook
// ============================================================================

export function useDITemplates() {
  const [audienceTemplates, setAudienceTemplates] = useState<Array<{
    id: string
    name: string
    description: string
    size: number
    segments: string[]
  }>>([])
  const [scenarioTemplates, setScenarioTemplates] = useState<Array<{
    id: string
    name: string
    description: string
    decision_type: string
  }>>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const fetchAudienceTemplates = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await decisionIntelligenceApi.getAudienceTemplates()
      setAudienceTemplates(result.templates)
      return result.templates
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch audience templates')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  const fetchScenarioTemplates = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await decisionIntelligenceApi.getScenarioTemplates()
      setScenarioTemplates(result.templates)
      return result.templates
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch scenario templates')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    audienceTemplates,
    scenarioTemplates,
    loading,
    error,
    fetchAudienceTemplates,
    fetchScenarioTemplates,
  }
}

// ============================================================================
// useDIHealth Hook
// ============================================================================

export function useDIHealth() {
  const [health, setHealth] = useState<{
    status: string
    decisions: number
    worlds: number
    audiences: number
    simulations: number
  } | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const checkHealth = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const result = await decisionIntelligenceApi.healthCheck()
      setHealth(result)
      return result
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to check health')
      throw err
    } finally {
      setLoading(false)
    }
  }, [])

  return {
    health,
    loading,
    error,
    checkHealth,
  }
}
