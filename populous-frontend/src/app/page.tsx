'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import {
  Search, Zap, GitBranch, BarChart3, Target,
  Building2, Users, Bot, Layers, Play, Plus,
  ChevronRight, Sparkles, FolderOpen,
  FileText, Minus, RotateCcw, X, Loader2,
  CheckCircle, AlertCircle, Send, TrendingUp,
  DollarSign, Clock, Award, AlertTriangle,
  MessageSquare, ChevronDown, ExternalLink,
  Command
} from 'lucide-react'

// =============================================================================
// TYPES
// =============================================================================

type NodeType = 'research' | 'batch' | 'prediction' | 'analysis' | 'chat' | 'startup'

interface Node {
  id: string
  type: NodeType
  x: number
  y: number
  title: string
  subtitle?: string
  status?: 'idle' | 'running' | 'complete' | 'error'
  data?: any
}

interface Edge {
  id: string
  from: string
  to: string
  animated?: boolean
}

interface StartupPrediction {
  startup_id: string
  startup_name: string
  unicorn_probability: number
  centaur_probability: number
  success_probability: number
  failure_probability: number
  expected_valuation: number
  valuation_p10: number
  valuation_p50: number
  valuation_p90: number
  years_to_unicorn?: number
  years_to_exit: number
  team_score: number
  market_score: number
  traction_score: number
  timing_score: number
  capital_score: number
  key_strengths: string[]
  key_risks: string[]
  detailed_reasoning: string
  prediction_confidence: number
  data_quality: string
}

interface BatchPrediction {
  batch_name: string
  batch_size: number
  expected_unicorns: number
  unicorn_range: [number, number]
  expected_centaurs: number
  expected_total_value: number
  startups: StartupPrediction[]
  top_unicorn_candidates: string[]
  highest_risk_startups: string[]
  batch_quality_score: number
  market_timing_score: number
  detailed_analysis?: string
}

// =============================================================================
// DESIGN SYSTEM - LINEAR INSPIRED
// =============================================================================

const colors = {
  // Core backgrounds - Linear's signature dark palette
  bg: '#0A0A0B',
  bgSecondary: '#111113',
  bgTertiary: '#18181B',
  bgElevated: '#1C1C1F',

  // Accent - Linear's signature purple
  accent: '#5E6AD2',
  accentMuted: '#5E6AD220',
  accentHover: '#7C85E0',
  accentSubtle: '#5E6AD215',

  // Text hierarchy
  textPrimary: '#EDEDEF',
  textSecondary: '#8B8B8D',
  textMuted: '#5C5C5E',
  textFaint: '#3F3F42',

  // Borders - very subtle
  border: '#1F1F22',
  borderSubtle: '#18181B',
  borderHover: '#2A2A2E',

  // Status colors - slightly muted
  success: '#3FB950',
  successMuted: '#3FB95020',
  warning: '#D4A72C',
  warningMuted: '#D4A72C20',
  error: '#E5534B',
  errorMuted: '#E5534B20',
  unicorn: '#A371F7',
  unicornMuted: '#A371F720',
}

const nodeIcons: Record<NodeType, any> = {
  research: Search,
  batch: Layers,
  prediction: TrendingUp,
  analysis: BarChart3,
  chat: MessageSquare,
  startup: Building2,
}

const nodeColors: Record<NodeType, string> = {
  research: '#5E6AD2',
  batch: '#F0883E',
  prediction: '#A371F7',
  analysis: '#58A6FF',
  chat: '#3FB950',
  startup: '#8B8B8D',
}

// =============================================================================
// API
// =============================================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api-production-9cbf.up.railway.app'

