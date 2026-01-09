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
  MessageSquare, ChevronDown, ExternalLink
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
// DESIGN SYSTEM
// =============================================================================

const colors = {
  bg: '#0D0D0F',
  bgSecondary: '#131316',
  bgTertiary: '#1A1A1F',
  accent: '#5E6AD2',
  accentHover: '#6E7AE2',
  textPrimary: '#FFFFFF',
  textSecondary: '#8A8F98',
  textMuted: '#5C5F66',
  border: '#26262C',
  success: '#3FB950',
  warning: '#D29922',
  error: '#F85149',
  unicorn: '#A371F7',
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
  chat: '#39D353',
  startup: '#8B949E',
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
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="absolute cursor-grab active:cursor-grabbing select-none"
      style={{ left: node.x, top: node.y }}
      onMouseDown={handleMouseDown}
    >
      <div
        className="w-[220px] rounded-lg border transition-all duration-200"
        style={{
          background: colors.bgSecondary,
          borderColor: selected ? color : colors.border,
          boxShadow: selected ? `0 0 0 2px ${colors.bg}, 0 0 0 4px ${color}` : 'none',
        }}
      >
        <div className="px-3 py-2 border-b flex items-center gap-2" style={{ borderColor: colors.border }}>
          <div className="w-6 h-6 rounded flex items-center justify-center" style={{ background: `${color}20` }}>
            <Icon size={14} style={{ color }} />
          </div>
          <span className="text-xs font-medium uppercase tracking-wider" style={{ color: colors.textMuted }}>
            {node.type}
          </span>
          {node.status === 'running' && <Loader2 className="ml-auto w-4 h-4 animate-spin text-yellow-500" />}
          {node.status === 'complete' && <CheckCircle className="ml-auto w-4 h-4 text-green-500" />}
          {node.status === 'error' && <AlertCircle className="ml-auto w-4 h-4 text-red-500" />}
        </div>

        <div className="px-3 py-3">
          <h3 className="text-sm font-medium" style={{ color: colors.textPrimary }}>{node.title}</h3>
          {node.subtitle && <p className="text-xs mt-1" style={{ color: colors.textSecondary }}>{node.subtitle}</p>}
        </div>

        <div className="absolute -left-1.5 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2" style={{ background: colors.bg, borderColor: colors.border }} />
        <div className="absolute -right-1.5 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2" style={{ background: colors.bg, borderColor: colors.border }} />
      </div>
    </motion.div>
  )
}

function CanvasEdge({ from, to, animated }: { from: { x: number, y: number }, to: { x: number, y: number }, animated?: boolean }) {
  const fromX = from.x + 220
  const fromY = from.y + 40
  const toX = to.x
  const toY = to.y + 40
  const midX = (fromX + toX) / 2
  const path = `M ${fromX} ${fromY} C ${midX} ${fromY}, ${midX} ${toY}, ${toX} ${toY}`

  return (
    <g>
      <path d={path} fill="none" stroke={colors.accent} strokeWidth="2" strokeOpacity={animated ? 1 : 0.5}
        strokeDasharray={animated ? "5,5" : "0"} className={animated ? "animate-dash" : ""} />
      <circle cx={toX} cy={toY} r="4" fill={colors.accent} />
    </g>
  )
}

