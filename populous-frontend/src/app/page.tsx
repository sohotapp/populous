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
  Command, Activity, Network, Database,
  LineChart, PieChart, Gauge, Shield,
  Calendar, Bell, Eye, Sliders, Map,
  GitMerge, Boxes, Briefcase, FileBarChart,
  Radio, Radar, Scale, Timer, Workflow,
  Brain, Cpu, Globe, Newspaper, Share2,
  TrendingDown, ArrowUpRight, ArrowDownRight,
  Info, Settings, Download, Copy, Link2
} from 'lucide-react'

// =============================================================================
// COMPREHENSIVE NODE TYPE SYSTEM
// =============================================================================

type NodeCategory = 'input' | 'analysis' | 'simulation' | 'output'

type NodeType =
  // Data Input Nodes
  | 'batch' | 'research' | 'market_scanner' | 'network_graph'
  | 'alternative_data' | 'financial_signals' | 'historical_outcomes'
  // Analysis Nodes
  | 'prediction' | 'monte_carlo' | 'sensitivity' | 'cohort_comparison'
  | 'risk_decomposition' | 'market_timing' | 'competitive_dynamics'
  | 'portfolio_optimizer' | 'scenario_planner'
  // Simulation Nodes
  | 'trajectory_sim' | 'exit_modeler' | 'funding_scenarios'
  // Output Nodes
  | 'chat' | 'decision_brief' | 'investment_memo' | 'risk_report'
  | 'portfolio_dashboard' | 'comparison_matrix' | 'alert_system'
  | 'stakeholder_views' | 'whatif_explorer' | 'timeline_projection'

interface NodeConfig {
  type: NodeType
  category: NodeCategory
  title: string
  subtitle: string
  icon: any
  color: string
  description: string
  inputs: string[]
  outputs: string[]
  capabilities: string[]
  dataSchema: Record<string, string>
}