const api = {
  // Startup Prediction API
  researchStartup: async (name: string, batch?: string) => {
    const res = await fetch(`${API_URL}/api/startups/research`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, batch })
    })
    return res.json()
  },

  predictStartup: async (startupId: string) => {
    const res = await fetch(`${API_URL}/api/startups/predict`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ startup_id: startupId })
    })
    return res.json()
  },

  analyzeYCBatch: async (batchCode: string, maxCompanies = 10) => {
    const res = await fetch(`${API_URL}/api/startups/yc/batch?batch_code=${batchCode}&max_companies=${maxCompanies}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    })
    return res.json()
  },

  chatAboutStartup: async (startupId: string, message: string, history: any[] = []) => {
    const res = await fetch(`${API_URL}/api/startups/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        startup_id: startupId,
        message,
        conversation_history: history
      })
    })
    return res.json()
  },

  getYCStats: async () => {
    const res = await fetch(`${API_URL}/api/startups/yc/stats`)
    return res.json()
  },

  // Legacy simulation API
  runSimulation: async (scenarioId: string, strategyId: string) => {
    const res = await fetch(`${API_URL}/simulations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenario_id: scenarioId,
        strategy_id: strategyId,
        num_agents: 5000,
        num_branches: 200,
      })
    })
    return res.json()
  },

  getSimulationStatus: async (simId: string) => {
    const res = await fetch(`${API_URL}/simulations/${simId}/status`)
    return res.json()
  },

  getResults: async (resultId: string) => {
    const res = await fetch(`${API_URL}/results/${resultId}`)
    return res.json()
  },
}

// =============================================================================
// COMPONENTS
// =============================================================================

function CanvasNode({
  node, selected, onSelect, onDrag, transform
}: {
  node: Node
  selected: boolean
  onSelect: (id: string) => void
  onDrag: (id: string, x: number, y: number) => void
  transform: { x: number; y: number; scale: number }
}) {
  const Icon = nodeIcons[node.type]
  const color = nodeColors[node.type]
  const [isDragging, setIsDragging] = useState(false)
  const [isHovered, setIsHovered] = useState(false)
  const dragStart = useRef({ x: 0, y: 0, nodeX: 0, nodeY: 0 })

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button !== 0) return
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
    dragStart.current = { x: e.clientX, y: e.clientY, nodeX: node.x, nodeY: node.y }
    onSelect(node.id)
  }

  useEffect(() => {
    if (!isDragging) return

    const handleMouseMove = (e: MouseEvent) => {
      const dx = (e.clientX - dragStart.current.x) / transform.scale
      const dy = (e.clientY - dragStart.current.y) / transform.scale
      onDrag(node.id, dragStart.current.nodeX + dx, dragStart.current.nodeY + dy)
    }

    const handleMouseUp = () => setIsDragging(false)

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging, node.id, onDrag, transform.scale])

  return (
    <motion.div
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      transition={{ duration: 0.15, ease: [0.16, 1, 0.3, 1] }}
      className="absolute cursor-grab active:cursor-grabbing select-none"
      style={{ left: node.x, top: node.y }}
      onMouseDown={handleMouseDown}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <motion.div
        animate={{
          y: isHovered && !isDragging ? -2 : 0,
          boxShadow: selected
            ? `0 0 0 1px ${color}, 0 8px 24px -8px rgba(0,0,0,0.5)`
            : isHovered
              ? '0 4px 16px -4px rgba(0,0,0,0.4)'
              : '0 2px 8px -2px rgba(0,0,0,0.3)'
        }}
        transition={{ duration: 0.15, ease: 'easeOut' }}
        className="w-[200px] rounded-lg overflow-hidden"
        style={{
          background: colors.bgElevated,
          border: `1px solid ${selected ? color : isHovered ? colors.borderHover : colors.border}`,
        }}
      >
        {/* Node header */}
        <div
          className="px-3 py-2.5 flex items-center gap-2.5"
          style={{ borderBottom: `1px solid ${colors.border}` }}
        >
          <div
            className="w-5 h-5 rounded flex items-center justify-center flex-shrink-0"
            style={{ background: `${color}15` }}
          >
            <Icon size={12} style={{ color }} strokeWidth={2} />
          </div>
          <span
            className="text-[10px] font-medium uppercase tracking-[0.5px]"
            style={{ color: colors.textMuted }}
          >
            {node.type}
          </span>
          <div className="ml-auto flex items-center">
            {node.status === 'running' && (
              <Loader2 className="w-3.5 h-3.5 animate-spin" style={{ color: colors.warning }} />
            )}
            {node.status === 'complete' && (
              <CheckCircle className="w-3.5 h-3.5" style={{ color: colors.success }} />
            )}
            {node.status === 'error' && (
              <AlertCircle className="w-3.5 h-3.5" style={{ color: colors.error }} />
            )}
          </div>
        </div>

        {/* Node content */}
        <div className="px-3 py-3">
          <h3
            className="text-[13px] font-medium leading-tight"
            style={{ color: colors.textPrimary }}
          >
            {node.title}
          </h3>
          {node.subtitle && (
            <p
              className="text-[11px] mt-1 leading-relaxed"
              style={{ color: colors.textSecondary }}
            >
              {node.subtitle}
            </p>
          )}
        </div>

        {/* Connection points */}
        <div
          className="absolute -left-[5px] top-1/2 -translate-y-1/2 w-[10px] h-[10px] rounded-full border-2 transition-colors duration-150"
          style={{
            background: colors.bg,
            borderColor: isHovered ? colors.borderHover : colors.border
          }}
        />
        <div
          className="absolute -right-[5px] top-1/2 -translate-y-1/2 w-[10px] h-[10px] rounded-full border-2 transition-colors duration-150"
          style={{
            background: colors.bg,
            borderColor: isHovered ? colors.borderHover : colors.border
          }}
        />
      </motion.div>
    </motion.div>
  )
}

function CanvasEdge({ from, to, animated }: { from: { x: number, y: number }, to: { x: number, y: number }, animated?: boolean }) {
  const fromX = from.x + 200
  const fromY = from.y + 40
  const toX = to.x
  const toY = to.y + 40
  const midX = (fromX + toX) / 2
  const path = `M ${fromX} ${fromY} C ${midX} ${fromY}, ${midX} ${toY}, ${toX} ${toY}`

  return (
    <g>
      <path
        d={path}
        fill="none"
        stroke={colors.border}
        strokeWidth="1.5"
        strokeOpacity={0.8}
      />
      {animated && (
        <path
          d={path}
          fill="none"
          stroke={colors.accent}
          strokeWidth="1.5"
          strokeDasharray="4,4"
          className="animate-dash"
        />
      )}
      <circle cx={toX} cy={toY} r="3" fill={animated ? colors.accent : colors.border} />
    </g>
  )
}

function PredictionCard({ prediction, onClick }: { prediction: StartupPrediction, onClick: () => void }) {
  const probPct = (prediction.unicorn_probability * 100).toFixed(1)
  const isHighProbability = prediction.unicorn_probability > 0.1
  const [isHovered, setIsHovered] = useState(false)

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
      className="group relative rounded-lg cursor-pointer overflow-hidden"
      style={{
        background: colors.bgTertiary,
        border: `1px solid ${isHovered ? colors.borderHover : colors.border}`,
      }}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <motion.div
        animate={{ y: isHovered ? -1 : 0 }}
        transition={{ duration: 0.15 }}
        className="p-3.5"
      >
        <div className="flex items-start justify-between gap-3">
          <div className="flex-1 min-w-0">
            <h3
              className="text-[13px] font-medium leading-tight truncate"
              style={{ color: colors.textPrimary }}
            >
              {prediction.startup_name}
            </h3>
            <p
              className="text-[11px] mt-0.5"
              style={{ color: colors.textSecondary }}
            >
              ${(prediction.expected_valuation / 1e6).toFixed(0)}M expected
            </p>
          </div>
          <div
            className="flex-shrink-0 px-2 py-1 rounded text-[10px] font-medium"
            style={{
              background: isHighProbability ? colors.unicornMuted : colors.warningMuted,
              color: isHighProbability ? colors.unicorn : colors.warning
            }}
          >
            {probPct}%
          </div>
        </div>

        <div className="mt-3 flex gap-1">
          {[
            { label: 'T', value: prediction.team_score, title: 'Team' },
            { label: 'M', value: prediction.market_score, title: 'Market' },
            { label: 'Tr', value: prediction.traction_score, title: 'Traction' },
            { label: 'Ti', value: prediction.timing_score, title: 'Timing' },
            { label: 'C', value: prediction.capital_score, title: 'Capital' },
          ].map(({ label, value, title }) => (
            <div key={label} className="flex-1" title={title}>
              <div
                className="h-1 rounded-full overflow-hidden"
                style={{ background: colors.border }}
              >
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${value * 100}%` }}
                  transition={{ duration: 0.5, delay: 0.1 }}
                  className="h-full rounded-full"
                  style={{ background: colors.accent }}
                />
              </div>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Hover indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: isHovered ? 1 : 0 }}
        className="absolute right-3 top-1/2 -translate-y-1/2"
      >
        <ChevronRight size={14} style={{ color: colors.textMuted }} />
      </motion.div>
    </motion.div>
  )
}

