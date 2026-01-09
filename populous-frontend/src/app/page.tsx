'use client'

import { useState, useCallback, useRef, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import {
  Search, Zap, GitBranch, BarChart3, Target,
  Building2, Users, Bot, Layers, Play, Plus,
  ChevronRight, Sparkles, ArrowRight
} from 'lucide-react'

// Node types
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

// Linear design system colors
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

// Canvas Node Component
function CanvasNode({
  node,
  selected,
  onSelect,
  onDrag
}: {
  node: Node
  selected: boolean
  onSelect: (id: string) => void
  onDrag: (id: string, x: number, y: number) => void
}) {
  const Icon = nodeIcons[node.type]
  const color = nodeColors[node.type]
  const [isDragging, setIsDragging] = useState(false)
  const dragStart = useRef({ x: 0, y: 0 })

  const handleMouseDown = (e: React.MouseEvent) => {
    e.preventDefault()
    setIsDragging(true)
    dragStart.current = { x: e.clientX - node.x, y: e.clientY - node.y }
    onSelect(node.id)
  }

  useEffect(() => {
    if (!isDragging) return

    const handleMouseMove = (e: MouseEvent) => {
      onDrag(node.id, e.clientX - dragStart.current.x, e.clientY - dragStart.current.y)
    }

    const handleMouseUp = () => setIsDragging(false)

    window.addEventListener('mousemove', handleMouseMove)
    window.addEventListener('mouseup', handleMouseUp)
    return () => {
      window.removeEventListener('mousemove', handleMouseMove)
      window.removeEventListener('mouseup', handleMouseUp)
    }
  }, [isDragging, node.id, onDrag])

  return (
    <motion.div
      initial={{ scale: 0, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      className="absolute cursor-move select-none"
      style={{ left: node.x, top: node.y }}
      onMouseDown={handleMouseDown}
    >
      <div
        className={`
          w-[200px] rounded-lg border transition-all duration-200
          ${selected ? 'ring-2 ring-offset-2 ring-offset-[#0D0D0F]' : ''}
        `}
        style={{
          background: colors.bgSecondary,
          borderColor: selected ? color : colors.border,
          ringColor: color,
        }}
      >
        {/* Header */}
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
            <div className="ml-auto w-2 h-2 rounded-full bg-yellow-500 animate-pulse" />
          )}
          {node.status === 'complete' && (
            <div className="ml-auto w-2 h-2 rounded-full bg-green-500" />
          )}
        </div>

        {/* Content */}
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

// Canvas Edge Component
function CanvasEdge({ from, to, animated }: { from: { x: number, y: number }, to: { x: number, y: number }, animated?: boolean }) {
  const fromX = from.x + 200 // Right side of node
  const fromY = from.y + 40  // Middle of node
  const toX = to.x           // Left side of node
  const toY = to.y + 40      // Middle of node

  const midX = (fromX + toX) / 2
  const path = `M ${fromX} ${fromY} C ${midX} ${fromY}, ${midX} ${toY}, ${toX} ${toY}`

  return (
    <svg className="absolute inset-0 pointer-events-none" style={{ zIndex: 0 }}>
      <defs>
        <linearGradient id="edgeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor={colors.accent} stopOpacity="0.5" />
          <stop offset="100%" stopColor={colors.accent} stopOpacity="1" />
        </linearGradient>
      </defs>
      <path
        d={path}
        fill="none"
        stroke="url(#edgeGradient)"
        strokeWidth="2"
        strokeDasharray={animated ? "5,5" : "0"}
        className={animated ? "animate-dash" : ""}
      />
      {/* Arrow */}
      <circle cx={toX} cy={toY} r="4" fill={colors.accent} />
    </svg>
  )
}

// Main Canvas Page
export default function CanvasPage() {
  const [nodes, setNodes] = useState<Node[]>([
    { id: '1', type: 'research', x: 100, y: 150, title: 'Research Stripe', subtitle: 'Deep company analysis', status: 'complete' },
    { id: '2', type: 'competitor', x: 400, y: 80, title: 'PayPal', subtitle: 'Leader position', status: 'complete' },
    { id: '3', type: 'competitor', x: 400, y: 220, title: 'Adyen', subtitle: 'Challenger position', status: 'complete' },
    { id: '4', type: 'decision', x: 700, y: 150, title: 'Price Reduction', subtitle: '-15% across all tiers', status: 'idle' },
    { id: '5', type: 'simulation', x: 1000, y: 150, title: 'Monte Carlo', subtitle: '1000 scenarios', status: 'idle' },
  ])

  const [edges] = useState<Edge[]>([
    { id: 'e1', from: '1', to: '2' },
    { id: 'e2', from: '1', to: '3' },
    { id: 'e3', from: '2', to: '4' },
    { id: 'e4', from: '3', to: '4' },
    { id: 'e5', from: '4', to: '5', animated: true },
  ])

  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })

  const handleDrag = useCallback((id: string, x: number, y: number) => {
    setNodes(prev => prev.map(n => n.id === id ? { ...n, x, y } : n))
  }, [])

  const addNode = (type: NodeType) => {
    const newNode: Node = {
      id: `node-${Date.now()}`,
      type,
      x: 200 + Math.random() * 400,
      y: 100 + Math.random() * 200,
      title: `New ${type}`,
      subtitle: 'Click to configure',
      status: 'idle',
    }
    setNodes(prev => [...prev, newNode])
  }

  return (
    <div className="h-screen w-screen overflow-hidden" style={{ background: colors.bg }}>
      {/* Header */}
      <header
        className="h-12 border-b flex items-center justify-between px-4"
        style={{ background: colors.bgSecondary, borderColor: colors.border }}
      >
        <div className="flex items-center gap-3">
          <div className="flex items-center gap-2">
            <div
              className="w-7 h-7 rounded-lg flex items-center justify-center"
              style={{ background: colors.accent }}
            >
              <Zap size={16} className="text-white" />
            </div>
            <span className="font-semibold text-white">Populous</span>
          </div>
          <span className="text-xs px-2 py-0.5 rounded" style={{ background: colors.bgTertiary, color: colors.textMuted }}>
            Canvas
          </span>
        </div>

        <div className="flex items-center gap-2">
          <button
            className="px-3 py-1.5 rounded-md text-sm flex items-center gap-2 transition-colors"
            style={{ background: colors.bgTertiary, color: colors.textSecondary }}
          >
            <Play size={14} />
            Run Simulation
          </button>
        </div>
      </header>

      {/* Toolbar */}
      <div
        className="absolute left-4 top-16 rounded-lg border p-2 flex flex-col gap-1 z-10"
        style={{ background: colors.bgSecondary, borderColor: colors.border }}
      >
        <span className="text-xs px-2 py-1" style={{ color: colors.textMuted }}>Workflow</span>
        {(['research', 'decision', 'simulation', 'analysis', 'recommendation'] as NodeType[]).map(type => {
          const Icon = nodeIcons[type]
          return (
            <button
              key={type}
              onClick={() => addNode(type)}
              className="w-9 h-9 rounded-md flex items-center justify-center transition-colors hover:bg-[#26262C]"
              title={type}
            >
              <Icon size={18} style={{ color: nodeColors[type] }} />
            </button>
          )
        })}

        <div className="h-px my-1" style={{ background: colors.border }} />

        <span className="text-xs px-2 py-1" style={{ color: colors.textMuted }}>Entities</span>
        {(['company', 'competitor', 'agent', 'scenario'] as NodeType[]).map(type => {
          const Icon = nodeIcons[type]
          return (
            <button
              key={type}
              onClick={() => addNode(type)}
              className="w-9 h-9 rounded-md flex items-center justify-center transition-colors hover:bg-[#26262C]"
              title={type}
            >
              <Icon size={18} style={{ color: nodeColors[type] }} />
            </button>
          )
        })}
      </div>

      {/* Canvas */}
      <div
        className="relative w-full h-[calc(100vh-48px)] overflow-hidden"
        style={{
          backgroundImage: `radial-gradient(${colors.border} 1px, transparent 1px)`,
          backgroundSize: '24px 24px',
        }}
      >
        {/* Edges */}
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

        {/* Nodes */}
        {nodes.map(node => (
          <CanvasNode
            key={node.id}
            node={node}
            selected={selectedNode === node.id}
            onSelect={setSelectedNode}
            onDrag={handleDrag}
          />
        ))}
      </div>

      {/* Right Panel - Node Details */}
      <AnimatePresence>
        {selectedNode && (
          <motion.div
            initial={{ x: 300, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 300, opacity: 0 }}
            className="absolute right-0 top-12 bottom-0 w-80 border-l"
            style={{ background: colors.bgSecondary, borderColor: colors.border }}
          >
            <div className="p-4">
              <h2 className="text-lg font-medium text-white">Node Details</h2>
              <p className="text-sm mt-2" style={{ color: colors.textSecondary }}>
                Configure the selected node
              </p>

              {(() => {
                const node = nodes.find(n => n.id === selectedNode)
                if (!node) return null
                const Icon = nodeIcons[node.type]
                return (
                  <div className="mt-4 space-y-4">
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

      {/* Tagline */}
      <div
        className="absolute bottom-4 left-1/2 -translate-x-1/2 px-4 py-2 rounded-full text-xs"
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