// Complete node configuration with depth
const NODE_CONFIGS: Record<NodeType, NodeConfig> = {
  // ==========================================================================
  // DATA INPUT NODES
  // ==========================================================================
  batch: {
    type: 'batch',
    category: 'input',
    title: 'YC Batch Analysis',
    subtitle: 'Accelerator batch ingestion',
    icon: Layers,
    color: '#F0883E',
    description: 'Ingests and analyzes entire Y Combinator batches. Pulls company lists from YC\'s public directory, cross-references with Crunchbase data, and initializes the research pipeline for each company.',
    inputs: ['Batch code (W24, S23, etc.)', 'Max companies to analyze', 'Filter criteria'],
    outputs: ['Company list', 'Initial metadata', 'Batch context'],
    capabilities: [
      'Automatic company discovery from YC directory',
      'Batch-level metadata extraction (theme, size, timing)',
      'Historical batch performance benchmarking',
      'Parallel research orchestration'
    ],
    dataSchema: {
      batch_name: 'string',
      batch_size: 'number',
      companies: 'Company[]',
      batch_theme: 'string',
      historical_unicorn_rate: 'number'
    }
  },
  research: {
    type: 'research',
    category: 'input',
    title: 'Deep Research',
    subtitle: 'Multi-source intelligence',
    icon: Search,
    color: '#5E6AD2',
    description: 'Executes 15-20 targeted web queries per company across founder backgrounds, funding history, traction signals, and market positioning. Uses structured extraction to pull specific data points with confidence scoring.',
    inputs: ['Company name', 'Batch context', 'Research depth'],
    outputs: ['Founder profiles', 'Funding data', 'Traction metrics', 'Market data'],
    capabilities: [
      'Multi-query research strategy (founders, funding, traction, market)',
      'Structured data extraction with confidence scores',
      'Source triangulation for data validation',
      'Proxy estimation for missing metrics'
    ],
    dataSchema: {
      founders: 'FounderProfile[]',
      funding_rounds: 'FundingRound[]',
      traction_metrics: 'TractionData',
      market_data: 'MarketData',
      source_count: 'number',
      data_quality: 'high | medium | low'
    }
  },
  market_scanner: {
    type: 'market_scanner',
    category: 'input',
    title: 'Market Scanner',
    subtitle: 'Real-time market intelligence',
    icon: Radar,
    color: '#3FB950',
    description: 'Continuously monitors market signals: funding announcements, M&A activity, sector news, and competitive moves. Provides real-time context for timing scores and market positioning.',
    inputs: ['Sector focus', 'Geographic scope', 'Time window'],
    outputs: ['Market trends', 'Funding velocity', 'News sentiment', 'Competitive signals'],
    capabilities: [
      'Real-time funding announcement tracking',
      'Sector-level trend analysis',
      'News sentiment aggregation',
      'Competitive move detection',
      'Market cycle positioning'
    ],
    dataSchema: {
      sector_funding_velocity: 'number',
      recent_deals: 'Deal[]',
      sentiment_score: 'number',
      market_cycle_phase: 'nascent | emerging | growth | mature | declining',
      key_trends: 'string[]'
    }
  },
  network_graph: {
    type: 'network_graph',
    category: 'input',
    title: 'Network Graph',
    subtitle: 'Relationship intelligence',
    icon: Share2,
    color: '#A371F7',
    description: 'Maps investor relationships, founder connections, board overlaps, and advisor networks. Identifies warm intro paths, syndicate patterns, and network-driven competitive advantages.',
    inputs: ['Entity list', 'Relationship types', 'Depth'],
    outputs: ['Connection graph', 'Influence scores', 'Intro paths'],
    capabilities: [
      'Investor network mapping',
      'Founder connection graph',
      'Board overlap analysis',
      'Warm intro path finding',
      'Network effect quantification'
    ],
    dataSchema: {
      nodes: 'NetworkNode[]',
      edges: 'NetworkEdge[]',
      influence_scores: 'Record<string, number>',
      clusters: 'Cluster[]',
      intro_paths: 'Path[]'
    }
  },
  alternative_data: {
    type: 'alternative_data',
    category: 'input',
    title: 'Alternative Data',
    subtitle: 'Non-traditional signals',
    icon: Database,
    color: '#58A6FF',
    description: 'Aggregates alternative data signals: job postings (hiring velocity), GitHub activity (developer traction), app store rankings, web traffic trends, and social media presence.',
    inputs: ['Company identifiers', 'Signal types', 'Time range'],
    outputs: ['Job posting trends', 'GitHub metrics', 'Traffic data', 'Social signals'],
    capabilities: [
      'Job posting analysis (Lever, Greenhouse, LinkedIn)',
      'GitHub repository metrics (stars, commits, contributors)',
      'Web traffic estimation (SimilarWeb proxies)',
      'App store ranking tracking',
      'Social media presence scoring'
    ],
    dataSchema: {
      job_postings: 'JobPosting[]',
      github_metrics: 'GitHubMetrics',
      traffic_estimate: 'number',
      app_rankings: 'AppRanking[]',
      social_scores: 'SocialMetrics'
    }
  },
  financial_signals: {
    type: 'financial_signals',
    category: 'input',
    title: 'Financial Signals',
    subtitle: 'Financial intelligence',
    icon: DollarSign,
    color: '#D4A72C',
    description: 'Tracks financial indicators: SEC filings for public comps, recent M&A transactions, valuation multiples, and capital efficiency benchmarks.',
    inputs: ['Sector', 'Stage', 'Geography'],
    outputs: ['Comp valuations', 'M&A data', 'Multiples', 'Benchmarks'],
    capabilities: [
      'Public company comparable analysis',
      'Recent M&A transaction tracking',
      'Valuation multiple calculation',
      'Capital efficiency benchmarking',
      'Revenue multiple by sector/stage'
    ],
    dataSchema: {
      public_comps: 'PublicComp[]',
      recent_ma: 'MATransaction[]',
      median_multiples: 'Multiples',
      efficiency_benchmarks: 'Benchmarks'
    }
  },
  historical_outcomes: {
    type: 'historical_outcomes',
    category: 'input',
    title: 'Historical Outcomes',
    subtitle: 'Outcome calibration data',
    icon: Clock,
    color: '#8B8B8D',
    description: 'Database of historical startup outcomes for model calibration. Tracks YC/Techstars/a16z portfolio performance, exit data, and failure patterns.',
    inputs: ['Accelerator', 'Vintage years', 'Outcome types'],
    outputs: ['Outcome distributions', 'Base rates', 'Pattern matches'],
    capabilities: [
      'Historical unicorn rate by batch',
      'Time-to-exit distributions',
      'Failure pattern analysis',
      'Factor-outcome correlation',
      'Model calibration data'
    ],
    dataSchema: {
      unicorn_rate: 'number',
      centaur_rate: 'number',
      failure_rate: 'number',
      median_time_to_exit: 'number',
      outcome_distribution: 'Distribution'
    }
  },

  // ==========================================================================
  // ANALYSIS NODES
  // ==========================================================================
  prediction: {
    type: 'prediction',
    category: 'analysis',
    title: 'Unicorn Prediction',
    subtitle: 'Factor-based model',
    icon: TrendingUp,
    color: '#A371F7',
    description: 'Core prediction engine using a 5-factor model calibrated on YC\'s historical 1.6% unicorn rate. Factors: Team (30%), Market (25%), Traction (20%), Timing (15%), Capital (10%).',
    inputs: ['Research data', 'Market context', 'Historical benchmarks'],
    outputs: ['Unicorn probability', 'Factor scores', 'Confidence interval'],
    capabilities: [
      'Multi-factor probability calculation',
      'Logistic transformation calibrated to base rates',
      'Per-factor confidence scoring',
      'Data quality adjustment',
      'Detailed reasoning generation'
    ],
    dataSchema: {
      unicorn_probability: 'number',
      factor_scores: 'FactorScores',
      confidence_interval: '[number, number]',
      prediction_confidence: 'number',
      reasoning: 'string'
    }
  },
  monte_carlo: {
    type: 'monte_carlo',
    category: 'analysis',
    title: 'Monte Carlo Simulator',
    subtitle: '10,000 scenario simulation',
    icon: Boxes,
    color: '#E5534B',
    description: 'Runs 10,000+ simulations sampling from uncertainty distributions for each factor. Produces full probability distributions, not just point estimates. Enables true confidence intervals.',
    inputs: ['Factor distributions', 'Correlation matrix', 'Simulation count'],
    outputs: ['Outcome distribution', 'Percentiles', 'Scenario paths'],
    capabilities: [
      'Triangular distribution sampling per factor',
      'Correlated random variable generation',
      'Full outcome distribution computation',
      'Percentile extraction (p5, p25, p50, p75, p95)',
      'Scenario path visualization'
    ],
    dataSchema: {
      simulations: 'number',
      outcome_distribution: 'number[]',
      percentiles: 'Percentiles',
      mean: 'number',
      std_dev: 'number',
      scenario_paths: 'Path[]'
    }
  },
  sensitivity: {
    type: 'sensitivity',
    category: 'analysis',
    title: 'Sensitivity Analysis',
    subtitle: 'What-if impact analysis',
    icon: Sliders,
    color: '#58A6FF',
    description: 'Identifies which factors have the greatest impact on outcomes. Shows how changes in each input affect the final probability. Reveals inflection points and key drivers.',
    inputs: ['Base prediction', 'Factor ranges', 'Granularity'],
    outputs: ['Sensitivity matrix', 'Tornado chart', 'Inflection points'],
    capabilities: [
      'One-at-a-time sensitivity analysis',
      'Tornado diagram generation',
      'Inflection point detection',
      'Factor importance ranking',
      'Marginal impact calculation'
    ],
    dataSchema: {
      sensitivity_matrix: 'number[][]',
      factor_importance: 'FactorImportance[]',
      inflection_points: 'InflectionPoint[]',
      marginal_impacts: 'MarginalImpact[]'
    }
  },
  cohort_comparison: {
    type: 'cohort_comparison',
    category: 'analysis',
    title: 'Cohort Comparison',
    subtitle: 'Historical benchmarking',
    icon: GitMerge,
    color: '#3FB950',
    description: 'Compares current predictions against historical cohorts. Shows how the current batch ranks against W15, W18, W21 etc. Provides relative percentile rankings.',
    inputs: ['Current batch', 'Comparison cohorts', 'Metrics'],
    outputs: ['Relative rankings', 'Percentiles', 'Trend analysis'],
    capabilities: [
      'Cross-batch comparison',
      'Percentile ranking within cohorts',
      'Trend detection across vintages',
      'Sector-specific benchmarking',
      'Temporal pattern analysis'
    ],
    dataSchema: {
      percentile_rank: 'number',
      cohort_comparison: 'CohortComparison[]',
      trend_direction: 'up | down | stable',
      notable_patterns: 'string[]'
    }
  },
  risk_decomposition: {
    type: 'risk_decomposition',
    category: 'analysis',
    title: 'Risk Decomposition',
    subtitle: 'Failure mode analysis',
    icon: Shield,
    color: '#E5534B',
    description: 'Breaks down the failure probability into specific risk categories: team risk, market risk, execution risk, competitive risk, timing risk. Identifies mitigation strategies.',
    inputs: ['Prediction data', 'Risk categories', 'Mitigation options'],
    outputs: ['Risk waterfall', 'Mitigation paths', 'Residual risk'],
    capabilities: [
      'Risk category decomposition',
      'Failure mode identification',
      'Mitigation strategy mapping',
      'Residual risk calculation',
      'Risk-adjusted return computation'
    ],
    dataSchema: {
      risk_breakdown: 'RiskBreakdown',
      failure_modes: 'FailureMode[]',
      mitigations: 'Mitigation[]',
      residual_risk: 'number',
      risk_adjusted_return: 'number'
    }
  },
  market_timing: {
    type: 'market_timing',
    category: 'analysis',
    title: 'Market Timing',
    subtitle: 'Cycle analysis',
    icon: Timer,
    color: '#D4A72C',
    description: 'Analyzes where we are in the market cycle and how it affects outcomes. Considers funding environment, sector momentum, and macro conditions. Outputs timing multiplier.',
    inputs: ['Sector', 'Current date', 'Macro indicators'],
    outputs: ['Cycle phase', 'Timing score', 'Optimal windows'],
    capabilities: [
      'Market cycle phase detection',
      'Sector momentum analysis',
      'Macro condition assessment',
      'Optimal entry/exit window identification',
      'Timing multiplier calculation'
    ],
    dataSchema: {
      cycle_phase: 'nascent | emerging | growth | mature | declining',
      timing_score: 'number',
      optimal_entry: 'DateRange',
      optimal_exit: 'DateRange',
      macro_sentiment: 'number'
    }
  },
  competitive_dynamics: {
    type: 'competitive_dynamics',
    category: 'analysis',
    title: 'Competitive Dynamics',
    subtitle: 'Market structure analysis',
    icon: Target,
    color: '#F0883E',
    description: 'Analyzes market structure: winner-take-all vs fragmented, network effects, switching costs, and competitive moats. Determines defensibility score.',
    inputs: ['Market data', 'Competitor list', 'Product features'],
    outputs: ['Market structure', 'Defensibility', 'Competitive position'],
    capabilities: [
      'Winner-take-all analysis',
      'Network effect quantification',
      'Switching cost estimation',
      'Moat assessment',
      'Competitive positioning map'
    ],
    dataSchema: {
      market_structure: 'winner_take_all | fragmented | oligopoly',
      defensibility_score: 'number',
      network_effects: 'number',
      switching_costs: 'number',
      competitive_position: 'Position'
    }
  },
  portfolio_optimizer: {
    type: 'portfolio_optimizer',
    category: 'analysis',
    title: 'Portfolio Optimizer',
    subtitle: 'Allocation optimization',
    icon: PieChart,
    color: '#A371F7',
    description: 'Applies Markowitz-style portfolio theory to startup investments. Optimizes allocation across companies considering correlation, diversification, and risk-adjusted returns.',
    inputs: ['Company predictions', 'Correlation matrix', 'Risk tolerance'],
    outputs: ['Optimal allocation', 'Efficient frontier', 'Portfolio metrics'],
    capabilities: [
      'Mean-variance optimization',
      'Efficient frontier computation',
      'Correlation-aware allocation',
      'Risk-adjusted return maximization',
      'Diversification scoring'
    ],
    dataSchema: {
      optimal_weights: 'Record<string, number>',
      expected_return: 'number',
      portfolio_risk: 'number',
      sharpe_ratio: 'number',
      diversification_score: 'number'
    }
  },
  scenario_planner: {
    type: 'scenario_planner',
    category: 'analysis',
    title: 'Scenario Planner',
    subtitle: 'Bull/Base/Bear modeling',
    icon: GitBranch,
    color: '#5E6AD2',
    description: 'Creates structured scenarios: Bull (top 25%), Base (median), Bear (bottom 25%). Models different future paths with explicit assumptions and probability weights.',
    inputs: ['Prediction distribution', 'Key assumptions', 'Scenario weights'],
    outputs: ['Scenario tree', 'Weighted outcomes', 'Decision points'],
    capabilities: [
      'Three-scenario framework (Bull/Base/Bear)',
      'Assumption documentation',
      'Probability-weighted outcomes',
      'Decision tree generation',
      'Contingency planning'
    ],
    dataSchema: {
      bull_case: 'Scenario',
      base_case: 'Scenario',
      bear_case: 'Scenario',
      weighted_outcome: 'number',
      key_assumptions: 'Assumption[]'
    }
  },

  // ==========================================================================
  // SIMULATION NODES
  // ==========================================================================
  trajectory_sim: {
    type: 'trajectory_sim',
    category: 'simulation',
    title: 'Trajectory Simulation',
    subtitle: '7-year growth modeling',
    icon: LineChart,
    color: '#3FB950',
    description: 'Simulates company growth trajectories over 7 years. Models stage transitions, revenue growth, team scaling, and valuation milestones with stochastic dynamics.',
    inputs: ['Initial state', 'Growth parameters', 'Milestone triggers'],
    outputs: ['Growth curves', 'Milestone probabilities', 'Exit timing'],
    capabilities: [
      'Stage-by-stage progression modeling',
      'Revenue growth simulation',
      'Team scaling dynamics',
      'Valuation milestone tracking',
      'Exit timing distribution'
    ],
    dataSchema: {
      growth_curves: 'GrowthCurve[]',
      milestone_probs: 'MilestoneProb[]',
      exit_timing: 'Distribution',
      stage_transitions: 'Transition[]'
    }
  },
  exit_modeler: {
    type: 'exit_modeler',
    category: 'simulation',
    title: 'Exit Modeler',
    subtitle: 'Exit path simulation',
    icon: ArrowUpRight,
    color: '#A371F7',
    description: 'Models exit paths: IPO, strategic acquisition, acqui-hire, or failure. Considers market conditions, company trajectory, and acquirer landscape.',
    inputs: ['Company trajectory', 'Market conditions', 'Acquirer landscape'],
    outputs: ['Exit probabilities', 'Expected returns', 'Timing distribution'],
    capabilities: [
      'Exit type probability estimation',
      'Valuation at exit modeling',
      'Acquirer landscape mapping',
      'IPO vs acquisition analysis',
      'Return multiple calculation'
    ],
    dataSchema: {
      ipo_probability: 'number',
      acquisition_probability: 'number',
      failure_probability: 'number',
      expected_multiple: 'number',
      exit_timing: 'Distribution'
    }
  },
  funding_scenarios: {
    type: 'funding_scenarios',
    category: 'simulation',
    title: 'Funding Scenarios',
    subtitle: 'Future round modeling',
    icon: DollarSign,
    color: '#D4A72C',
    description: 'Models future funding rounds, dilution, and cap table evolution. Projects round timing, size, and valuation step-ups based on growth trajectory.',
    inputs: ['Current cap table', 'Growth projection', 'Market conditions'],
    outputs: ['Future rounds', 'Dilution schedule', 'Ownership evolution'],
    capabilities: [
      'Future round timing estimation',
      'Round size projection',
      'Dilution calculation',
      'Ownership evolution tracking',
      'Employee pool modeling'
    ],
    dataSchema: {
      future_rounds: 'FundingRound[]',
      dilution_schedule: 'number[]',
      ownership_evolution: 'Ownership[]',
      pro_forma_cap_table: 'CapTable'
    }
  },

  // ==========================================================================
  // OUTPUT NODES
  // ==========================================================================
  chat: {
    type: 'chat',
    category: 'output',
    title: 'Interactive Chat',
    subtitle: 'AI-powered Q&A',
    icon: MessageSquare,
    color: '#3FB950',
    description: 'Conversational interface for exploring predictions. Ask questions about specific factors, compare companies, drill into reasoning, and explore what-if scenarios.',
    inputs: ['Prediction context', 'User query', 'Conversation history'],
    outputs: ['AI response', 'Supporting data', 'Follow-up suggestions'],
    capabilities: [
      'Natural language querying',
      'Factor-specific deep dives',
      'Cross-company comparison',
      'What-if exploration',
      'Reasoning explanation'
    ],
    dataSchema: {
      conversation: 'Message[]',
      context: 'PredictionContext',
      suggestions: 'string[]'
    }
  },
  decision_brief: {
    type: 'decision_brief',
    category: 'output',
    title: 'Decision Brief',
    subtitle: 'One-page executive summary',
    icon: FileText,
    color: '#5E6AD2',
    description: 'Generates a one-page decision brief with key metrics, recommendation, and supporting rationale. Designed for quick partner review and investment committee.',
    inputs: ['Full prediction', 'Company data', 'Comparison data'],
    outputs: ['PDF document', 'Key metrics', 'Recommendation'],
    capabilities: [
      'One-page summary generation',
      'Key metric extraction',
      'Clear recommendation with rationale',
      'Risk highlight section',
      'PDF export'
    ],
    dataSchema: {
      summary: 'string',
      key_metrics: 'Metric[]',
      recommendation: 'invest | pass | monitor',
      confidence: 'number',
      key_risks: 'string[]'
    }
  },
  investment_memo: {
    type: 'investment_memo',
    category: 'output',
    title: 'Investment Memo',
    subtitle: 'Full thesis document',
    icon: FileBarChart,
    color: '#58A6FF',
    description: 'Generates a complete investment memo with market analysis, competitive positioning, team assessment, financial projections, and risk analysis.',
    inputs: ['All analysis outputs', 'Investment thesis', 'Deal terms'],
    outputs: ['Full memo', 'Appendix data', 'Model outputs'],
    capabilities: [
      'Multi-section memo generation',
      'Market sizing documentation',
      'Competitive analysis writeup',
      'Financial model integration',
      'Risk/return summary'
    ],
    dataSchema: {
      sections: 'MemoSection[]',
      appendix: 'AppendixData',
      financial_model: 'FinancialModel',
      recommendation: 'Recommendation'
    }
  },
  risk_report: {
    type: 'risk_report',
    category: 'output',
    title: 'Risk Report',
    subtitle: 'Detailed risk assessment',
    icon: AlertTriangle,
    color: '#E5534B',
    description: 'Comprehensive risk report covering all identified risks, probability assessments, impact estimates, and mitigation strategies.',
    inputs: ['Risk decomposition', 'Mitigation data', 'Historical comps'],
    outputs: ['Risk matrix', 'Mitigation plan', 'Monitoring triggers'],
    capabilities: [
      'Risk matrix visualization',
      'Probability x Impact scoring',
      'Mitigation strategy mapping',
      'Monitoring trigger definition',
      'Risk evolution tracking'
    ],
    dataSchema: {
      risk_matrix: 'RiskMatrix',
      mitigation_plan: 'MitigationPlan',
      monitoring_triggers: 'Trigger[]',
      residual_risks: 'Risk[]'
    }
  },
  portfolio_dashboard: {
    type: 'portfolio_dashboard',
    category: 'output',
    title: 'Portfolio Dashboard',
    subtitle: 'Real-time monitoring',
    icon: BarChart3,
    color: '#A371F7',
    description: 'Live dashboard for monitoring portfolio-level metrics. Tracks aggregate predictions, alerts on changes, and visualizes portfolio composition.',
    inputs: ['All company predictions', 'Portfolio allocation', 'Alert rules'],
    outputs: ['Dashboard view', 'Alerts', 'Trend charts'],
    capabilities: [
      'Real-time metric aggregation',
      'Portfolio composition visualization',
      'Alert generation on changes',
      'Trend tracking over time',
      'Drill-down to company level'
    ],
    dataSchema: {
      portfolio_metrics: 'PortfolioMetrics',
      company_list: 'CompanySummary[]',
      active_alerts: 'Alert[]',
      trends: 'TrendData[]'
    }
  },
  comparison_matrix: {
    type: 'comparison_matrix',
    category: 'output',
    title: 'Comparison Matrix',
    subtitle: 'Side-by-side analysis',
    icon: Scale,
    color: '#D4A72C',
    description: 'Side-by-side comparison of multiple companies across all factors. Enables quick relative assessment and ranking.',
    inputs: ['Company list', 'Comparison metrics', 'Weighting'],
    outputs: ['Comparison table', 'Rankings', 'Differentiators'],
    capabilities: [
      'Multi-company comparison',
      'Factor-by-factor breakdown',
      'Weighted ranking',
      'Key differentiator identification',
      'Export to spreadsheet'
    ],
    dataSchema: {
      comparison_table: 'ComparisonRow[]',
      rankings: 'Ranking[]',
      key_differentiators: 'Differentiator[]'
    }
  },
  alert_system: {
    type: 'alert_system',
    category: 'output',
    title: 'Alert System',
    subtitle: 'Trigger-based notifications',
    icon: Bell,
    color: '#F0883E',
    description: 'Configurable alert system that monitors conditions and triggers notifications. Watch for funding announcements, score changes, or market shifts.',
    inputs: ['Watch conditions', 'Notification channels', 'Thresholds'],
    outputs: ['Active alerts', 'Notification history', 'Condition status'],
    capabilities: [
      'Condition-based alerting',
      'Multi-channel notification (email, Slack, webhook)',
      'Threshold configuration',
      'Alert history tracking',
      'Escalation rules'
    ],
    dataSchema: {
      watch_conditions: 'WatchCondition[]',
      active_alerts: 'Alert[]',
      notification_history: 'Notification[]'
    }
  },
  stakeholder_views: {
    type: 'stakeholder_views',
    category: 'output',
    title: 'Stakeholder Views',
    subtitle: 'Role-based dashboards',
    icon: Users,
    color: '#8B8B8D',
    description: 'Tailored views for different stakeholders: CEO (strategic), CFO (financial), CTO (technical), Board (governance), Team (execution).',
    inputs: ['Full analysis', 'Stakeholder role', 'Focus areas'],
    outputs: ['Tailored view', 'Key metrics', 'Action items'],
    capabilities: [
      'Role-specific metric selection',
      'Focus area prioritization',
      'Action item generation',
      'Risk/opportunity framing',
      'Communication templates'
    ],
    dataSchema: {
      stakeholder_type: 'ceo | cfo | cto | board | team',
      key_metrics: 'Metric[]',
      focus_areas: 'FocusArea[]',
      action_items: 'ActionItem[]'
    }
  },
  whatif_explorer: {
    type: 'whatif_explorer',
    category: 'output',
    title: 'What-If Explorer',
    subtitle: 'Interactive sensitivity',
    icon: Gauge,
    color: '#3FB950',
    description: 'Interactive interface with sliders for each factor. See real-time probability updates as you adjust inputs. Explore how different scenarios affect outcomes.',
    inputs: ['Base prediction', 'Factor ranges', 'Constraints'],
    outputs: ['Live probability', 'Factor impacts', 'Scenario comparison'],
    capabilities: [
      'Real-time probability recalculation',
      'Interactive factor sliders',
      'Scenario save/compare',
      'Constraint enforcement',
      'Impact visualization'
    ],
    dataSchema: {
      current_factors: 'FactorValues',
      live_probability: 'number',
      saved_scenarios: 'Scenario[]',
      impact_visualization: 'ImpactViz'
    }
  },
  timeline_projection: {
    type: 'timeline_projection',
    category: 'output',
    title: 'Timeline Projection',
    subtitle: 'Milestone visualization',
    icon: Calendar,
    color: '#5E6AD2',
    description: 'Visual timeline of projected milestones: funding rounds, product launches, team growth, and potential exit events. Gantt-style visualization with probability overlays.',
    inputs: ['Trajectory simulation', 'Milestone definitions', 'Time horizon'],
    outputs: ['Timeline view', 'Milestone probabilities', 'Critical path'],
    capabilities: [
      'Gantt-style timeline visualization',
      'Milestone probability overlay',
      'Critical path identification',
      'Dependency mapping',
      'Scenario timeline comparison'
    ],
    dataSchema: {
      milestones: 'Milestone[]',
      timeline_view: 'TimelineView',
      critical_path: 'Path',
      dependencies: 'Dependency[]'
    }
  },
}