// Keyboard shortcut hint component
function KbdHint({ children }: { children: React.ReactNode }) {
  return (
    <kbd
      className="inline-flex items-center justify-center px-1.5 py-0.5 rounded text-[10px] font-medium"
      style={{
        background: colors.bgTertiary,
        color: colors.textMuted,
        border: `1px solid ${colors.border}`
      }}
    >
      {children}
    </kbd>
  )
}

// =============================================================================
// MAIN PAGE
// =============================================================================

export default function CanvasPage() {
  // Canvas state
  const [nodes, setNodes] = useState<Node[]>([
    { id: '1', type: 'batch', x: 100, y: 150, title: 'YC Batch Analysis', subtitle: 'Analyze accelerator batch', status: 'idle' },
    { id: '2', type: 'research', x: 400, y: 80, title: 'Deep Research', subtitle: 'Exa API + Claude', status: 'idle' },
    { id: '3', type: 'prediction', x: 400, y: 220, title: 'Unicorn Prediction', subtitle: 'Factor-based model', status: 'idle' },
    { id: '4', type: 'analysis', x: 700, y: 150, title: 'Portfolio Analysis', subtitle: 'Aggregate predictions', status: 'idle' },
    { id: '5', type: 'chat', x: 1000, y: 150, title: 'Interactive Chat', subtitle: 'Ask questions', status: 'idle' },
  ])

  const [edges] = useState<Edge[]>([
    { id: 'e1', from: '1', to: '2' },
    { id: 'e2', from: '1', to: '3' },
    { id: 'e3', from: '2', to: '4' },
    { id: 'e4', from: '3', to: '4' },
    { id: 'e5', from: '4', to: '5', animated: true },
  ])

  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 })
  const [isPanning, setIsPanning] = useState(false)
  const panStart = useRef({ x: 0, y: 0, transformX: 0, transformY: 0 })
  const canvasRef = useRef<HTMLDivElement>(null)

  // Research/Prediction state
  const [isResearching, setIsResearching] = useState(false)
  const [batchPrediction, setBatchPrediction] = useState<BatchPrediction | null>(null)
  const [selectedStartup, setSelectedStartup] = useState<StartupPrediction | null>(null)
  const [showResults, setShowResults] = useState(false)
  const [batchCode, setBatchCode] = useState('W21')

  // Chat state
  const [chatMessages, setChatMessages] = useState<Array<{ role: string, content: string }>>([])
  const [chatInput, setChatInput] = useState('')
  const [isChatting, setIsChatting] = useState(false)
  const [showChat, setShowChat] = useState(false)

  // Sidebar
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  // Track space key for pan mode
  const [spaceHeld, setSpaceHeld] = useState(false)

  // Space key detection for Figma-style space+drag panning
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space' && !e.repeat) {
        e.preventDefault()
        setSpaceHeld(true)
      }
    }
    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.code === 'Space') {
        setSpaceHeld(false)
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [])

  // Figma 2025 style: trackpad/scroll = pan naturally, pinch/ctrl+scroll = zoom
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault()

    // Pinch zoom or Cmd/Ctrl + scroll = zoom
    if (e.ctrlKey || e.metaKey) {
      const delta = e.deltaY > 0 ? 0.95 : 1.05
      const newScale = Math.min(Math.max(transform.scale * delta, 0.1), 3)
      const rect = canvasRef.current?.getBoundingClientRect()
      if (rect) {
        const x = e.clientX - rect.left
        const y = e.clientY - rect.top
        const newX = x - (x - transform.x) * (newScale / transform.scale)
        const newY = y - (y - transform.y) * (newScale / transform.scale)
        setTransform({ x: newX, y: newY, scale: newScale })
      }
    } else {
      // Natural pan - just use deltaX and deltaY directly
      // This works perfectly with trackpad two-finger scroll in any direction
      setTransform(prev => ({
        ...prev,
        x: prev.x - e.deltaX,
        y: prev.y - e.deltaY
      }))
    }
  }, [transform])

  const handleCanvasMouseDown = useCallback((e: React.MouseEvent) => {
    // Middle mouse, space+click, or alt+click = start panning
    if (e.button === 1 || (e.button === 0 && spaceHeld) || (e.button === 0 && e.altKey)) {
      e.preventDefault()
      setIsPanning(true)
      panStart.current = { x: e.clientX, y: e.clientY, transformX: transform.x, transformY: transform.y }
    } else if (e.button === 0 && e.target === e.currentTarget) {
      setSelectedNode(null)
    }
  }, [transform, spaceHeld])

  useEffect(() => {
    if (!isPanning) return
    const handleMouseMove = (e: MouseEvent) => {
      setTransform(prev => ({
        ...prev,
        x: panStart.current.transformX + (e.clientX - panStart.current.x),
        y: panStart.current.transformY + (e.clientY - panStart.current.y)
      }))
    }
    const handleMouseUp = () => setIsPanning(false)
    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isPanning])

  const handleDrag = useCallback((id: string, x: number, y: number) => {
    setNodes(prev => prev.map(n => n.id === id ? { ...n, x, y } : n))
  }, [])

  // Research YC Batch
  const runBatchAnalysis = async () => {
    setIsResearching(true)
    setShowResults(false)
    setBatchPrediction(null)

    setNodes(prev => prev.map(n =>
      ['1', '2', '3'].includes(n.id) ? { ...n, status: 'running' } : n
    ))

    try {
      const result = await api.analyzeYCBatch(batchCode, 8)

      setBatchPrediction(result)
      setShowResults(true)

      setNodes(prev => prev.map(n => {
        if (['1', '2', '3', '4'].includes(n.id)) return { ...n, status: 'complete' }
        return n
      }))

      // Update analysis node with results
      setNodes(prev => prev.map(n =>
        n.id === '4' ? { ...n, subtitle: `${result.expected_unicorns.toFixed(1)} expected unicorns` } : n
      ))

    } catch (error) {
      console.error('Batch analysis failed:', error)
      setNodes(prev => prev.map(n =>
        ['1', '2', '3'].includes(n.id) ? { ...n, status: 'error' } : n
      ))
    }

    setIsResearching(false)
  }

  // Chat
  const sendChatMessage = async () => {
    if (!chatInput.trim() || !selectedStartup) return

    const userMessage = chatInput.trim()
    setChatInput('')
    setChatMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsChatting(true)

    try {
      const response = await api.chatAboutStartup(selectedStartup.startup_id, userMessage, chatMessages)
      setChatMessages(prev => [...prev, { role: 'assistant', content: response.response }])
    } catch (error) {
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' }])
    }

    setIsChatting(false)
  }

  const openStartupChat = (prediction: StartupPrediction) => {
    setSelectedStartup(prediction)
    setChatMessages([])
    setShowChat(true)
    setNodes(prev => prev.map(n => n.id === '5' ? { ...n, status: 'complete' } : n))
  }

  return (
    <div
      className="h-screen w-screen overflow-hidden flex antialiased"
      style={{
        background: colors.bg,
        fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
      }}
    >
      {/* Sidebar - Linear style */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarCollapsed ? 48 : 200 }}
        transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
        className="h-full flex flex-col z-20 flex-shrink-0"
        style={{
          background: colors.bgSecondary,
          borderRight: `1px solid ${colors.border}`
        }}
      >
        {/* Logo */}
        <div
          className="h-11 flex items-center px-3 gap-2.5"
          style={{ borderBottom: `1px solid ${colors.border}` }}
        >
          <div
            className="w-6 h-6 rounded flex items-center justify-center flex-shrink-0"
            style={{
              background: `linear-gradient(135deg, ${colors.accent} 0%, #7C3AED 100%)`,
              boxShadow: '0 2px 4px rgba(94, 106, 210, 0.3)'
            }}
          >
            <Zap size={13} className="text-white" strokeWidth={2.5} />
          </div>
          {!sidebarCollapsed && (
            <span
              className="text-[13px] font-semibold tracking-[-0.01em]"
              style={{ color: colors.textPrimary }}
            >
              Populous
            </span>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-2 px-2 space-y-0.5">
          <Link
            href="/projects"
            className="flex items-center gap-2.5 px-2 py-1.5 rounded-md transition-colors duration-150 group"
            style={{ color: colors.textSecondary }}
            onMouseEnter={(e) => e.currentTarget.style.background = colors.bgTertiary}
            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
          >
            <FolderOpen size={15} strokeWidth={1.75} />
            {!sidebarCollapsed && (
              <span className="text-[13px] font-medium">Projects</span>
            )}
          </Link>
          <Link
            href="/audiences"
            className="flex items-center gap-2.5 px-2 py-1.5 rounded-md transition-colors duration-150 group"
            style={{ color: colors.textSecondary }}
            onMouseEnter={(e) => e.currentTarget.style.background = colors.bgTertiary}
            onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
          >
            <Users size={15} strokeWidth={1.75} />
            {!sidebarCollapsed && (
              <span className="text-[13px] font-medium">Audiences</span>
            )}
          </Link>

          {!sidebarCollapsed && (
            <>
              <div
                className="h-px my-3 mx-1"
                style={{ background: colors.border }}
              />

              <div className="px-2 mb-2">
                <span
                  className="text-[10px] font-medium uppercase tracking-[0.5px]"
                  style={{ color: colors.textMuted }}
                >
                  YC Batch
                </span>
              </div>
              <div className="px-1">
                <select
                  value={batchCode}
                  onChange={(e) => setBatchCode(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded-md text-[13px] font-medium appearance-none cursor-pointer transition-colors duration-150 focus:outline-none focus:ring-1"
                  style={{
                    background: colors.bgTertiary,
                    color: colors.textPrimary,
                    border: `1px solid ${colors.border}`,
                  }}
                >
                  <option value="W24">W24 (Winter 2024)</option>
                  <option value="S23">S23 (Summer 2023)</option>
                  <option value="W23">W23 (Winter 2023)</option>
                  <option value="S22">S22 (Summer 2022)</option>
                  <option value="W22">W22 (Winter 2022)</option>
                  <option value="S21">S21 (Summer 2021)</option>
                  <option value="W21">W21 (Winter 2021)</option>
                  <option value="S20">S20 (Summer 2020)</option>
                </select>
              </div>
            </>
          )}
        </nav>

        {/* Collapse toggle */}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="h-9 flex items-center justify-center transition-colors duration-150"
          style={{ borderTop: `1px solid ${colors.border}` }}
          onMouseEnter={(e) => e.currentTarget.style.background = colors.bgTertiary}
          onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
        >
          <ChevronRight
            size={14}
            style={{
              color: colors.textMuted,
              transform: sidebarCollapsed ? 'rotate(0deg)' : 'rotate(180deg)',
              transition: 'transform 0.2s ease'
            }}
          />
        </button>
      </motion.aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header - Minimal Linear style */}
        <header
          className="h-11 flex items-center justify-between px-4 z-10 flex-shrink-0"
          style={{
            background: colors.bgSecondary,
            borderBottom: `1px solid ${colors.border}`
          }}
        >
          <div className="flex items-center gap-3">
            <h1
              className="text-[13px] font-medium"
              style={{ color: colors.textPrimary }}
            >
              Unicorn Prediction Engine
            </h1>
            <span
              className="text-[11px] px-1.5 py-0.5 rounded font-medium tabular-nums"
              style={{
                background: colors.bgTertiary,
                color: colors.textMuted
              }}
            >
              {Math.round(transform.scale * 100)}%
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            {/* Zoom controls */}
            <div className="flex items-center">
              <button
                onClick={() => setTransform({ x: 0, y: 0, scale: 1 })}
                className="p-1.5 rounded transition-colors duration-150"
                title="Reset view (R)"
                style={{ color: colors.textMuted }}
                onMouseEnter={(e) => e.currentTarget.style.background = colors.bgTertiary}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <RotateCcw size={14} strokeWidth={1.75} />
              </button>
              <button
                onClick={() => setTransform(prev => ({ ...prev, scale: Math.max(0.25, prev.scale - 0.1) }))}
                className="p-1.5 rounded transition-colors duration-150"
                style={{ color: colors.textMuted }}
                onMouseEnter={(e) => e.currentTarget.style.background = colors.bgTertiary}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <Minus size={14} strokeWidth={1.75} />
              </button>
              <button
                onClick={() => setTransform(prev => ({ ...prev, scale: Math.min(2, prev.scale + 0.1) }))}
                className="p-1.5 rounded transition-colors duration-150"
                style={{ color: colors.textMuted }}
                onMouseEnter={(e) => e.currentTarget.style.background = colors.bgTertiary}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <Plus size={14} strokeWidth={1.75} />
              </button>
            </div>

            <div className="w-px h-5 mx-1" style={{ background: colors.border }} />

            {/* Run button - Linear style */}
            <motion.button
              onClick={runBatchAnalysis}
              disabled={isResearching}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="px-3 py-1.5 rounded-md text-[12px] font-medium flex items-center gap-2 disabled:opacity-50 transition-all duration-150"
              style={{
                background: `linear-gradient(180deg, ${colors.accent} 0%, #4F5BC7 100%)`,
                color: 'white',
                boxShadow: '0 1px 2px rgba(0,0,0,0.2), inset 0 1px 0 rgba(255,255,255,0.1)'
              }}
            >
              {isResearching ? (
                <>
                  <Loader2 size={13} className="animate-spin" strokeWidth={2} />
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <Search size={13} strokeWidth={2} />
                  <span>Analyze {batchCode}</span>
                </>
              )}
            </motion.button>
          </div>
        </header>

        {/* Canvas */}
        <div
          ref={canvasRef}
          className="flex-1 relative overflow-hidden"
          style={{
            cursor: isPanning ? 'grabbing' : spaceHeld ? 'grab' : 'default',
            backgroundImage: `radial-gradient(${colors.border} 1px, transparent 1px)`,
            backgroundSize: `${20 * transform.scale}px ${20 * transform.scale}px`,
            backgroundPosition: `${transform.x}px ${transform.y}px`,
          }}
          onWheel={handleWheel}
          onMouseDown={handleCanvasMouseDown}
        >
          <div style={{ transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})`, transformOrigin: '0 0' }}>
            <svg className="absolute inset-0 pointer-events-none" style={{ width: '5000px', height: '5000px', overflow: 'visible' }}>
              {edges.map(edge => {
                const fromNode = nodes.find(n => n.id === edge.from)
                const toNode = nodes.find(n => n.id === edge.to)
                if (!fromNode || !toNode) return null
                return <CanvasEdge key={edge.id} from={{ x: fromNode.x, y: fromNode.y }} to={{ x: toNode.x, y: toNode.y }} animated={edge.animated} />
              })}
            </svg>

            {nodes.map(node => (
              <CanvasNode key={node.id} node={node} selected={selectedNode === node.id} onSelect={setSelectedNode} onDrag={handleDrag} transform={transform} />
            ))}
          </div>

          {/* Canvas controls hint */}
          <div
            className="absolute bottom-4 left-4 px-3 py-2 rounded-lg flex items-center gap-3"
            style={{
              background: `${colors.bgSecondary}E6`,
              border: `1px solid ${colors.border}`,
              backdropFilter: 'blur(8px)'
            }}
          >
            <div className="flex items-center gap-1.5">
              <span className="text-[11px]" style={{ color: colors.textMuted }}>Scroll to pan</span>
            </div>
            <div className="w-px h-3" style={{ background: colors.border }} />
            <div className="flex items-center gap-1.5">
              <KbdHint><Command size={9} /></KbdHint>
              <span className="text-[11px]" style={{ color: colors.textMuted }}>+ scroll to zoom</span>
            </div>
          </div>
        </div>
      </div>

      {/* Results Panel - Linear style */}
      <AnimatePresence>
        {showResults && batchPrediction && (
          <motion.div
            initial={{ x: 380, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 380, opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="w-[380px] flex flex-col z-20 flex-shrink-0"
            style={{
              background: colors.bgSecondary,
              borderLeft: `1px solid ${colors.border}`
            }}
          >
            {/* Panel header */}
            <div
              className="h-11 flex items-center justify-between px-4 flex-shrink-0"
              style={{ borderBottom: `1px solid ${colors.border}` }}
            >
              <h2
                className="text-[13px] font-medium"
                style={{ color: colors.textPrimary }}
              >
                {batchPrediction.batch_name}
              </h2>
              <button
                onClick={() => setShowResults(false)}
                className="p-1 rounded transition-colors duration-150"
                style={{ color: colors.textMuted }}
                onMouseEnter={(e) => e.currentTarget.style.background = colors.bgTertiary}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <X size={14} strokeWidth={1.75} />
              </button>
            </div>

            {/* Panel content */}
            <div className="flex-1 overflow-auto">
              <div className="p-4 space-y-4">
                {/* Summary Stats */}
                <div className="grid grid-cols-2 gap-3">
                  <div
                    className="p-3 rounded-lg"
                    style={{
                      background: colors.bgTertiary,
                      border: `1px solid ${colors.border}`
                    }}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <div
                        className="w-5 h-5 rounded flex items-center justify-center"
                        style={{ background: colors.unicornMuted }}
                      >
                        <Award size={11} style={{ color: colors.unicorn }} />
                      </div>
                      <span
                        className="text-[10px] font-medium uppercase tracking-[0.5px]"
                        style={{ color: colors.textMuted }}
                      >
                        Unicorns
                      </span>
                    </div>
                    <p
                      className="text-xl font-semibold tracking-tight"
                      style={{ color: colors.unicorn }}
                    >
                      {batchPrediction.expected_unicorns.toFixed(1)}
                    </p>
                    <p
                      className="text-[10px] mt-0.5"
                      style={{ color: colors.textMuted }}
                    >
                      Range: {batchPrediction.unicorn_range[0]}-{batchPrediction.unicorn_range[1]}
                    </p>
                  </div>

                  <div
                    className="p-3 rounded-lg"
                    style={{
                      background: colors.bgTertiary,
                      border: `1px solid ${colors.border}`
                    }}
                  >
                    <div className="flex items-center gap-2 mb-2">
                      <div
                        className="w-5 h-5 rounded flex items-center justify-center"
                        style={{ background: colors.successMuted }}
                      >
                        <DollarSign size={11} style={{ color: colors.success }} />
                      </div>
                      <span
                        className="text-[10px] font-medium uppercase tracking-[0.5px]"
                        style={{ color: colors.textMuted }}
                      >
                        Value
                      </span>
                    </div>
                    <p
                      className="text-xl font-semibold tracking-tight"
                      style={{ color: colors.success }}
                    >
                      ${batchPrediction.expected_total_value.toFixed(1)}B
                    </p>
                    <p
                      className="text-[10px] mt-0.5"
                      style={{ color: colors.textMuted }}
                    >
                      {batchPrediction.batch_size} companies
                    </p>
                  </div>
                </div>

                {/* Batch Quality */}
                <div
                  className="p-3 rounded-lg"
                  style={{
                    background: colors.bgTertiary,
                    border: `1px solid ${colors.border}`
                  }}
                >
                  <div className="flex justify-between items-center mb-2">
                    <span
                      className="text-[10px] font-medium uppercase tracking-[0.5px]"
                      style={{ color: colors.textMuted }}
                    >
                      Batch Quality
                    </span>
                    <span
                      className="text-[12px] font-semibold tabular-nums"
                      style={{ color: colors.textPrimary }}
                    >
                      {(batchPrediction.batch_quality_score * 100).toFixed(0)}%
                    </span>
                  </div>
                  <div
                    className="h-1.5 rounded-full overflow-hidden"
                    style={{ background: colors.border }}
                  >
                    <motion.div
                      initial={{ width: 0 }}
                      animate={{ width: `${batchPrediction.batch_quality_score * 100}%` }}
                      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                      className="h-full rounded-full"
                      style={{ background: `linear-gradient(90deg, ${colors.accent} 0%, ${colors.unicorn} 100%)` }}
                    />
                  </div>
                </div>

                {/* Top Candidates */}
                <div>
                  <h3
                    className="text-[10px] font-medium uppercase tracking-[0.5px] mb-3 px-0.5"
                    style={{ color: colors.textMuted }}
                  >
                    Top Unicorn Candidates
                  </h3>
                  <div className="space-y-2">
                    {batchPrediction.startups.slice(0, 5).map((p) => (
                      <PredictionCard key={p.startup_id} prediction={p} onClick={() => openStartupChat(p)} />
                    ))}
                  </div>
                </div>

                {/* Methodology Note */}
                <div
                  className="p-3 rounded-lg"
                  style={{
                    background: colors.accentSubtle,
                    border: `1px solid ${colors.accent}30`
                  }}
                >
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles size={12} style={{ color: colors.accent }} />
                    <span
                      className="text-[10px] font-medium uppercase tracking-[0.5px]"
                      style={{ color: colors.accent }}
                    >
                      Methodology
                    </span>
                  </div>
                  <p
                    className="text-[11px] leading-relaxed"
                    style={{ color: colors.textSecondary }}
                  >
                    Predictions use a factor-based model calibrated on YC's historical 1.6% unicorn rate (82 unicorns from ~5,000 companies).
                    Factors: Team (30%), Market (25%), Traction (20%), Timing (15%), Capital (10%).
                  </p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Panel - Linear style */}
      <AnimatePresence>
        {showChat && selectedStartup && (
          <motion.div
            initial={{ y: '100%', opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: '100%', opacity: 0 }}
            transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
            className="fixed bottom-0 right-4 w-[380px] h-[480px] rounded-t-xl flex flex-col z-30 overflow-hidden"
            style={{
              background: colors.bgSecondary,
              border: `1px solid ${colors.border}`,
              borderBottom: 'none',
              boxShadow: '0 -8px 32px rgba(0,0,0,0.4)'
            }}
          >
            {/* Chat header */}
            <div
              className="h-11 flex items-center justify-between px-4 flex-shrink-0"
              style={{ borderBottom: `1px solid ${colors.border}` }}
            >
              <div className="flex items-center gap-2.5">
                <div
                  className="w-5 h-5 rounded flex items-center justify-center"
                  style={{ background: colors.successMuted }}
                >
                  <MessageSquare size={11} style={{ color: colors.success }} />
                </div>
                <span
                  className="text-[13px] font-medium"
                  style={{ color: colors.textPrimary }}
                >
                  {selectedStartup.startup_name}
                </span>
              </div>
              <button
                onClick={() => setShowChat(false)}
                className="p-1 rounded transition-colors duration-150"
                style={{ color: colors.textMuted }}
                onMouseEnter={(e) => e.currentTarget.style.background = colors.bgTertiary}
                onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
              >
                <X size={14} strokeWidth={1.75} />
              </button>
            </div>

            {/* Chat messages */}
            <div className="flex-1 overflow-auto p-4 space-y-3">
              {chatMessages.length === 0 && (
                <div className="text-center py-12">
                  <div
                    className="w-10 h-10 rounded-lg flex items-center justify-center mx-auto mb-3"
                    style={{ background: colors.bgTertiary }}
                  >
                    <MessageSquare size={18} style={{ color: colors.textMuted }} />
                  </div>
                  <p
                    className="text-[13px] font-medium"
                    style={{ color: colors.textSecondary }}
                  >
                    Ask about {selectedStartup.startup_name}
                  </p>
                  <p
                    className="text-[11px] mt-1.5 leading-relaxed max-w-[240px] mx-auto"
                    style={{ color: colors.textMuted }}
                  >
                    Try: "Why is the team score low?" or "Compare to average YC company"
                  </p>
                </div>
              )}

              {chatMessages.map((msg, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className="max-w-[85%] px-3 py-2 rounded-lg text-[13px] leading-relaxed"
                    style={{
                      background: msg.role === 'user' ? colors.accent : colors.bgTertiary,
                      color: colors.textPrimary,
                    }}
                  >
                    {msg.content}
                  </div>
                </motion.div>
              ))}

              {isChatting && (
                <div className="flex justify-start">
                  <div
                    className="px-3 py-2 rounded-lg"
                    style={{ background: colors.bgTertiary }}
                  >
                    <Loader2
                      size={14}
                      className="animate-spin"
                      style={{ color: colors.textMuted }}
                    />
                  </div>
                </div>
              )}
            </div>

            {/* Chat input */}
            <div
              className="p-3 flex-shrink-0"
              style={{ borderTop: `1px solid ${colors.border}` }}
            >
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendChatMessage()}
                  placeholder="Ask a question..."
                  className="flex-1 px-3 py-2 rounded-md text-[13px] transition-colors duration-150 focus:outline-none"
                  style={{
                    background: colors.bgTertiary,
                    color: colors.textPrimary,
                    border: `1px solid ${colors.border}`,
                  }}
                />
                <motion.button
                  onClick={sendChatMessage}
                  disabled={isChatting || !chatInput.trim()}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className="px-3 py-2 rounded-md disabled:opacity-40 transition-opacity duration-150"
                  style={{
                    background: colors.accent,
                    boxShadow: '0 1px 2px rgba(0,0,0,0.2)'
                  }}
                >
                  <Send size={14} className="text-white" strokeWidth={2} />
                </motion.button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Tagline - Linear style */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5, duration: 0.3 }}
        className="fixed bottom-4 left-1/2 -translate-x-1/2 px-4 py-2 rounded-full text-[11px] z-10"
        style={{
          background: `${colors.bgSecondary}E6`,
          color: colors.textMuted,
          border: `1px solid ${colors.border}`,
          backdropFilter: 'blur(8px)'
        }}
      >
        There's a future where you win; we engineer that for you.
      </motion.div>

      <style jsx global>{`
        @keyframes dash { to { stroke-dashoffset: -8; } }
        .animate-dash { animation: dash 0.4s linear infinite; }

        /* Custom scrollbar - Linear style */
        ::-webkit-scrollbar {
          width: 6px;
          height: 6px;
        }
        ::-webkit-scrollbar-track {
          background: transparent;
        }
        ::-webkit-scrollbar-thumb {
          background: ${colors.border};
          border-radius: 3px;
        }
        ::-webkit-scrollbar-thumb:hover {
          background: ${colors.borderHover};
        }

        /* Selection color */
        ::selection {
          background: ${colors.accentMuted};
          color: ${colors.textPrimary};
        }

        /* Focus styles */
        input:focus {
          border-color: ${colors.accent} !important;
          box-shadow: 0 0 0 1px ${colors.accent}40;
        }

        select:focus {
          border-color: ${colors.accent} !important;
          box-shadow: 0 0 0 1px ${colors.accent}40;
        }
      `}</style>
    </div>
  )
}
