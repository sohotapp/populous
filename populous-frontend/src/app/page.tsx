'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import Link from 'next/link'
import {
  Search, Zap, GitBranch, BarChart3, Target,
  Building2, Users, Bot, Layers, Play, Plus,
  ChevronRight, Sparkles, FolderOpen, UserCircle,
  FileText, Settings, Minus, RotateCcw, X, Loader2,
  CheckCircle, AlertCircle
} from 'lucide-react'

// ============================================================================
// TYPES
// ============================================================================

type NodeType = 'research' | 'decision' | 'simulation' | 'analysis' | 'recommendation' |
                'company' | 'competitor' | 'agent' | 'scenario'

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

interface SimulationStatus {
  id: string
  status: 'pending' | 'running' | 'completed' | 'failed'
  progress: number
  result_id?: string
}

interface SimulationResults {
  id: string
  mean_conversion: number
  std_conversion: number
  p5: number
  p95: number
  insight?: string
  segment_analysis: Array<{
    segment_id: string
    segment_name: string
    conversion_rate: number
  }>
}

// ============================================================================
// DESIGN SYSTEM
// ============================================================================

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
}

const nodeIcons: Record<NodeType, any> = {
  research: Search,
  decision: Target,
  simulation: GitBranch,
  analysis: BarChart3,
  recommendation: Sparkles,
  company: Building2,
  competitor: Layers,
  agent: Bot,
  scenario: Zap,
}

const nodeColors: Record<NodeType, string> = {
  research: '#5E6AD2',
  decision: '#3FB950',
  simulation: '#D29922',
  analysis: '#58A6FF',
  recommendation: '#A371F7',
  company: '#8B949E',
  competitor: '#F85149',
  agent: '#39D353',
  scenario: '#F0883E',
}

// ============================================================================
// API CLIENT
// ============================================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api-production-9cbf.up.railway.app'

const api = {
  getScenarios: async () => {
    const res = await fetch(`${API_URL}/scenarios`)
    return res.json()
  },
  getStrategies: async () => {
    const res = await fetch(`${API_URL}/strategies`)
    return res.json()
  },
  runSimulation: async (scenarioId: string, strategyId: string, numAgents = 5000, numBranches = 200) => {
    const res = await fetch(`${API_URL}/simulations`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenario_id: scenarioId,
        strategy_id: strategyId,
        num_agents: numAgents,
        num_branches: numBranches,
        use_llm_personas: false
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
  compareStrategies: async (scenarioId: string, strategyIds: string[]) => {
    const res = await fetch(`${API_URL}/compare`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        scenario_id: scenarioId,
        strategy_ids: strategyIds,
        num_agents: 5000,
        num_branches: 200
      })
    })
    return res.json()
  }
}

// ============================================================================
// CANVAS NODE COMPONENT
// ============================================================================

function CanvasNode({
  node,
  selected,
  onSelect,
  onDrag,
  transform
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
    if (e.button !== 0) return // Only left click
    e.preventDefault()
    e.stopPropagation()
    setIsDragging(true)
    dragStart.current = {
      x: e.clientX,
      y: e.clientY,
      nodeX: node.x,
      nodeY: node.y
    }
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
        className="w-[200px] rounded-lg border transition-all duration-200"
        style={{
          background: colors.bgSecondary,
          borderColor: selected ? color : colors.border,
          boxShadow: selected ? `0 0 0 2px ${colors.bg}, 0 0 0 4px ${color}` : 'none',
        }}
      >
        <div
          className="px-3 py-2 border-b flex items-center gap-2"
          style={{ borderColor: colors.border }}
        >
          <div
            className="w-6 h-6 rounded flex items-center justify-center"
            style={{ background: `${color}20` }}
          >
            <Icon size={14} style={{ color }} />
          </div>
          <span className="text-xs font-medium uppercase tracking-wider" style={{ color: colors.textMuted }}>
            {node.type}
          </span>
          {node.status === 'running' && (
            <Loader2 className="ml-auto w-4 h-4 animate-spin text-yellow-500" />
          )}
          {node.status === 'complete' && (
            <CheckCircle className="ml-auto w-4 h-4 text-green-500" />
          )}
          {node.status === 'error' && (
            <AlertCircle className="ml-auto w-4 h-4 text-red-500" />
          )}
        </div>

        <div className="px-3 py-3">
          <h3 className="text-sm font-medium" style={{ color: colors.textPrimary }}>
            {node.title}
          </h3>
          {node.subtitle && (
            <p className="text-xs mt-1" style={{ color: colors.textSecondary }}>
              {node.subtitle}
            </p>
          )}
        </div>

        {/* Connection handles */}
        <div
          className="absolute -left-1.5 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2"
          style={{ background: colors.bg, borderColor: colors.border }}
        />
        <div
          className="absolute -right-1.5 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full border-2"
          style={{ background: colors.bg, borderColor: colors.border }}
        />
      </div>
    </motion.div>
  )
}