function PredictionCard({ prediction, onClick }: { prediction: StartupPrediction, onClick: () => void }) {
  const probPct = (prediction.unicorn_probability * 100).toFixed(1)
  const isHighProbability = prediction.unicorn_probability > 0.1

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="p-4 rounded-lg border cursor-pointer hover:border-[#5E6AD2] transition-all"
      style={{ background: colors.bgTertiary, borderColor: colors.border }}
      onClick={onClick}
    >
      <div className="flex items-start justify-between">
        <div>
          <h3 className="text-sm font-medium text-white">{prediction.startup_name}</h3>
          <p className="text-xs mt-1" style={{ color: colors.textSecondary }}>
            Expected: ${(prediction.expected_valuation / 1e6).toFixed(0)}M
          </p>
        </div>
        <div
          className="px-2 py-1 rounded text-xs font-medium"
          style={{
            background: isHighProbability ? `${colors.unicorn}20` : `${colors.warning}20`,
            color: isHighProbability ? colors.unicorn : colors.warning
          }}
        >
          {probPct}% unicorn
        </div>
      </div>

      <div className="mt-3 grid grid-cols-5 gap-1">
        {[
          { label: 'Team', value: prediction.team_score },
          { label: 'Market', value: prediction.market_score },
          { label: 'Traction', value: prediction.traction_score },
          { label: 'Timing', value: prediction.timing_score },
          { label: 'Capital', value: prediction.capital_score },
        ].map(({ label, value }) => (
          <div key={label} className="text-center">
            <div className="h-1.5 rounded-full overflow-hidden" style={{ background: colors.border }}>
              <div className="h-full rounded-full" style={{ width: `${value * 100}%`, background: colors.accent }} />
            </div>
            <span className="text-[10px]" style={{ color: colors.textMuted }}>{label}</span>
          </div>
        ))}
      </div>
    </motion.div>
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

  // Pan/Zoom handlers
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? 0.9 : 1.1
    const newScale = Math.min(Math.max(transform.scale * delta, 0.25), 2)
    const rect = canvasRef.current?.getBoundingClientRect()
    if (rect) {
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      const newX = x - (x - transform.x) * (newScale / transform.scale)
      const newY = y - (y - transform.y) * (newScale / transform.scale)
      setTransform({ x: newX, y: newY, scale: newScale })
    }
  }, [transform])

  const handleCanvasMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 1 || (e.button === 0 && e.altKey)) {
      e.preventDefault()
      setIsPanning(true)
      panStart.current = { x: e.clientX, y: e.clientY, transformX: transform.x, transformY: transform.y }
    } else if (e.button === 0 && e.target === e.currentTarget) {
      setSelectedNode(null)
    }
  }, [transform])

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
    <div className="h-screen w-screen overflow-hidden flex" style={{ background: colors.bg }}>
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarCollapsed ? 56 : 220 }}
        className="h-full border-r flex flex-col z-20"
        style={{ background: colors.bgSecondary, borderColor: colors.border }}
      >
        <div className="h-12 border-b flex items-center px-3 gap-2" style={{ borderColor: colors.border }}>
          <div className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0" style={{ background: colors.accent }}>
            <Zap size={16} className="text-white" />
          </div>
          {!sidebarCollapsed && <span className="font-semibold text-white text-sm">Populous Demo</span>}
        </div>

        <nav className="flex-1 p-2 space-y-1">
          <Link href="/projects" className="flex items-center gap-2 px-2 py-2 rounded-md hover:bg-[#26262C] transition-colors">
            <FolderOpen size={18} style={{ color: colors.textSecondary }} />
            {!sidebarCollapsed && <span className="text-sm" style={{ color: colors.textSecondary }}>Projects</span>}
          </Link>
          <Link href="/audiences" className="flex items-center gap-2 px-2 py-2 rounded-md hover:bg-[#26262C] transition-colors">
            <Users size={18} style={{ color: colors.textSecondary }} />
            {!sidebarCollapsed && <span className="text-sm" style={{ color: colors.textSecondary }}>Audiences</span>}
          </Link>

          <div className="h-px my-2" style={{ background: colors.border }} />

          {!sidebarCollapsed && (
            <>
              <span className="text-xs px-2 py-1 block" style={{ color: colors.textMuted }}>YC Batch</span>
              <select
                value={batchCode}
                onChange={(e) => setBatchCode(e.target.value)}
                className="w-full px-2 py-2 rounded-md text-sm"
                style={{ background: colors.bgTertiary, color: colors.textPrimary, border: `1px solid ${colors.border}` }}
              >
                <option value="W24">YC W24 (Winter 2024)</option>
                <option value="S23">YC S23 (Summer 2023)</option>
                <option value="W23">YC W23 (Winter 2023)</option>
                <option value="S22">YC S22 (Summer 2022)</option>
                <option value="W22">YC W22 (Winter 2022)</option>
                <option value="S21">YC S21 (Summer 2021)</option>
                <option value="W21">YC W21 (Winter 2021)</option>
                <option value="S20">YC S20 (Summer 2020)</option>
              </select>
            </>
          )}
        </nav>

        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="h-10 border-t flex items-center justify-center hover:bg-[#26262C] transition-colors"
          style={{ borderColor: colors.border }}
        >
          <ChevronRight size={16} style={{ color: colors.textMuted, transform: sidebarCollapsed ? 'rotate(0)' : 'rotate(180deg)' }} />
        </button>
      </motion.aside>

      {/* Main */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-12 border-b flex items-center justify-between px-4 z-10" style={{ background: colors.bgSecondary, borderColor: colors.border }}>
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-white">Unicorn Prediction Engine</span>
            <span className="text-xs px-2 py-0.5 rounded" style={{ background: colors.bgTertiary, color: colors.textMuted }}>
              {Math.round(transform.scale * 100)}%
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button onClick={() => setTransform({ x: 0, y: 0, scale: 1 })} className="p-2 rounded-md hover:bg-[#26262C]" title="Reset view">
              <RotateCcw size={16} style={{ color: colors.textSecondary }} />
            </button>
            <button onClick={() => setTransform(prev => ({ ...prev, scale: Math.max(0.25, prev.scale - 0.1) }))} className="p-2 rounded-md hover:bg-[#26262C]">
              <Minus size={16} style={{ color: colors.textSecondary }} />
            </button>
            <button onClick={() => setTransform(prev => ({ ...prev, scale: Math.min(2, prev.scale + 0.1) }))} className="p-2 rounded-md hover:bg-[#26262C]">
              <Plus size={16} style={{ color: colors.textSecondary }} />
            </button>

            <div className="w-px h-6 mx-2" style={{ background: colors.border }} />

            <button
              onClick={runBatchAnalysis}
              disabled={isResearching}
              className="px-4 py-1.5 rounded-md text-sm font-medium flex items-center gap-2 disabled:opacity-50"
              style={{ background: colors.accent, color: 'white' }}
            >
              {isResearching ? (
                <><Loader2 size={14} className="animate-spin" /> Researching...</>
              ) : (
                <><Search size={14} /> Analyze YC {batchCode}</>
              )}
            </button>
          </div>
        </header>

        {/* Canvas */}
        <div
          ref={canvasRef}
          className="flex-1 relative overflow-hidden"
          style={{
            cursor: isPanning ? 'grabbing' : 'default',
            backgroundImage: `radial-gradient(${colors.border} 1px, transparent 1px)`,
            backgroundSize: `${24 * transform.scale}px ${24 * transform.scale}px`,
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

          <div className="absolute bottom-4 left-4 px-3 py-2 rounded-lg text-xs" style={{ background: colors.bgSecondary, color: colors.textMuted, border: `1px solid ${colors.border}` }}>
            Scroll to zoom | Alt+drag to pan | Click "Analyze" to research YC batch
          </div>
        </div>
      </div>

      {/* Results Panel */}
      <AnimatePresence>
        {showResults && batchPrediction && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            className="w-[400px] border-l flex flex-col z-20"
            style={{ background: colors.bgSecondary, borderColor: colors.border }}
          >
            <div className="h-12 border-b flex items-center justify-between px-4" style={{ borderColor: colors.border }}>
              <h2 className="text-sm font-medium text-white">{batchPrediction.batch_name} Analysis</h2>
              <button onClick={() => setShowResults(false)} className="p-1 hover:bg-[#26262C] rounded">
                <X size={16} style={{ color: colors.textMuted }} />
              </button>
            </div>

            <div className="flex-1 overflow-auto p-4 space-y-4">
              {/* Summary Stats */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg" style={{ background: colors.bgTertiary }}>
                  <div className="flex items-center gap-2">
                    <Award size={16} style={{ color: colors.unicorn }} />
                    <span className="text-xs" style={{ color: colors.textMuted }}>Expected Unicorns</span>
                  </div>
                  <p className="text-xl font-bold mt-1" style={{ color: colors.unicorn }}>
                    {batchPrediction.expected_unicorns.toFixed(1)}
                  </p>
                  <p className="text-xs" style={{ color: colors.textMuted }}>
                    Range: {batchPrediction.unicorn_range[0]}-{batchPrediction.unicorn_range[1]}
                  </p>
                </div>

                <div className="p-3 rounded-lg" style={{ background: colors.bgTertiary }}>
                  <div className="flex items-center gap-2">
                    <DollarSign size={16} style={{ color: colors.success }} />
                    <span className="text-xs" style={{ color: colors.textMuted }}>Expected Value</span>
                  </div>
                  <p className="text-xl font-bold mt-1" style={{ color: colors.success }}>
                    ${batchPrediction.expected_total_value.toFixed(1)}B
                  </p>
                  <p className="text-xs" style={{ color: colors.textMuted }}>
                    {batchPrediction.batch_size} companies
                  </p>
                </div>
              </div>

              {/* Batch Quality */}
              <div className="p-3 rounded-lg" style={{ background: colors.bgTertiary }}>
                <div className="flex justify-between items-center mb-2">
                  <span className="text-xs font-medium" style={{ color: colors.textMuted }}>BATCH QUALITY</span>
                  <span className="text-sm font-medium text-white">
                    {(batchPrediction.batch_quality_score * 100).toFixed(0)}%
                  </span>
                </div>
                <div className="h-2 rounded-full overflow-hidden" style={{ background: colors.border }}>
                  <div
                    className="h-full rounded-full"
                    style={{ width: `${batchPrediction.batch_quality_score * 100}%`, background: colors.accent }}
                  />
                </div>
              </div>

              {/* Top Candidates */}
              <div>
                <h3 className="text-xs font-medium mb-2" style={{ color: colors.textMuted }}>TOP UNICORN CANDIDATES</h3>
                <div className="space-y-2">
                  {batchPrediction.startups.slice(0, 5).map((p, i) => (
                    <PredictionCard key={p.startup_id} prediction={p} onClick={() => openStartupChat(p)} />
                  ))}
                </div>
              </div>

              {/* Methodology Note */}
              <div className="p-3 rounded-lg border" style={{ background: `${colors.accent}10`, borderColor: colors.accent }}>
                <div className="flex items-center gap-2 mb-2">
                  <Sparkles size={14} style={{ color: colors.accent }} />
                  <span className="text-xs font-medium" style={{ color: colors.accent }}>Methodology</span>
                </div>
                <p className="text-xs" style={{ color: colors.textSecondary }}>
                  Predictions use a factor-based model calibrated on YC's historical 1.6% unicorn rate (82 unicorns from ~5,000 companies).
                  Factors: Team (30%), Market (25%), Traction (20%), Timing (15%), Capital (10%).
                </p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Panel */}
      <AnimatePresence>
        {showChat && selectedStartup && (
          <motion.div
            initial={{ y: '100%' }}
            animate={{ y: 0 }}
            exit={{ y: '100%' }}
            className="fixed bottom-0 right-4 w-[400px] h-[500px] rounded-t-xl border border-b-0 flex flex-col z-30"
            style={{ background: colors.bgSecondary, borderColor: colors.border }}
          >
            <div className="h-12 border-b flex items-center justify-between px-4" style={{ borderColor: colors.border }}>
              <div className="flex items-center gap-2">
                <MessageSquare size={16} style={{ color: colors.success }} />
                <span className="text-sm font-medium text-white">{selectedStartup.startup_name}</span>
              </div>
              <button onClick={() => setShowChat(false)} className="p-1 hover:bg-[#26262C] rounded">
                <X size={16} style={{ color: colors.textMuted }} />
              </button>
            </div>

            <div className="flex-1 overflow-auto p-4 space-y-3">
              {chatMessages.length === 0 && (
                <div className="text-center py-8">
                  <MessageSquare size={32} style={{ color: colors.textMuted }} className="mx-auto mb-2 opacity-50" />
                  <p className="text-sm" style={{ color: colors.textMuted }}>
                    Ask questions about {selectedStartup.startup_name}'s prediction
                  </p>
                  <p className="text-xs mt-2" style={{ color: colors.textMuted }}>
                    Try: "Why is the team score low?" or "Compare to average YC company"
                  </p>
                </div>
              )}

              {chatMessages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className="max-w-[80%] px-3 py-2 rounded-lg text-sm"
                    style={{
                      background: msg.role === 'user' ? colors.accent : colors.bgTertiary,
                      color: colors.textPrimary,
                    }}
                  >
                    {msg.content}
                  </div>
                </div>
              ))}

              {isChatting && (
                <div className="flex justify-start">
                  <div className="px-3 py-2 rounded-lg" style={{ background: colors.bgTertiary }}>
                    <Loader2 size={16} className="animate-spin" style={{ color: colors.textMuted }} />
                  </div>
                </div>
              )}
            </div>

            <div className="p-3 border-t" style={{ borderColor: colors.border }}>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendChatMessage()}
                  placeholder="Ask about this prediction..."
                  className="flex-1 px-3 py-2 rounded-md text-sm"
                  style={{ background: colors.bgTertiary, color: colors.textPrimary, border: `1px solid ${colors.border}` }}
                />
                <button
                  onClick={sendChatMessage}
                  disabled={isChatting || !chatInput.trim()}
                  className="px-3 py-2 rounded-md disabled:opacity-50"
                  style={{ background: colors.accent }}
                >
                  <Send size={16} className="text-white" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Tagline */}
      <div
        className="fixed bottom-4 left-1/2 -translate-x-1/2 px-4 py-2 rounded-full text-xs z-10"
        style={{ background: colors.bgSecondary, color: colors.textMuted, border: `1px solid ${colors.border}` }}
      >
        There's a future where you win; we engineer that for you.
      </div>

      <style jsx global>{`
        @keyframes dash { to { stroke-dashoffset: -10; } }
        .animate-dash { animation: dash 0.5s linear infinite; }
      `}</style>
    </div>
  )
}