// =============================================================================
// DESIGN SYSTEM
// =============================================================================

const colors = {
  bg: '#0A0A0B',
  bgSecondary: '#111113',
  bgTertiary: '#18181B',
  bgElevated: '#1C1C1F',
  accent: '#5E6AD2',
  accentMuted: '#5E6AD220',
  accentHover: '#7C85E0',
  accentSubtle: '#5E6AD215',
  textPrimary: '#EDEDEF',
  textSecondary: '#8B8B8D',
  textMuted: '#5C5C5E',
  textFaint: '#3F3F42',
  border: '#1F1F22',
  borderSubtle: '#18181B',
  borderHover: '#2A2A2E',
  success: '#3FB950',
  successMuted: '#3FB95020',
  warning: '#D4A72C',
  warningMuted: '#D4A72C20',
  error: '#E5534B',
  errorMuted: '#E5534B20',
  unicorn: '#A371F7',
  unicornMuted: '#A371F720',
}

const categoryColors: Record<NodeCategory, string> = {
  input: '#F0883E',
  analysis: '#5E6AD2',
  simulation: '#3FB950',
  output: '#A371F7',
}

// =============================================================================
// TYPES
// =============================================================================

interface Node {
  id: string
  type: NodeType
  x: number
  y: number
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
  source_count?: number
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
// API
// =============================================================================

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://api-production-9cbf.up.railway.app'

const api = {
  analyzeYCBatch: async (batchCode: string, maxCompanies = 8) => {
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

  getMethodology: async () => {
    const res = await fetch(`${API_URL}/api/startups/methodology`)
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
  const config = NODE_CONFIGS[node.type]
  const Icon = config.icon
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
            ? `0 0 0 1px ${config.color}, 0 8px 24px -8px rgba(0,0,0,0.5)`
            : isHovered
              ? '0 4px 16px -4px rgba(0,0,0,0.4)'
              : '0 2px 8px -2px rgba(0,0,0,0.3)'
        }}
        transition={{ duration: 0.15, ease: 'easeOut' }}
        className="w-[200px] rounded-lg overflow-hidden"
        style={{
          background: colors.bgElevated,
          border: `1px solid ${selected ? config.color : isHovered ? colors.borderHover : colors.border}`,
        }}
      >
        {/* Node header */}
        <div
          className="px-3 py-2.5 flex items-center gap-2.5"
          style={{ borderBottom: `1px solid ${colors.border}` }}
        >
          <div
            className="w-5 h-5 rounded flex items-center justify-center flex-shrink-0"
            style={{ background: `${config.color}15` }}
          >
            <Icon size={12} style={{ color: config.color }} strokeWidth={2} />
          </div>
          <span
            className="text-[10px] font-medium uppercase tracking-[0.5px]"
            style={{ color: colors.textMuted }}
          >
            {config.category}
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
            {config.title}
          </h3>
          <p
            className="text-[11px] mt-1 leading-relaxed"
            style={{ color: colors.textSecondary }}
          >
            {config.subtitle}
          </p>
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

function NodeDetailPanel({ nodeType, onClose }: { nodeType: NodeType, onClose: () => void }) {
  const config = NODE_CONFIGS[nodeType]
  const Icon = config.icon

  return (
    <motion.div
      initial={{ x: 400, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      exit={{ x: 400, opacity: 0 }}
      transition={{ duration: 0.25, ease: [0.16, 1, 0.3, 1] }}
      className="w-[400px] flex flex-col z-20 flex-shrink-0"
      style={{
        background: colors.bgSecondary,
        borderLeft: `1px solid ${colors.border}`
      }}
    >
      {/* Header */}
      <div
        className="h-12 flex items-center justify-between px-4 flex-shrink-0"
        style={{ borderBottom: `1px solid ${colors.border}` }}
      >
        <div className="flex items-center gap-3">
          <div
            className="w-7 h-7 rounded-md flex items-center justify-center"
            style={{ background: `${config.color}15` }}
          >
            <Icon size={14} style={{ color: config.color }} />
          </div>
          <div>
            <h2 className="text-[13px] font-medium" style={{ color: colors.textPrimary }}>
              {config.title}
            </h2>
            <span className="text-[10px] uppercase tracking-wide" style={{ color: colors.textMuted }}>
              {config.category} node
            </span>
          </div>
        </div>
        <button
          onClick={onClose}
          className="p-1.5 rounded transition-colors duration-150"
          style={{ color: colors.textMuted }}
          onMouseEnter={(e) => e.currentTarget.style.background = colors.bgTertiary}
          onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
        >
          <X size={14} />
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto p-4 space-y-5">
        {/* Description */}
        <div>
          <h3 className="text-[10px] font-medium uppercase tracking-wide mb-2" style={{ color: colors.textMuted }}>
            Description
          </h3>
          <p className="text-[13px] leading-relaxed" style={{ color: colors.textSecondary }}>
            {config.description}
          </p>
        </div>

        {/* Capabilities */}
        <div>
          <h3 className="text-[10px] font-medium uppercase tracking-wide mb-2" style={{ color: colors.textMuted }}>
            Capabilities
          </h3>
          <div className="space-y-1.5">
            {config.capabilities.map((cap, i) => (
              <div key={i} className="flex items-start gap-2">
                <CheckCircle size={12} style={{ color: colors.success, marginTop: 2, flexShrink: 0 }} />
                <span className="text-[12px]" style={{ color: colors.textSecondary }}>{cap}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Inputs */}
        <div>
          <h3 className="text-[10px] font-medium uppercase tracking-wide mb-2" style={{ color: colors.textMuted }}>
            Inputs
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {config.inputs.map((input, i) => (
              <span
                key={i}
                className="px-2 py-1 rounded text-[11px]"
                style={{ background: colors.bgTertiary, color: colors.textSecondary }}
              >
                {input}
              </span>
            ))}
          </div>
        </div>

        {/* Outputs */}
        <div>
          <h3 className="text-[10px] font-medium uppercase tracking-wide mb-2" style={{ color: colors.textMuted }}>
            Outputs
          </h3>
          <div className="flex flex-wrap gap-1.5">
            {config.outputs.map((output, i) => (
              <span
                key={i}
                className="px-2 py-1 rounded text-[11px]"
                style={{ background: `${config.color}15`, color: config.color }}
              >
                {output}
              </span>
            ))}
          </div>
        </div>

        {/* Data Schema */}
        <div>
          <h3 className="text-[10px] font-medium uppercase tracking-wide mb-2" style={{ color: colors.textMuted }}>
            Data Schema
          </h3>
          <div
            className="rounded-md p-3 font-mono text-[11px] space-y-1"
            style={{ background: colors.bgTertiary }}
          >
            {Object.entries(config.dataSchema).map(([key, type]) => (
              <div key={key} className="flex">
                <span style={{ color: colors.accent }}>{key}</span>
                <span style={{ color: colors.textMuted }}>: </span>
                <span style={{ color: colors.textSecondary }}>{type}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Integration Info */}
        <div
          className="p-3 rounded-lg"
          style={{ background: colors.accentSubtle, border: `1px solid ${colors.accent}30` }}
        >
          <div className="flex items-center gap-2 mb-2">
            <Info size={12} style={{ color: colors.accent }} />
            <span className="text-[10px] font-medium uppercase tracking-wide" style={{ color: colors.accent }}>
              Integration
            </span>
          </div>
          <p className="text-[11px] leading-relaxed" style={{ color: colors.textSecondary }}>
            Connect this node to other nodes by dragging from the output port (right) to an input port (left).
            Data flows through connections automatically when the upstream node completes.
          </p>
        </div>
      </div>
    </motion.div>
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
            { label: 'T', value: prediction.team_score },
            { label: 'M', value: prediction.market_score },
            { label: 'Tr', value: prediction.traction_score },
            { label: 'Ti', value: prediction.timing_score },
            { label: 'C', value: prediction.capital_score },
          ].map(({ label, value }) => (
            <div key={label} className="flex-1">
              <div className="h-1 rounded-full overflow-hidden" style={{ background: colors.border }}>
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
    </motion.div>
  )
}

function KbdHint({ children }: { children: React.ReactNode }) {
  return (
    <kbd
      className="inline-flex items-center justify-center px-1.5 py-0.5 rounded text-[10px] font-medium"
      style={{ background: colors.bgTertiary, color: colors.textMuted, border: `1px solid ${colors.border}` }}
    >
      {children}
    </kbd>
  )
}

// =============================================================================
// MAIN PAGE
// =============================================================================

export default function CanvasPage() {
  // Canvas state - Full node architecture
  const [nodes, setNodes] = useState<Node[]>([
    // Data Input Row (y: 50-150)
    { id: 'batch', type: 'batch', x: 50, y: 100, status: 'idle' },
    { id: 'research', type: 'research', x: 300, y: 50, status: 'idle' },
    { id: 'market_scanner', type: 'market_scanner', x: 300, y: 180, status: 'idle' },
    { id: 'alternative_data', type: 'alternative_data', x: 550, y: 50, status: 'idle' },
    { id: 'network_graph', type: 'network_graph', x: 550, y: 180, status: 'idle' },
    { id: 'financial_signals', type: 'financial_signals', x: 550, y: 310, status: 'idle' },
    { id: 'historical_outcomes', type: 'historical_outcomes', x: 300, y: 310, status: 'idle' },

    // Analysis Row (y: 450-600)
    { id: 'prediction', type: 'prediction', x: 50, y: 480, status: 'idle' },
    { id: 'monte_carlo', type: 'monte_carlo', x: 300, y: 430, status: 'idle' },
    { id: 'sensitivity', type: 'sensitivity', x: 300, y: 560, status: 'idle' },
    { id: 'cohort_comparison', type: 'cohort_comparison', x: 550, y: 430, status: 'idle' },
    { id: 'risk_decomposition', type: 'risk_decomposition', x: 550, y: 560, status: 'idle' },
    { id: 'market_timing', type: 'market_timing', x: 800, y: 430, status: 'idle' },
    { id: 'competitive_dynamics', type: 'competitive_dynamics', x: 800, y: 560, status: 'idle' },
    { id: 'portfolio_optimizer', type: 'portfolio_optimizer', x: 1050, y: 480, status: 'idle' },
    { id: 'scenario_planner', type: 'scenario_planner', x: 1050, y: 610, status: 'idle' },

    // Simulation Row (y: 800)
    { id: 'trajectory_sim', type: 'trajectory_sim', x: 300, y: 780, status: 'idle' },
    { id: 'exit_modeler', type: 'exit_modeler', x: 550, y: 780, status: 'idle' },
    { id: 'funding_scenarios', type: 'funding_scenarios', x: 800, y: 780, status: 'idle' },

    // Output Row (y: 980)
    { id: 'chat', type: 'chat', x: 50, y: 980, status: 'idle' },
    { id: 'decision_brief', type: 'decision_brief', x: 300, y: 930, status: 'idle' },
    { id: 'investment_memo', type: 'investment_memo', x: 300, y: 1060, status: 'idle' },
    { id: 'risk_report', type: 'risk_report', x: 550, y: 930, status: 'idle' },
    { id: 'comparison_matrix', type: 'comparison_matrix', x: 550, y: 1060, status: 'idle' },
    { id: 'portfolio_dashboard', type: 'portfolio_dashboard', x: 800, y: 930, status: 'idle' },
    { id: 'alert_system', type: 'alert_system', x: 800, y: 1060, status: 'idle' },
    { id: 'stakeholder_views', type: 'stakeholder_views', x: 1050, y: 930, status: 'idle' },
    { id: 'whatif_explorer', type: 'whatif_explorer', x: 1050, y: 1060, status: 'idle' },
    { id: 'timeline_projection', type: 'timeline_projection', x: 1300, y: 980, status: 'idle' },
  ])

  const [edges] = useState<Edge[]>([
    // Input connections
    { id: 'e1', from: 'batch', to: 'research' },
    { id: 'e2', from: 'batch', to: 'market_scanner' },
    { id: 'e3', from: 'research', to: 'alternative_data' },
    { id: 'e4', from: 'research', to: 'network_graph' },
    { id: 'e5', from: 'market_scanner', to: 'financial_signals' },
    { id: 'e6', from: 'market_scanner', to: 'historical_outcomes' },

    // Input to Analysis
    { id: 'e7', from: 'alternative_data', to: 'prediction' },
    { id: 'e8', from: 'network_graph', to: 'prediction' },
    { id: 'e9', from: 'financial_signals', to: 'prediction' },
    { id: 'e10', from: 'historical_outcomes', to: 'prediction' },

    // Analysis connections
    { id: 'e11', from: 'prediction', to: 'monte_carlo' },
    { id: 'e12', from: 'prediction', to: 'sensitivity' },
    { id: 'e13', from: 'monte_carlo', to: 'cohort_comparison' },
    { id: 'e14', from: 'monte_carlo', to: 'risk_decomposition' },
    { id: 'e15', from: 'sensitivity', to: 'market_timing' },
    { id: 'e16', from: 'cohort_comparison', to: 'market_timing' },
    { id: 'e17', from: 'risk_decomposition', to: 'competitive_dynamics' },
    { id: 'e18', from: 'market_timing', to: 'portfolio_optimizer' },
    { id: 'e19', from: 'competitive_dynamics', to: 'portfolio_optimizer' },
    { id: 'e20', from: 'portfolio_optimizer', to: 'scenario_planner' },

    // Analysis to Simulation
    { id: 'e21', from: 'scenario_planner', to: 'trajectory_sim' },
    { id: 'e22', from: 'portfolio_optimizer', to: 'trajectory_sim' },
    { id: 'e23', from: 'trajectory_sim', to: 'exit_modeler' },
    { id: 'e24', from: 'exit_modeler', to: 'funding_scenarios' },

    // To Outputs
    { id: 'e25', from: 'prediction', to: 'chat', animated: true },
    { id: 'e26', from: 'scenario_planner', to: 'decision_brief' },
    { id: 'e27', from: 'portfolio_optimizer', to: 'investment_memo' },
    { id: 'e28', from: 'risk_decomposition', to: 'risk_report' },
    { id: 'e29', from: 'cohort_comparison', to: 'comparison_matrix' },
    { id: 'e30', from: 'portfolio_optimizer', to: 'portfolio_dashboard' },
    { id: 'e31', from: 'market_scanner', to: 'alert_system' },
    { id: 'e32', from: 'scenario_planner', to: 'stakeholder_views' },
    { id: 'e33', from: 'sensitivity', to: 'whatif_explorer' },
    { id: 'e34', from: 'trajectory_sim', to: 'timeline_projection' },
  ])

  const [selectedNode, setSelectedNode] = useState<string | null>(null)
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 0.7 })
  const [isPanning, setIsPanning] = useState(false)
  const panStart = useRef({ x: 0, y: 0, transformX: 0, transformY: 0 })
  const canvasRef = useRef<HTMLDivElement>(null)

  // Data state
  const [isResearching, setIsResearching] = useState(false)
  const [batchPrediction, setBatchPrediction] = useState<BatchPrediction | null>(null)
  const [selectedStartup, setSelectedStartup] = useState<StartupPrediction | null>(null)
  const [showResults, setShowResults] = useState(false)
  const [batchCode, setBatchCode] = useState('W24')

  // Chat state
  const [chatMessages, setChatMessages] = useState<Array<{ role: string, content: string }>>([])
  const [chatInput, setChatInput] = useState('')
  const [isChatting, setIsChatting] = useState(false)
  const [showChat, setShowChat] = useState(false)

  // UI state
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [spaceHeld, setSpaceHeld] = useState(false)
  const [showNodeDetail, setShowNodeDetail] = useState(false)

  // Keyboard handlers
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.code === 'Space' && !e.repeat) {
        e.preventDefault()
        setSpaceHeld(true)
      }
    }
    const handleKeyUp = (e: KeyboardEvent) => {
      if (e.code === 'Space') setSpaceHeld(false)
    }
    window.addEventListener('keydown', handleKeyDown)
    window.addEventListener('keyup', handleKeyUp)
    return () => {
      window.removeEventListener('keydown', handleKeyDown)
      window.removeEventListener('keyup', handleKeyUp)
    }
  }, [])

  // Canvas interactions
  const handleWheel = useCallback((e: React.WheelEvent) => {
    e.preventDefault()
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
      setTransform(prev => ({ ...prev, x: prev.x - e.deltaX, y: prev.y - e.deltaY }))
    }
  }, [transform])

  const handleCanvasMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button === 1 || (e.button === 0 && spaceHeld) || (e.button === 0 && e.altKey)) {
      e.preventDefault()
      setIsPanning(true)
      panStart.current = { x: e.clientX, y: e.clientY, transformX: transform.x, transformY: transform.y }
    } else if (e.button === 0 && e.target === e.currentTarget) {
      setSelectedNode(null)
      setShowNodeDetail(false)
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

  const handleNodeSelect = (id: string) => {
    setSelectedNode(id)
    setShowNodeDetail(true)
  }

  // Run batch analysis
  const runBatchAnalysis = async () => {
    setIsResearching(true)
    setShowResults(false)
    setBatchPrediction(null)

    // Update node statuses
    const inputNodes = ['batch', 'research', 'market_scanner', 'alternative_data', 'network_graph', 'financial_signals', 'historical_outcomes']
    const analysisNodes = ['prediction', 'monte_carlo', 'sensitivity', 'cohort_comparison', 'risk_decomposition', 'market_timing', 'competitive_dynamics', 'portfolio_optimizer', 'scenario_planner']
    const simulationNodes = ['trajectory_sim', 'exit_modeler', 'funding_scenarios']
    const outputNodes = ['chat', 'decision_brief', 'investment_memo', 'risk_report', 'comparison_matrix', 'portfolio_dashboard', 'alert_system', 'stakeholder_views', 'whatif_explorer', 'timeline_projection']

    // Animate through stages
    setNodes(prev => prev.map(n => inputNodes.includes(n.id) ? { ...n, status: 'running' } : n))

    try {
      const result = await api.analyzeYCBatch(batchCode, 8)

      // Complete input nodes
      setNodes(prev => prev.map(n => inputNodes.includes(n.id) ? { ...n, status: 'complete' } : n))

      // Run analysis nodes
      setNodes(prev => prev.map(n => analysisNodes.includes(n.id) ? { ...n, status: 'running' } : n))
      await new Promise(r => setTimeout(r, 500))
      setNodes(prev => prev.map(n => analysisNodes.includes(n.id) ? { ...n, status: 'complete' } : n))

      // Run simulation nodes
      setNodes(prev => prev.map(n => simulationNodes.includes(n.id) ? { ...n, status: 'running' } : n))
      await new Promise(r => setTimeout(r, 300))
      setNodes(prev => prev.map(n => simulationNodes.includes(n.id) ? { ...n, status: 'complete' } : n))

      // Complete output nodes
      setNodes(prev => prev.map(n => outputNodes.includes(n.id) ? { ...n, status: 'complete' } : n))

      setBatchPrediction(result)
      setShowResults(true)

    } catch (error) {
      console.error('Batch analysis failed:', error)
      setNodes(prev => prev.map(n => ({ ...n, status: 'error' })))
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
      setChatMessages(prev => [...prev, { role: 'assistant', content: 'Sorry, I encountered an error.' }])
    }

    setIsChatting(false)
  }

  const openStartupChat = (prediction: StartupPrediction) => {
    setSelectedStartup(prediction)
    setChatMessages([])
    setShowChat(true)
  }

  const selectedNodeConfig = selectedNode ? NODE_CONFIGS[nodes.find(n => n.id === selectedNode)?.type || 'batch'] : null

  return (
    <div
      className="h-screen w-screen overflow-hidden flex antialiased"
      style={{ background: colors.bg, fontFamily: 'Inter, -apple-system, sans-serif' }}
    >
      {/* Sidebar */}
      <motion.aside
        initial={false}
        animate={{ width: sidebarCollapsed ? 48 : 200 }}
        transition={{ duration: 0.2, ease: [0.16, 1, 0.3, 1] }}
        className="h-full flex flex-col z-20 flex-shrink-0"
        style={{ background: colors.bgSecondary, borderRight: `1px solid ${colors.border}` }}
      >
        {/* Logo */}
        <div className="h-11 flex items-center px-3 gap-2.5" style={{ borderBottom: `1px solid ${colors.border}` }}>
          <div
            className="w-6 h-6 rounded flex items-center justify-center flex-shrink-0"
            style={{ background: `linear-gradient(135deg, ${colors.accent} 0%, #7C3AED 100%)` }}
          >
            <Zap size={13} className="text-white" strokeWidth={2.5} />
          </div>
          {!sidebarCollapsed && (
            <span className="text-[13px] font-semibold" style={{ color: colors.textPrimary }}>Populous</span>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-2 px-2 space-y-0.5">
          <Link
            href="/projects"
            className="flex items-center gap-2.5 px-2 py-1.5 rounded-md transition-colors"
            style={{ color: colors.textSecondary }}
          >
            <FolderOpen size={15} strokeWidth={1.75} />
            {!sidebarCollapsed && <span className="text-[13px] font-medium">Projects</span>}
          </Link>
          <Link
            href="/audiences"
            className="flex items-center gap-2.5 px-2 py-1.5 rounded-md transition-colors"
            style={{ color: colors.textSecondary }}
          >
            <Users size={15} strokeWidth={1.75} />
            {!sidebarCollapsed && <span className="text-[13px] font-medium">Audiences</span>}
          </Link>

          {!sidebarCollapsed && (
            <>
              <div className="h-px my-3 mx-1" style={{ background: colors.border }} />
              <div className="px-2 mb-2">
                <span className="text-[10px] font-medium uppercase tracking-wide" style={{ color: colors.textMuted }}>
                  YC Batch
                </span>
              </div>
              <div className="px-1">
                <select
                  value={batchCode}
                  onChange={(e) => setBatchCode(e.target.value)}
                  className="w-full px-2.5 py-1.5 rounded-md text-[13px] font-medium appearance-none cursor-pointer"
                  style={{ background: colors.bgTertiary, color: colors.textPrimary, border: `1px solid ${colors.border}` }}
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

              {/* Node Legend */}
              <div className="h-px my-3 mx-1" style={{ background: colors.border }} />
              <div className="px-2 mb-2">
                <span className="text-[10px] font-medium uppercase tracking-wide" style={{ color: colors.textMuted }}>
                  Node Types
                </span>
              </div>
              <div className="px-2 space-y-1.5">
                {(['input', 'analysis', 'simulation', 'output'] as NodeCategory[]).map(cat => (
                  <div key={cat} className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full" style={{ background: categoryColors[cat] }} />
                    <span className="text-[11px] capitalize" style={{ color: colors.textSecondary }}>{cat}</span>
                  </div>
                ))}
              </div>
            </>
          )}
        </nav>

        <button
          onClick={() => setSidebarCollapsed(!sidebarCollapsed)}
          className="h-9 flex items-center justify-center transition-colors"
          style={{ borderTop: `1px solid ${colors.border}` }}
        >
          <ChevronRight
            size={14}
            style={{ color: colors.textMuted, transform: sidebarCollapsed ? 'rotate(0deg)' : 'rotate(180deg)' }}
          />
        </button>
      </motion.aside>

      {/* Main */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header
          className="h-11 flex items-center justify-between px-4 z-10 flex-shrink-0"
          style={{ background: colors.bgSecondary, borderBottom: `1px solid ${colors.border}` }}
        >
          <div className="flex items-center gap-3">
            <h1 className="text-[13px] font-medium" style={{ color: colors.textPrimary }}>
              Decision Intelligence Engine
            </h1>
            <span
              className="text-[11px] px-1.5 py-0.5 rounded font-medium"
              style={{ background: colors.bgTertiary, color: colors.textMuted }}
            >
              {Math.round(transform.scale * 100)}%
            </span>
            <span
              className="text-[10px] px-2 py-0.5 rounded-full font-medium"
              style={{ background: colors.successMuted, color: colors.success }}
            >
              {nodes.length} nodes
            </span>
          </div>

          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setTransform({ x: 0, y: 0, scale: 0.7 })}
              className="p-1.5 rounded transition-colors"
              style={{ color: colors.textMuted }}
            >
              <RotateCcw size={14} />
            </button>
            <button
              onClick={() => setTransform(prev => ({ ...prev, scale: Math.max(0.25, prev.scale - 0.1) }))}
              className="p-1.5 rounded transition-colors"
              style={{ color: colors.textMuted }}
            >
              <Minus size={14} />
            </button>
            <button
              onClick={() => setTransform(prev => ({ ...prev, scale: Math.min(2, prev.scale + 0.1) }))}
              className="p-1.5 rounded transition-colors"
              style={{ color: colors.textMuted }}
            >
              <Plus size={14} />
            </button>

            <div className="w-px h-5 mx-1" style={{ background: colors.border }} />

            <motion.button
              onClick={runBatchAnalysis}
              disabled={isResearching}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="px-3 py-1.5 rounded-md text-[12px] font-medium flex items-center gap-2 disabled:opacity-50"
              style={{
                background: `linear-gradient(180deg, ${colors.accent} 0%, #4F5BC7 100%)`,
                color: 'white',
              }}
            >
              {isResearching ? (
                <>
                  <Loader2 size={13} className="animate-spin" />
                  <span>Running Pipeline...</span>
                </>
              ) : (
                <>
                  <Play size={13} />
                  <span>Run Full Analysis</span>
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
            <svg className="absolute inset-0 pointer-events-none" style={{ width: '3000px', height: '1500px', overflow: 'visible' }}>
              {edges.map(edge => {
                const fromNode = nodes.find(n => n.id === edge.from)
                const toNode = nodes.find(n => n.id === edge.to)
                if (!fromNode || !toNode) return null
                return <CanvasEdge key={edge.id} from={{ x: fromNode.x, y: fromNode.y }} to={{ x: toNode.x, y: toNode.y }} animated={edge.animated} />
              })}
            </svg>

            {nodes.map(node => (
              <CanvasNode
                key={node.id}
                node={node}
                selected={selectedNode === node.id}
                onSelect={handleNodeSelect}
                onDrag={handleDrag}
                transform={transform}
              />
            ))}
          </div>

          {/* Controls hint */}
          <div
            className="absolute bottom-4 left-4 px-3 py-2 rounded-lg flex items-center gap-3"
            style={{ background: `${colors.bgSecondary}E6`, border: `1px solid ${colors.border}` }}
          >
            <div className="flex items-center gap-1.5">
              <span className="text-[11px]" style={{ color: colors.textMuted }}>Scroll to pan</span>
            </div>
            <div className="w-px h-3" style={{ background: colors.border }} />
            <div className="flex items-center gap-1.5">
              <KbdHint><Command size={9} /></KbdHint>
              <span className="text-[11px]" style={{ color: colors.textMuted }}>+ scroll to zoom</span>
            </div>
            <div className="w-px h-3" style={{ background: colors.border }} />
            <div className="flex items-center gap-1.5">
              <span className="text-[11px]" style={{ color: colors.textMuted }}>Click node for details</span>
            </div>
          </div>
        </div>
      </div>

      {/* Node Detail Panel */}
      <AnimatePresence>
        {showNodeDetail && selectedNode && (
          <NodeDetailPanel
            nodeType={nodes.find(n => n.id === selectedNode)?.type || 'batch'}
            onClose={() => setShowNodeDetail(false)}
          />
        )}
      </AnimatePresence>

      {/* Results Panel */}
      <AnimatePresence>
        {showResults && batchPrediction && !showNodeDetail && (
          <motion.div
            initial={{ x: 400, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 400, opacity: 0 }}
            transition={{ duration: 0.25 }}
            className="w-[380px] flex flex-col z-20 flex-shrink-0"
            style={{ background: colors.bgSecondary, borderLeft: `1px solid ${colors.border}` }}
          >
            <div
              className="h-11 flex items-center justify-between px-4 flex-shrink-0"
              style={{ borderBottom: `1px solid ${colors.border}` }}
            >
              <h2 className="text-[13px] font-medium" style={{ color: colors.textPrimary }}>
                {batchPrediction.batch_name}
              </h2>
              <button onClick={() => setShowResults(false)} className="p-1 rounded" style={{ color: colors.textMuted }}>
                <X size={14} />
              </button>
            </div>

            <div className="flex-1 overflow-auto p-4 space-y-4">
              {/* Stats */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-3 rounded-lg" style={{ background: colors.bgTertiary, border: `1px solid ${colors.border}` }}>
                  <div className="flex items-center gap-2 mb-2">
                    <Award size={11} style={{ color: colors.unicorn }} />
                    <span className="text-[10px] font-medium uppercase" style={{ color: colors.textMuted }}>Unicorns</span>
                  </div>
                  <p className="text-xl font-semibold" style={{ color: colors.unicorn }}>
                    {batchPrediction.expected_unicorns.toFixed(1)}
                  </p>
                </div>
                <div className="p-3 rounded-lg" style={{ background: colors.bgTertiary, border: `1px solid ${colors.border}` }}>
                  <div className="flex items-center gap-2 mb-2">
                    <DollarSign size={11} style={{ color: colors.success }} />
                    <span className="text-[10px] font-medium uppercase" style={{ color: colors.textMuted }}>Value</span>
                  </div>
                  <p className="text-xl font-semibold" style={{ color: colors.success }}>
                    ${batchPrediction.expected_total_value.toFixed(1)}B
                  </p>
                </div>
              </div>

              {/* Companies */}
              <div>
                <h3 className="text-[10px] font-medium uppercase mb-3" style={{ color: colors.textMuted }}>
                  Top Candidates
                </h3>
                <div className="space-y-2">
                  {batchPrediction.startups.slice(0, 5).map((p) => (
                    <PredictionCard key={p.startup_id} prediction={p} onClick={() => openStartupChat(p)} />
                  ))}
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Chat Panel */}
      <AnimatePresence>
        {showChat && selectedStartup && (
          <motion.div
            initial={{ y: '100%', opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            exit={{ y: '100%', opacity: 0 }}
            className="fixed bottom-0 right-4 w-[380px] h-[480px] rounded-t-xl flex flex-col z-30"
            style={{ background: colors.bgSecondary, border: `1px solid ${colors.border}` }}
          >
            <div className="h-11 flex items-center justify-between px-4" style={{ borderBottom: `1px solid ${colors.border}` }}>
              <div className="flex items-center gap-2.5">
                <MessageSquare size={11} style={{ color: colors.success }} />
                <span className="text-[13px] font-medium" style={{ color: colors.textPrimary }}>
                  {selectedStartup.startup_name}
                </span>
              </div>
              <button onClick={() => setShowChat(false)} className="p-1 rounded" style={{ color: colors.textMuted }}>
                <X size={14} />
              </button>
            </div>

            <div className="flex-1 overflow-auto p-4 space-y-3">
              {chatMessages.length === 0 && (
                <div className="text-center py-12">
                  <MessageSquare size={18} style={{ color: colors.textMuted }} className="mx-auto mb-3" />
                  <p className="text-[13px]" style={{ color: colors.textSecondary }}>
                    Ask about {selectedStartup.startup_name}
                  </p>
                </div>
              )}
              {chatMessages.map((msg, i) => (
                <div key={i} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className="max-w-[85%] px-3 py-2 rounded-lg text-[13px]"
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
                    <Loader2 size={14} className="animate-spin" style={{ color: colors.textMuted }} />
                  </div>
                </div>
              )}
            </div>

            <div className="p-3" style={{ borderTop: `1px solid ${colors.border}` }}>
              <div className="flex gap-2">
                <input
                  type="text"
                  value={chatInput}
                  onChange={(e) => setChatInput(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && sendChatMessage()}
                  placeholder="Ask a question..."
                  className="flex-1 px-3 py-2 rounded-md text-[13px]"
                  style={{ background: colors.bgTertiary, color: colors.textPrimary, border: `1px solid ${colors.border}` }}
                />
                <button
                  onClick={sendChatMessage}
                  disabled={isChatting || !chatInput.trim()}
                  className="px-3 py-2 rounded-md disabled:opacity-40"
                  style={{ background: colors.accent }}
                >
                  <Send size={14} className="text-white" />
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Tagline */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
        className="fixed bottom-4 left-1/2 -translate-x-1/2 px-4 py-2 rounded-full text-[11px] z-10"
        style={{ background: `${colors.bgSecondary}E6`, color: colors.textMuted, border: `1px solid ${colors.border}` }}
      >
        There's a future where you win; we engineer that for you.
      </motion.div>

      <style jsx global>{`
        @keyframes dash { to { stroke-dashoffset: -8; } }
        .animate-dash { animation: dash 0.4s linear infinite; }
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: transparent; }
        ::-webkit-scrollbar-thumb { background: ${colors.border}; border-radius: 3px; }
        ::selection { background: ${colors.accentMuted}; color: ${colors.textPrimary}; }
      `}</style>
    </div>
  )
}