// ============================================================================
// CANVAS EDGE COMPONENT
// ============================================================================

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
        stroke={colors.accent}
        strokeWidth="2"
        strokeOpacity={animated ? 1 : 0.5}
        strokeDasharray={animated ? "5,5" : "0"}
        className={animated ? "animate-dash" : ""}
      />
      <circle cx={toX} cy={toY} r="4" fill={colors.accent} />
    </g>
  )
}

// ============================================================================
// MAIN CANVAS PAGE
// ============================================================================

export default function CanvasPage() {
  // Canvas state
  const [nodes, setNodes] = useState<Node[]>([
    { id: '1', type: 'scenario', x: 100, y: 150, title: 'B2B SaaS Launch', subtitle: 'Project management market', status: 'complete', data: { scenarioId: 'saas_launch_2024' } },
    { id: '2', type: 'competitor', x: 380, y: 80, title: 'Monday.com', subtitle: '30% market share', status: 'complete' },
    { id: '3', type: 'competitor', x: 380, y: 220, title: 'Asana', subtitle: '25% market share', status: 'complete' },
    { id: '4', type: 'decision', x: 660, y: 150, title: 'Value Play', subtitle: 'Lead with price, target SMB', status: 'idle', data: { strategyId: 'value_play' } },
    { id: '5', type: 'simulation', x: 940, y: 150, title: 'Monte Carlo', subtitle: '5000 agents, 200 branches', status: 'idle' },
  ])

  const [edges, setEdges] = useState<Edge[]>([
    { id: 'e1', from: '1', to: '2' },
    { id: 'e2', from: '1', to: '3' },
    { id: 'e3', from: '2', to: '4' },
    { id: 'e4', from: '3', to: '4' },
    { id: 'e5', from: '4', to: '5', animated: true },
  ])

  const [selectedNode, setSelectedNode] = useState<string | null>(null)

  // Transform state for pan/zoom
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 1 })
  const [isPanning, setIsPanning] = useState(false)
  const panStart = useRef({ x: 0, y: 0, transformX: 0, transformY: 0 })
  const canvasRef = useRef<HTMLDivElement>(null)

  // Simulation state
  const [isSimulating, setIsSimulating] = useState(false)
  const [simulationStatus, setSimulationStatus] = useState<SimulationStatus | null>(null)
  const [results, setResults] = useState<SimulationResults | null>(null)
  const [showResults, setShowResults] = useState(false)

  // Sidebar state
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)

  // ============================================================================
  // PAN/ZOOM HANDLERS (FIGMA-STYLE)
  // ============================================================================

  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault()
    const delta = e.deltaY > 0 ? 0.9 : 1.1
    const newScale = Math.min(Math.max(transform.scale * delta, 0.25), 2)

    // Zoom toward cursor position
    const rect = canvasRef.current?.getBoundingClientRect()
    if (rect) {
      const x = e.clientX - rect.left
      const y = e.clientY - rect.top
      const newX = x - (x - transform.x) * (newScale / transform.scale)
      const newY = y - (y - transform.y) * (newScale / transform.scale)
      setTransform({ x: newX, y: newY, scale: newScale })
    } else {
      setTransform(prev => ({ ...prev, scale: newScale }))
    }
  }, [transform])

  const handleCanvasMouseDown = useCallback((e: React.MouseEvent) => {
    // Space+click or middle mouse button to pan
    if (e.button === 1 || (e.button === 0 && e.altKey)) {
      e.preventDefault()
      setIsPanning(true)
      panStart.current = {
        x: e.clientX,
        y: e.clientY,
        transformX: transform.x,
        transformY: transform.y
      }
    } else if (e.button === 0 && e.target === e.currentTarget) {
      // Click on empty canvas to deselect
      setSelectedNode(null)
    }
  }, [transform])

  useEffect(() => {
    if (!isPanning) return

    const handleMouseMove = (e: MouseEvent) => {
      const dx = e.clientX - panStart.current.x
      const dy = e.clientY - panStart.current.y
      setTransform(prev => ({
        ...prev,
        x: panStart.current.transformX + dx,
        y: panStart.current.transformY + dy
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

  // ============================================================================
  // NODE HANDLERS
  // ============================================================================

  const handleDrag = useCallback((id: string, x: number, y: number) => {
    setNodes(prev => prev.map(n => n.id === id ? { ...n, x, y } : n))
  }, [])

  const addNode = (type: NodeType) => {
    const canvasCenter = {
      x: (window.innerWidth / 2 - transform.x) / transform.scale,
      y: (window.innerHeight / 2 - transform.y) / transform.scale
    }
    const newNode: Node = {
      id: `node-${Date.now()}`,
      type,
      x: canvasCenter.x - 100 + Math.random() * 200,
      y: canvasCenter.y - 50 + Math.random() * 100,
      title: `New ${type}`,
      subtitle: 'Click to configure',
      status: 'idle',
    }
    setNodes(prev => [...prev, newNode])
  }

  const resetView = () => {
    setTransform({ x: 0, y: 0, scale: 1 })
  }

  // ============================================================================
  // SIMULATION HANDLERS
  // ============================================================================

  const runSimulation = async () => {
    setIsSimulating(true)
    setShowResults(false)
    setResults(null)

    // Update simulation node status
    setNodes(prev => prev.map(n =>
      n.type === 'simulation' ? { ...n, status: 'running' } : n
    ))

    try {
      // Start simulation
      const simResponse = await api.runSimulation('saas_launch_2024', 'value_play', 5000, 200)
      setSimulationStatus(simResponse)

      // Poll for completion
      const pollInterval = setInterval(async () => {
        const status = await api.getSimulationStatus(simResponse.id)
        setSimulationStatus(status)

        if (status.status === 'completed' && status.result_id) {
          clearInterval(pollInterval)
          const resultsData = await api.getResults(status.result_id)
          setResults(resultsData)
          setShowResults(true)
          setIsSimulating(false)
          setNodes(prev => prev.map(n =>
            n.type === 'simulation' ? { ...n, status: 'complete', subtitle: `${(resultsData.mean_conversion * 100).toFixed(1)}% conversion` } : n
          ))
        } else if (status.status === 'failed') {
          clearInterval(pollInterval)
          setIsSimulating(false)
          setNodes(prev => prev.map(n =>
            n.type === 'simulation' ? { ...n, status: 'error' } : n
          ))
        }
      }, 1000)
    } catch (error) {
      console.error('Simulation failed:', error)
      setIsSimulating(false)
      setNodes(prev => prev.map(n =>
        n.type === 'simulation' ? { ...n, status: 'error' } : n
      ))
    }
  }

  // ============================================================================
  // RENDER
  // ============================================================================

  return (
    <div className="h-screen w-screen overflow-hidden flex" style={{ background: colors.bg }}>
      {/* Left Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarCollapsed ? 56 : 200 }}
        className="h-full border-r flex flex-col z-20"
        style={{ background: colors.bgSecondary, borderColor: colors.border }}
      >
        {/* Logo */}
        <div className="h-12 border-b flex items-center px-3 gap-2" style={{ borderColor: colors.border }}>
          <div
            className="w-7 h-7 rounded-lg flex items-center justify-center flex-shrink-0"
            style={{ background: colors.accent }}
          >
            <Zap size={16} className="text-white" />
          </div>
          {!sidebarCollapsed && (
            <span className="font-semibold text-white text-sm">Populous Demo</span>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-2 space-y-1">
          <Link
            href="/projects"
            className="flex items-center gap-2 px-2 py-2 rounded-md hover:bg-[#26262C] transition-colors"
          >
            <FolderOpen size={18} style={{ color: colors.textSecondary }} />
            {!sidebarCollapsed && <span className="text-sm" style={{ color: colors.textSecondary }}>Projects</span>}
          </Link>
          <Link
            href="/audiences"
            className="flex items-center gap-2 px-2 py-2 rounded-md hover:bg-[#26262C] transition-colors"
          >
            <Users size={18} style={{ color: colors.textSecondary }} />
            {!sidebarCollapsed && <span className="text-sm" style={{ color: colors.textSecondary }}>Audiences</span>}
          </Link>
          <Link
            href="/templates"
            className="flex items-center gap-2 px-2 py-2 rounded-md hover:bg-[#26262C] transition-colors"
          >
            <FileText size={18} style={{ color: colors.textSecondary }} />
            {!sidebarCollapsed && <span className="text-sm" style={{ color: colors.textSecondary }}>Templates</span>}
          </Link>

          <div className="h-px my-2" style={{ background: colors.border }} />

          {/* Node types */}
          {!sidebarCollapsed && (
            <span className="text-xs px-2 py-1 block" style={{ color: colors.textMuted }}>Add Node</span>
          )}
          {(['research', 'decision', 'simulation', 'analysis'] as NodeType[]).map(type => {
            const Icon = nodeIcons[type]
            return (
              <button
                key={type}
                onClick={() => addNode(type)}
                className="w-full flex items-center gap-2 px-2 py-2 rounded-md hover:bg-[#26262C] transition-colors"
                title={type}
              >
                <Icon size={18} style={{ color: nodeColors[type] }} />
                {!sidebarCollapsed && (
                  <span className="text-sm capitalize" style={{ color: colors.textSecondary }}>{type}</span>
                )}
              </button>
            )
          })}
        </nav>

        {/* Collapse toggle */}
        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="h-10 border-t flex items-center justify-center hover:bg-[#26262C] transition-colors"
          style={{ borderColor: colors.border }}
        >
          <ChevronRight
            size={16}
            style={{ color: colors.textMuted, transform: sidebarCollapsed ? 'rotate(0)' : 'rotate(180deg)' }}
          />
        </button>
      </motion.aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header
          className="h-12 border-b flex items-center justify-between px-4 z-10"
          style={{ background: colors.bgSecondary, borderColor: colors.border }}
        >
          <div className="flex items-center gap-3">
            <span className="text-sm font-medium text-white">Decision Canvas</span>
            <span className="text-xs px-2 py-0.5 rounded" style={{ background: colors.bgTertiary, color: colors.textMuted }}>
              {Math.round(transform.scale * 100)}%
            </span>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={resetView}
              className="p-2 rounded-md transition-colors hover:bg-[#26262C]"
              title="Reset view"
            >
              <RotateCcw size={16} style={{ color: colors.textSecondary }} />
            </button>
            <button
              onClick={() => setTransform(prev => ({ ...prev, scale: Math.max(0.25, prev.scale - 0.1) }))}
              className="p-2 rounded-md transition-colors hover:bg-[#26262C]"
            >
              <Minus size={16} style={{ color: colors.textSecondary }} />
            </button>
            <button
              onClick={() => setTransform(prev => ({ ...prev, scale: Math.min(2, prev.scale + 0.1) }))}
              className="p-2 rounded-md transition-colors hover:bg-[#26262C]"
            >
              <Plus size={16} style={{ color: colors.textSecondary }} />
            </button>

            <div className="w-px h-6 mx-2" style={{ background: colors.border }} />

            <button
              onClick={runSimulation}
              disabled={isSimulating}
              className="px-4 py-1.5 rounded-md text-sm font-medium flex items-center gap-2 transition-colors disabled:opacity-50"
              style={{ background: colors.accent, color: 'white' }}
            >
              {isSimulating ? (
                <>
                  <Loader2 size={14} className="animate-spin" />
                  Running...
                </>
              ) : (
                <>
                  <Play size={14} />
                  Run Simulation
                </>
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
          {/* Transform container */}
          <div
            style={{
              transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})`,
              transformOrigin: '0 0',
            }}
          >
            {/* Edges SVG */}
            <svg className="absolute inset-0 pointer-events-none" style={{ width: '5000px', height: '5000px', overflow: 'visible' }}>
              {edges.map(edge => {
                const fromNode = nodes.find(n => n.id === edge.from)
                const toNode = nodes.find(n => n.id === edge.to)
                if (!fromNode || !toNode) return null
                return (
                  <CanvasEdge
                    key={edge.id}
                    from={{ x: fromNode.x, y: fromNode.y }}
                    to={{ x: toNode.x, y: toNode.y }}
                    animated={edge.animated}
                  />
                )
              })}
            </svg>

            {/* Nodes */}
            {nodes.map(node => (
              <CanvasNode
                key={node.id}
                node={node}
                selected={selectedNode === node.id}
                onSelect={setSelectedNode}
                onDrag={handleDrag}
                transform={transform}
              />
            ))}
          </div>

          {/* Instructions overlay */}
          <div
            className="absolute bottom-4 left-4 px-3 py-2 rounded-lg text-xs"
            style={{ background: colors.bgSecondary, color: colors.textMuted, border: `1px solid ${colors.border}` }}
          >
            Scroll to zoom | Alt+drag to pan | Drag nodes to move
          </div>
        </div>
      </div>

      {/* Right Panel - Node Details */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            initial={{ x: 320, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 320, opacity: 0 }}
            className="w-80 border-l flex flex-col z-20"
            style={{ background: colors.bgSecondary, borderColor: colors.border }}
          >
            <div className="h-12 border-b flex items-center justify-between px-4" style={{ borderColor: colors.border }}>
              <h2 className="text-sm font-medium text-white">Node Details</h2>
              <button onClick={() => setSelectedNode(null)} className="p-1 hover:bg-[#26262C] rounded">
                <X size={16} style={{ color: colors.textMuted }} />
              </button>
            </div>
            <div className="flex-1 overflow-auto p-4">
              {(() => {
                const node = nodes.find(n => n.id === selectedNode)
                if (!node) return null
                const Icon = nodeIcons[node.type]
                return (
                  <div className="space-y-4">
                    <div
                      className="p-3 rounded-lg border"
                      style={{ background: colors.bgTertiary, borderColor: colors.border }}
                    >
                      <div className="flex items-center gap-2">
                        <Icon size={16} style={{ color: nodeColors[node.type] }} />
                        <span className="text-sm font-medium text-white">{node.title}</span>
                      </div>
                      <p className="text-xs mt-1" style={{ color: colors.textSecondary }}>
                        {node.subtitle}
                      </p>
                    </div>

                    <div className="space-y-2">
                      <label className="text-xs" style={{ color: colors.textMuted }}>Status</label>
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${
                          node.status === 'complete' ? 'bg-green-500' :
                          node.status === 'running' ? 'bg-yellow-500 animate-pulse' :
                          node.status === 'error' ? 'bg-red-500' :
                          'bg-gray-500'
                        }`} />
                        <span className="text-sm capitalize" style={{ color: colors.textSecondary }}>
                          {node.status || 'idle'}
                        </span>
                      </div>
                    </div>

                    {node.type === 'simulation' && node.status === 'complete' && results && (
                      <div className="space-y-3 pt-3 border-t" style={{ borderColor: colors.border }}>
                        <h3 className="text-xs font-medium" style={{ color: colors.textMuted }}>RESULTS</h3>
                        <div className="grid grid-cols-2 gap-2">
                          <div className="p-2 rounded" style={{ background: colors.bgTertiary }}>
                            <p className="text-xs" style={{ color: colors.textMuted }}>Mean</p>
                            <p className="text-lg font-semibold text-white">{(results.mean_conversion * 100).toFixed(1)}%</p>
                          </div>
                          <div className="p-2 rounded" style={{ background: colors.bgTertiary }}>
                            <p className="text-xs" style={{ color: colors.textMuted }}>Std Dev</p>
                            <p className="text-lg font-semibold text-white">{(results.std_conversion * 100).toFixed(2)}%</p>
                          </div>
                        </div>
                        <div className="p-2 rounded" style={{ background: colors.bgTertiary }}>
                          <p className="text-xs" style={{ color: colors.textMuted }}>90% Confidence Interval</p>
                          <p className="text-sm text-white">{(results.p5 * 100).toFixed(1)}% - {(results.p95 * 100).toFixed(1)}%</p>
                        </div>
                      </div>
                    )}

                    <button
                      className="w-full py-2 rounded-md text-sm font-medium transition-colors"
                      style={{ background: colors.accent, color: 'white' }}
                    >
                      Configure Node
                    </button>
                  </div>
                )
              })()}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Results Modal */}
      <AnimatePresence>
        {showResults && results && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center"
            style={{ background: 'rgba(0,0,0,0.8)' }}
            onClick={() => setShowResults(false)}
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.9, opacity: 0 }}
              className="w-[600px] max-h-[80vh] overflow-auto rounded-xl border"
              style={{ background: colors.bgSecondary, borderColor: colors.border }}
              onClick={e => e.stopPropagation()}
            >
              <div className="p-6 border-b" style={{ borderColor: colors.border }}>
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-semibold text-white">Simulation Results</h2>
                  <button onClick={() => setShowResults(false)} className="p-2 hover:bg-[#26262C] rounded-lg">
                    <X size={20} style={{ color: colors.textMuted }} />
                  </button>
                </div>
              </div>

              <div className="p-6 space-y-6">
                {/* Summary stats */}
                <div className="grid grid-cols-3 gap-4">
                  <div className="p-4 rounded-lg" style={{ background: colors.bgTertiary }}>
                    <p className="text-xs" style={{ color: colors.textMuted }}>Mean Conversion</p>
                    <p className="text-2xl font-bold" style={{ color: colors.success }}>{(results.mean_conversion * 100).toFixed(1)}%</p>
                  </div>
                  <div className="p-4 rounded-lg" style={{ background: colors.bgTertiary }}>
                    <p className="text-xs" style={{ color: colors.textMuted }}>5th Percentile</p>
                    <p className="text-2xl font-bold text-white">{(results.p5 * 100).toFixed(1)}%</p>
                  </div>
                  <div className="p-4 rounded-lg" style={{ background: colors.bgTertiary }}>
                    <p className="text-xs" style={{ color: colors.textMuted }}>95th Percentile</p>
                    <p className="text-2xl font-bold text-white">{(results.p95 * 100).toFixed(1)}%</p>
                  </div>
                </div>

                {/* Segment breakdown */}
                {results.segment_analysis && results.segment_analysis.length > 0 && (
                  <div>
                    <h3 className="text-sm font-medium text-white mb-3">Segment Performance</h3>
                    <div className="space-y-2">
                      {results.segment_analysis.map(segment => (
                        <div
                          key={segment.segment_id}
                          className="flex items-center justify-between p-3 rounded-lg"
                          style={{ background: colors.bgTertiary }}
                        >
                          <span className="text-sm text-white">{segment.segment_name}</span>
                          <div className="flex items-center gap-3">
                            <div className="w-32 h-2 rounded-full overflow-hidden" style={{ background: colors.border }}>
                              <div
                                className="h-full rounded-full"
                                style={{ width: `${segment.conversion_rate * 100}%`, background: colors.accent }}
                              />
                            </div>
                            <span className="text-sm font-medium text-white w-12 text-right">
                              {(segment.conversion_rate * 100).toFixed(1)}%
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Insight */}
                {results.insight && (
                  <div className="p-4 rounded-lg border" style={{ background: `${colors.accent}10`, borderColor: colors.accent }}>
                    <div className="flex items-center gap-2 mb-2">
                      <Sparkles size={16} style={{ color: colors.accent }} />
                      <span className="text-sm font-medium" style={{ color: colors.accent }}>AI Insight</span>
                    </div>
                    <p className="text-sm" style={{ color: colors.textSecondary }}>{results.insight}</p>
                  </div>
                )}
              </div>
            </motion.div>
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
        @keyframes dash {
          to {
            stroke-dashoffset: -10;
          }
        }
        .animate-dash {
          animation: dash 0.5s linear infinite;
        }
      `}</style>
    </div>
  )
}
