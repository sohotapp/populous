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

  // Node-based pipeline APIs
  nodes: {
    marketScanner: async (sector: string, companies: string[] = []) => {
      const res = await fetch(`${API_URL}/api/nodes/market_scanner`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sector, companies, time_window_days: 90 })
      })
      return res.json()
    },

    alternativeData: async (companyName: string) => {
      const res = await fetch(`${API_URL}/api/nodes/alternative_data`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: companyName, signals: ['github', 'jobs', 'social'] })
      })
      return res.json()
    },

    financialSignals: async (sector: string, stage = 'seed') => {
      const res = await fetch(`${API_URL}/api/nodes/financial_signals`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sector, stage, geography: 'US' })
      })
      return res.json()
    },

    historicalOutcomes: async (accelerator = 'YC') => {
      const res = await fetch(`${API_URL}/api/nodes/historical_outcomes`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ accelerator, vintage_years: [2018, 2019, 2020, 2021] })
      })
      return res.json()
    },

    networkGraph: async (companies: string[]) => {
      const res = await fetch(`${API_URL}/api/nodes/network_graph`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ companies, include_investors: true, include_founders: true })
      })
      return res.json()
    },

    monteCarlo: async (prediction: any) => {
      const res = await fetch(`${API_URL}/api/nodes/monte_carlo`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prediction, simulations: 10000 })
      })
      return res.json()
    },

    sensitivity: async (prediction: any) => {
      const res = await fetch(`${API_URL}/api/nodes/sensitivity`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prediction, range_pct: 0.20 })
      })
      return res.json()
    },

    cohortComparison: async (currentBatch: string, predictions: any[]) => {
      const res = await fetch(`${API_URL}/api/nodes/cohort_comparison`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          current_batch: currentBatch,
          current_predictions: predictions,
          comparison_cohorts: ['YC W21', 'YC W22', 'YC W23']
        })
      })
      return res.json()
    },

    riskDecomposition: async (prediction: any) => {
      const res = await fetch(`${API_URL}/api/nodes/risk_decomposition`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prediction })
      })
      return res.json()
    },

    marketTiming: async (sector: string) => {
      const res = await fetch(`${API_URL}/api/nodes/market_timing`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ sector })
      })
      return res.json()
    },

    portfolioOptimizer: async (companies: any[]) => {
      const res = await fetch(`${API_URL}/api/nodes/portfolio_optimizer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ companies, risk_tolerance: 0.7 })
      })
      return res.json()
    },

    trajectorySim: async (company: any, prediction: any) => {
      const res = await fetch(`${API_URL}/api/nodes/trajectory_sim`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company, prediction, years: 7, simulations: 1000 })
      })
      return res.json()
    },

    exitModeler: async (company: any) => {
      const res = await fetch(`${API_URL}/api/nodes/exit_modeler`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company })
      })
      return res.json()
    },

    fundingScenarios: async (currentValuation: number) => {
      const res = await fetch(`${API_URL}/api/nodes/funding_scenarios`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ current_valuation: currentValuation })
      })
      return res.json()
    },

    decisionBrief: async (companyName: string, prediction: any) => {
      const res = await fetch(`${API_URL}/api/nodes/decision_brief`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: companyName, prediction })
      })
      return res.json()
    },

    comparisonMatrix: async (companies: any[]) => {
      const res = await fetch(`${API_URL}/api/nodes/comparison_matrix`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ companies })
      })
      return res.json()
    },

    whatifExplorer: async (prediction: any, factorChanges: any) => {
      const res = await fetch(`${API_URL}/api/nodes/whatif_explorer`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prediction, factor_changes: factorChanges })
      })
      return res.json()
    },

    timelineProjection: async (companyName: string, prediction: any) => {
      const res = await fetch(`${API_URL}/api/nodes/timeline_projection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ company_name: companyName, prediction, trajectory: {} })
      })
      return res.json()
    },

    health: async () => {
      const res = await fetch(`${API_URL}/api/nodes/health`)
      return res.json()
    }
  },

  // ========== GRAPH EXECUTION API (NEW - Proper Data Flow) ==========
  graph: {
    // List all nodes and dependencies
    listNodes: async () => {
      const res = await fetch(`${API_URL}/api/graph/nodes`)
      return res.json()
    },

    // Execute full graph synchronously (blocks until complete)
    executeSync: async (batchCode: string, maxCompanies = 5) => {
      const res = await fetch(`${API_URL}/api/graph/execute/sync`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          batch_code: batchCode,
          accelerator: 'YC',
          max_companies: maxCompanies
        })
      })
      return res.json()
    },

    // Execute graph asynchronously (returns immediately, poll for status)
    execute: async (batchCode: string, maxCompanies = 5) => {
      const res = await fetch(`${API_URL}/api/graph/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          batch_code: batchCode,
          accelerator: 'YC',
          max_companies: maxCompanies
        })
      })
      return res.json()
    },

    // Get execution status
    getStatus: async (executionId: string) => {
      const res = await fetch(`${API_URL}/api/graph/status/${executionId}`)
      return res.json()
    },

    // Get full results after completion
    getResults: async (executionId: string, includeFullState = false) => {
      const res = await fetch(`${API_URL}/api/graph/results/${executionId}?include_full_state=${includeFullState}`)
      return res.json()
    },

    // Quick demo endpoint
    demo: async () => {
      const res = await fetch(`${API_URL}/api/graph/demo`)
      return res.json()
    },

    // Get all deliverables for an execution
    getDeliverables: async (executionId: string) => {
      const res = await fetch(`${API_URL}/api/graph/deliverables/${executionId}`)
      return res.json()
    },

    // Get investment memo for a specific company
    getInvestmentMemo: async (executionId: string, companyName: string) => {
      const res = await fetch(`${API_URL}/api/graph/deliverables/${executionId}/investment-memo/${encodeURIComponent(companyName)}`)
      return res.json()
    },

    // Get risk register for a specific company
    getRiskRegister: async (executionId: string, companyName: string) => {
      const res = await fetch(`${API_URL}/api/graph/deliverables/${executionId}/risk-register/${encodeURIComponent(companyName)}`)
      return res.json()
    },

    // Get executive brief for a specific company
    getExecutiveBrief: async (executionId: string, companyName: string) => {
      const res = await fetch(`${API_URL}/api/graph/deliverables/${executionId}/executive-brief/${encodeURIComponent(companyName)}`)
      return res.json()
    },

    // Get decision matrix for the batch
    getDecisionMatrix: async (executionId: string) => {
      const res = await fetch(`${API_URL}/api/graph/deliverables/${executionId}/decision-matrix`)
      return res.json()
    }
  }
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

  // Enterprise Deliverables state
  const [deliverables, setDeliverables] = useState<any>(null)
  const [showDeliverables, setShowDeliverables] = useState(false)
  const [selectedDeliverableType, setSelectedDeliverableType] = useState<'decision_matrix' | 'investment_memo' | 'risk_register' | 'executive_brief'>('decision_matrix')
  const [selectedCompanyForDeliverable, setSelectedCompanyForDeliverable] = useState<string | null>(null)
  const [executionId, setExecutionId] = useState<string | null>(null)

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

  // Run batch analysis using the Graph Execution Engine
  // This runs all nodes in proper dependency order with state accumulation
  const runBatchAnalysis = async () => {
    setIsResearching(true)
    setShowResults(false)
    setBatchPrediction(null)
    setShowNodeDetail(false)

    // Reset all nodes to idle first
    setNodes(prev => prev.map(n => ({ ...n, status: 'idle' as const })))

    // Helper to update single node status
    const updateNodeStatus = (nodeId: string, status: 'idle' | 'running' | 'complete' | 'error') => {
      setNodes(prev => prev.map(n => n.id === nodeId ? { ...n, status } : n))
    }

    // Helper to update multiple nodes
    const updateNodesStatus = (nodeIds: string[], status: 'idle' | 'running' | 'complete' | 'error') => {
      setNodes(prev => prev.map(n => nodeIds.includes(n.id) ? { ...n, status } : n))
    }

    // Graph execution order - matches backend node IDs
    const executionOrder = [
      'batch', 'research', 'market_scanner', 'alternative_data',
      'financial_signals', 'network_graph', 'historical_outcomes',
      'prediction', 'monte_carlo', 'sensitivity',
      'trajectory_sim', 'exit_modeler', 'funding_scenarios',
      'decision_brief', 'comparison_matrix', 'portfolio_optimizer',
      'deliverables'  // Enterprise deliverables node (Answer Node)
    ]

    // Additional frontend nodes to mark complete after main pipeline
    const additionalNodes = [
      'cohort_comparison', 'risk_decomposition', 'market_timing',
      'competitive_dynamics', 'scenario_planner', 'chat',
      'investment_memo', 'risk_report', 'portfolio_dashboard',
      'alert_system', 'stakeholder_views', 'whatif_explorer', 'timeline_projection'
    ]

    try {
      console.log('[GraphPipeline] Starting full graph execution...')
      console.log('[GraphPipeline] Batch:', batchCode)

      // Start first node as running immediately for visual feedback
      updateNodeStatus('batch', 'running')

      // Start async execution
      const execResponse = await api.graph.execute(batchCode, 5)

      if (!execResponse || !execResponse.execution_id) {
        throw new Error('Failed to start graph execution - no execution ID returned')
      }

      const executionId = execResponse.execution_id
      console.log('[GraphPipeline] Execution started:', executionId)

      // Poll for status and update node visualizations
      let completed = false
      let lastCompletedCount = 0
      let pollCount = 0
      const maxPolls = 300 // 2.5 minutes max

      while (!completed && pollCount < maxPolls) {
        await new Promise(resolve => setTimeout(resolve, 500)) // Poll every 500ms
        pollCount++

        try {
          const status = await api.graph.getStatus(executionId)
          console.log('[GraphPipeline] Poll', pollCount, '| Status:', status.status, '| Progress:', (status.progress * 100).toFixed(0) + '%', '| Nodes:', status.nodes_completed?.length || 0)

          // Update node statuses based on completion
          const completedNodes = status.nodes_completed || []

          // Mark newly completed nodes
          if (completedNodes.length > lastCompletedCount) {
            for (const nodeId of completedNodes) {
              updateNodeStatus(nodeId, 'complete')
            }
            lastCompletedCount = completedNodes.length

            // Mark next node as running
            const nextNodeIndex = completedNodes.length
            if (nextNodeIndex < executionOrder.length) {
              const nextNode = executionOrder[nextNodeIndex]
              if (nextNode) {
                updateNodeStatus(nextNode, 'running')
              }
            }
          }

          // Update additional nodes based on progress
          if (status.progress > 0.3) {
            updateNodesStatus(['cohort_comparison', 'risk_decomposition'], 'running')
          }
          if (status.progress > 0.5) {
            updateNodesStatus(['market_timing', 'competitive_dynamics', 'scenario_planner'], 'running')
          }
          if (status.progress > 0.8) {
            updateNodesStatus(['chat', 'investment_memo', 'risk_report', 'portfolio_dashboard', 'alert_system', 'stakeholder_views', 'whatif_explorer', 'timeline_projection'], 'running')
          }

          if (status.status === 'completed' || status.status === 'failed') {
            completed = true
            if (status.status === 'failed') {
              throw new Error('Graph execution failed: ' + (status.error || 'Unknown error'))
            }
          }
        } catch (pollError) {
          console.error('[GraphPipeline] Poll error:', pollError)
          // Continue polling on error
        }
      }

      if (!completed) {
        throw new Error('Graph execution timed out after ' + (pollCount * 0.5) + ' seconds')
      }

      // Mark all nodes complete
      updateNodesStatus(executionOrder, 'complete')
      updateNodesStatus(additionalNodes, 'complete')

      // Fetch full results
      console.log('[GraphPipeline] Fetching full results...')
      const results = await api.graph.getResults(executionId, true)

      if (!results) {
        throw new Error('No results returned from graph execution')
      }

      console.log('[GraphPipeline] Results received:', {
        companies: results.companies?.length,
        predictions: Object.keys(results.predictions || {}).length,
        success: results.success,
        time: results.total_time_ms
      })

      // Transform graph results to batch prediction format
      const startups = (results.companies || []).map((companyName: string) => {
        const pred = results.predictions?.[companyName] || {}
        const brief = results.decision_briefs?.[companyName] || {}
        return {
          startup_id: companyName.toLowerCase().replace(/\s+/g, '_'),
          startup_name: companyName,
          unicorn_probability: pred.unicorn_probability || 0,
          centaur_probability: pred.centaur_probability || 0,
          success_probability: pred.success_probability || 0,
          failure_probability: 1 - (pred.success_probability || 0),
          expected_valuation: pred.expected_valuation || 0,
          valuation_p10: (pred.expected_valuation || 0) * 0.3,
          valuation_p50: (pred.expected_valuation || 0) * 0.7,
          valuation_p90: (pred.expected_valuation || 0) * 2.5,
          team_score: pred.team_score || 0.5,
          market_score: pred.market_score || 0.5,
          traction_score: pred.traction_score || 0.5,
          timing_score: pred.timing_score || 0.5,
          capital_score: pred.capital_score || 0.5,
          key_strengths: pred.key_strengths || ['Data analysis in progress'],
          key_risks: pred.key_risks || ['Limited data available'],
          detailed_reasoning: brief.summary || `${companyName} analysis complete.`,
          prediction_confidence: pred.prediction_confidence || 0.5,
          data_quality: 'high',
          recommendation: brief.recommendation || 'MONITOR',
          percentile_rank: brief.percentile_rank || 50,
          years_to_exit: 7
        }
      })

      // Sort by unicorn probability (descending)
      startups.sort((a: any, b: any) => b.unicorn_probability - a.unicorn_probability)

      // Calculate batch-level stats
      const totalUnicornProb = startups.reduce((sum: number, s: any) => sum + s.unicorn_probability, 0)
      const totalValue = startups.reduce((sum: number, s: any) => sum + s.expected_valuation, 0)

      const enhancedResult = {
        batch_name: `YC ${batchCode}`,
        batch_size: startups.length,
        expected_unicorns: totalUnicornProb,
        unicorn_range: [totalUnicornProb * 0.5, totalUnicornProb * 1.5] as [number, number],
        expected_centaurs: startups.reduce((sum: number, s: any) => sum + s.centaur_probability, 0),
        expected_total_value: totalValue / 1e9, // In billions
        startups,
        top_unicorn_candidates: startups.slice(0, 3).map((s: any) => s.startup_name),
        highest_risk_startups: startups.slice(-2).map((s: any) => s.startup_name),
        batch_quality_score: startups.length > 0 ? startups.reduce((sum: number, s: any) => sum + s.prediction_confidence, 0) / startups.length : 0,
        market_timing_score: startups[0]?.timing_score || 0.5,
        graph_execution: {
          execution_id: executionId,
          total_time_ms: results.total_time_ms,
          nodes_completed: results.nodes_completed,
          comparison_matrix: results.comparison_matrix,
          portfolio_analysis: results.portfolio_analysis
        }
      }

      console.log('[GraphPipeline] Pipeline complete!', {
        totalTime: results.total_time_ms + 'ms',
        nodesCompleted: results.nodes_completed?.length,
        companiesAnalyzed: startups.length,
        topCompany: startups[0]?.startup_name,
        topProbability: (startups[0]?.unicorn_probability * 100).toFixed(1) + '%'
      })

      setBatchPrediction(enhancedResult)
      setShowResults(true)

      // Store execution ID and deliverables
      setExecutionId(executionId)
      if (results.deliverables) {
        setDeliverables(results.deliverables)
        console.log('[GraphPipeline] Deliverables loaded:', Object.keys(results.deliverables))
      }

    } catch (error: any) {
      console.error('[GraphPipeline] Analysis failed:', error)
      // Mark running nodes as error
      setNodes(prev => prev.map(n => n.status === 'running' ? { ...n, status: 'error' } : n))
      alert('Analysis failed: ' + (error?.message || 'Unknown error'))
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
            className="w-[420px] flex flex-col z-20 flex-shrink-0"
            style={{ background: colors.bgSecondary, borderLeft: `1px solid ${colors.border}` }}
          >
            {/* Header */}
            <div
              className="h-12 flex items-center justify-between px-4 flex-shrink-0"
              style={{ borderBottom: `1px solid ${colors.border}` }}
            >
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg flex items-center justify-center" style={{ background: colors.unicornMuted }}>
                  <Sparkles size={16} style={{ color: colors.unicorn }} />
                </div>
                <div>
                  <h2 className="text-[14px] font-semibold" style={{ color: colors.textPrimary }}>
                    {batchPrediction.batch_name} Analysis
                  </h2>
                  <p className="text-[11px]" style={{ color: colors.textMuted }}>
                    {batchPrediction.batch_size} companies analyzed
                  </p>
                </div>
              </div>
              <button onClick={() => setShowResults(false)} className="p-1.5 rounded-lg hover:bg-white/5 transition-colors" style={{ color: colors.textMuted }}>
                <X size={16} />
              </button>
            </div>

            <div className="flex-1 overflow-auto p-4 space-y-5">
              {/* Executive Summary Stats */}
              <div className="grid grid-cols-2 gap-3">
                <div className="p-4 rounded-xl" style={{ background: `linear-gradient(135deg, ${colors.unicornMuted} 0%, transparent 100%)`, border: `1px solid ${colors.unicorn}30` }}>
                  <div className="flex items-center gap-2 mb-2">
                    <Award size={14} style={{ color: colors.unicorn }} />
                    <span className="text-[11px] font-medium uppercase tracking-wide" style={{ color: colors.unicorn }}>Expected Unicorns</span>
                  </div>
                  <p className="text-2xl font-bold" style={{ color: colors.unicorn }}>
                    {batchPrediction.expected_unicorns.toFixed(2)}
                  </p>
                  <p className="text-[10px] mt-1" style={{ color: colors.textMuted }}>
                    of {batchPrediction.batch_size} companies
                  </p>
                </div>
                <div className="p-4 rounded-xl" style={{ background: `linear-gradient(135deg, ${colors.successMuted} 0%, transparent 100%)`, border: `1px solid ${colors.success}30` }}>
                  <div className="flex items-center gap-2 mb-2">
                    <DollarSign size={14} style={{ color: colors.success }} />
                    <span className="text-[11px] font-medium uppercase tracking-wide" style={{ color: colors.success }}>Total Value</span>
                  </div>
                  <p className="text-2xl font-bold" style={{ color: colors.success }}>
                    ${batchPrediction.expected_total_value.toFixed(2)}B
                  </p>
                  <p className="text-[10px] mt-1" style={{ color: colors.textMuted }}>
                    expected portfolio value
                  </p>
                </div>
              </div>

              {/* Pipeline Stats */}
              {batchPrediction.graph_execution && (
                <div className="p-3 rounded-lg flex items-center justify-between" style={{ background: colors.bgTertiary, border: `1px solid ${colors.border}` }}>
                  <div className="flex items-center gap-2">
                    <Activity size={12} style={{ color: colors.accent }} />
                    <span className="text-[11px]" style={{ color: colors.textSecondary }}>Pipeline completed</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className="text-[11px] font-medium" style={{ color: colors.textPrimary }}>
                      {batchPrediction.graph_execution.nodes_completed?.length || 16} nodes
                    </span>
                    <span className="text-[11px]" style={{ color: colors.textMuted }}>
                      {((batchPrediction.graph_execution.total_time_ms || 0) / 1000).toFixed(1)}s
                    </span>
                  </div>
                </div>
              )}

              {/* Top Candidates */}
              <div>
                <div className="flex items-center justify-between mb-3">
                  <h3 className="text-[11px] font-semibold uppercase tracking-wide" style={{ color: colors.textMuted }}>
                    Top Unicorn Candidates
                  </h3>
                  <span className="text-[10px] px-2 py-0.5 rounded-full" style={{ background: colors.accentMuted, color: colors.accent }}>
                    Ranked by probability
                  </span>
                </div>
                <div className="space-y-2">
                  {batchPrediction.startups.slice(0, 5).map((p) => (
                    <PredictionCard key={p.startup_id} prediction={p} onClick={() => openStartupChat(p)} />
                  ))}
                </div>
              </div>

              {/* Enterprise Deliverables Button */}
              {deliverables && (
                <div className="pt-2">
                  <button
                    onClick={() => {
                      setShowDeliverables(true)
                      setShowResults(false)
                    }}
                    className="w-full py-3 px-4 rounded-xl flex items-center justify-between group transition-all duration-200"
                    style={{
                      background: `linear-gradient(135deg, ${colors.accent}15 0%, ${colors.unicorn}15 100%)`,
                      border: `1px solid ${colors.accent}40`
                    }}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${colors.accent} 0%, ${colors.unicorn} 100%)` }}>
                        <FileBarChart size={18} className="text-white" />
                      </div>
                      <div className="text-left">
                        <p className="text-[13px] font-semibold" style={{ color: colors.textPrimary }}>
                          Enterprise Deliverables
                        </p>
                        <p className="text-[11px]" style={{ color: colors.textMuted }}>
                          Investment Memos, Risk Registers, Decision Matrix
                        </p>
                      </div>
                    </div>
                    <ChevronRight size={16} style={{ color: colors.accent }} className="group-hover:translate-x-1 transition-transform" />
                  </button>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Enterprise Deliverables Panel */}
      <AnimatePresence>
        {showDeliverables && deliverables && (
          <motion.div
            initial={{ x: 500, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: 500, opacity: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="w-[520px] flex flex-col z-20 flex-shrink-0"
            style={{ background: colors.bgSecondary, borderLeft: `1px solid ${colors.border}` }}
          >
            {/* Header */}
            <div
              className="h-14 flex items-center justify-between px-4 flex-shrink-0"
              style={{ borderBottom: `1px solid ${colors.border}`, background: `linear-gradient(135deg, ${colors.accent}08 0%, transparent 100%)` }}
            >
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 rounded-lg flex items-center justify-center" style={{ background: `linear-gradient(135deg, ${colors.accent} 0%, ${colors.unicorn} 100%)` }}>
                  <FileBarChart size={18} className="text-white" />
                </div>
                <div>
                  <h2 className="text-[14px] font-bold" style={{ color: colors.textPrimary }}>
                    Enterprise Deliverables
                  </h2>
                  <p className="text-[10px] uppercase tracking-wider" style={{ color: colors.textMuted }}>
                    Board-Ready Documents
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => {
                    setShowDeliverables(false)
                    setShowResults(true)
                  }}
                  className="p-2 rounded-lg hover:bg-white/5 transition-colors"
                  style={{ color: colors.textMuted }}
                >
                  <X size={16} />
                </button>
              </div>
            </div>

            {/* Deliverable Type Tabs */}
            <div className="px-4 py-3 flex gap-2 overflow-x-auto" style={{ borderBottom: `1px solid ${colors.border}` }}>
              {[
                { id: 'decision_matrix', label: 'Decision Matrix', icon: Scale },
                { id: 'investment_memo', label: 'Investment Memo', icon: FileBarChart },
                { id: 'risk_register', label: 'Risk Register', icon: Shield },
                { id: 'executive_brief', label: 'Executive Brief', icon: FileText },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setSelectedDeliverableType(tab.id as any)}
                  className="px-3 py-2 rounded-lg text-[12px] font-medium flex items-center gap-2 transition-all whitespace-nowrap"
                  style={{
                    background: selectedDeliverableType === tab.id ? colors.accent : colors.bgTertiary,
                    color: selectedDeliverableType === tab.id ? 'white' : colors.textSecondary,
                    border: `1px solid ${selectedDeliverableType === tab.id ? colors.accent : colors.border}`
                  }}
                >
                  <tab.icon size={13} />
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Company Selector for per-company deliverables */}
            {(selectedDeliverableType === 'investment_memo' || selectedDeliverableType === 'risk_register' || selectedDeliverableType === 'executive_brief') && (
              <div className="px-4 py-3" style={{ borderBottom: `1px solid ${colors.border}` }}>
                <select
                  value={selectedCompanyForDeliverable || ''}
                  onChange={(e) => setSelectedCompanyForDeliverable(e.target.value)}
                  className="w-full px-3 py-2 rounded-lg text-[13px] appearance-none cursor-pointer"
                  style={{ background: colors.bgTertiary, color: colors.textPrimary, border: `1px solid ${colors.border}` }}
                >
                  <option value="">Select a company...</option>
                  {batchPrediction?.startups.map((s) => (
                    <option key={s.startup_id} value={s.startup_name}>{s.startup_name}</option>
                  ))}
                </select>
              </div>
            )}

            {/* Deliverable Content */}
            <div className="flex-1 overflow-auto p-4">
              {/* Decision Matrix View */}
              {selectedDeliverableType === 'decision_matrix' && deliverables.decision_matrix && (
                <div className="space-y-4">
                  <div className="p-4 rounded-xl" style={{ background: `linear-gradient(135deg, ${colors.accent}10 0%, transparent 100%)`, border: `1px solid ${colors.accent}30` }}>
                    <div className="flex items-center gap-2 mb-2">
                      <Scale size={16} style={{ color: colors.accent }} />
                      <h3 className="text-[14px] font-bold" style={{ color: colors.textPrimary }}>
                        {deliverables.decision_matrix.title || 'Investment Decision Matrix'}
                      </h3>
                    </div>
                    <p className="text-[12px]" style={{ color: colors.textSecondary }}>
                      {deliverables.decision_matrix.decision_context}
                    </p>
                  </div>

                  {/* Recommended Company */}
                  {deliverables.decision_matrix.recommended_company && (
                    <div className="p-4 rounded-xl" style={{ background: colors.successMuted, border: `1px solid ${colors.success}40` }}>
                      <div className="flex items-center gap-2 mb-2">
                        <Award size={16} style={{ color: colors.success }} />
                        <span className="text-[10px] font-bold uppercase tracking-wider" style={{ color: colors.success }}>
                          TOP RECOMMENDATION
                        </span>
                      </div>
                      <p className="text-[18px] font-bold" style={{ color: colors.textPrimary }}>
                        {deliverables.decision_matrix.recommended_company}
                      </p>
                      <p className="text-[12px] mt-2" style={{ color: colors.textSecondary }}>
                        {deliverables.decision_matrix.recommendation_rationale}
                      </p>
                      <div className="mt-3 flex items-center gap-2">
                        <span className="text-[11px] px-2 py-1 rounded-full font-medium" style={{ background: `${colors.success}20`, color: colors.success }}>
                          {(deliverables.decision_matrix.confidence_level * 100).toFixed(0)}% Confidence
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Company Comparison Table */}
                  {deliverables.decision_matrix.companies && (
                    <div>
                      <h4 className="text-[11px] font-bold uppercase tracking-wider mb-3" style={{ color: colors.textMuted }}>
                        Side-by-Side Comparison
                      </h4>
                      <div className="space-y-2">
                        {deliverables.decision_matrix.companies.map((company: any, idx: number) => (
                          <div
                            key={company.name}
                            className="p-3 rounded-lg flex items-center justify-between"
                            style={{
                              background: idx === 0 ? `${colors.unicorn}10` : colors.bgTertiary,
                              border: `1px solid ${idx === 0 ? colors.unicorn : colors.border}40`
                            }}
                          >
                            <div className="flex items-center gap-3">
                              <span className="text-[14px] font-bold w-6 h-6 rounded-full flex items-center justify-center"
                                style={{ background: colors.bgElevated, color: idx === 0 ? colors.unicorn : colors.textMuted }}>
                                {idx + 1}
                              </span>
                              <div>
                                <p className="text-[13px] font-semibold" style={{ color: colors.textPrimary }}>{company.name}</p>
                                <p className="text-[10px]" style={{ color: colors.textMuted }}>
                                  {company.recommendation.replace('_', ' ')}
                                </p>
                              </div>
                            </div>
                            <div className="text-right">
                              <p className="text-[14px] font-bold" style={{ color: colors.unicorn }}>
                                {(company.unicorn_probability * 100).toFixed(1)}%
                              </p>
                              <p className="text-[10px]" style={{ color: colors.textMuted }}>Unicorn Prob</p>
                            </div>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              )}

              {/* Investment Memo View */}
              {selectedDeliverableType === 'investment_memo' && selectedCompanyForDeliverable && deliverables.investment_memos?.[selectedCompanyForDeliverable] && (
                <div className="space-y-4">
                  {(() => {
                    const memo = deliverables.investment_memos[selectedCompanyForDeliverable]
                    return (
                      <>
                        {/* Header */}
                        <div className="p-4 rounded-xl" style={{ background: `linear-gradient(135deg, ${colors.accent}10 0%, ${colors.unicorn}10 100%)`, border: `1px solid ${colors.accent}30` }}>
                          <div className="flex items-center justify-between mb-3">
                            <div>
                              <p className="text-[10px] uppercase tracking-wider font-bold" style={{ color: colors.textMuted }}>
                                Investment Memorandum
                              </p>
                              <h3 className="text-[18px] font-bold" style={{ color: colors.textPrimary }}>
                                {memo.company_name}
                              </h3>
                            </div>
                            <span className={`px-3 py-1.5 rounded-lg text-[11px] font-bold uppercase ${
                              memo.recommendation === 'STRONG_YES' ? 'bg-green-500/20 text-green-400' :
                              memo.recommendation === 'YES' ? 'bg-green-400/20 text-green-300' :
                              memo.recommendation === 'CONDITIONAL' ? 'bg-yellow-500/20 text-yellow-400' :
                              'bg-red-500/20 text-red-400'
                            }`}>
                              {memo.recommendation.replace('_', ' ')}
                            </span>
                          </div>
                          <p className="text-[12px]" style={{ color: colors.textSecondary }}>
                            {memo.recommendation_summary}
                          </p>
                        </div>

                        {/* Investment Thesis */}
                        {memo.thesis && (
                          <div className="p-4 rounded-lg" style={{ background: colors.bgTertiary, border: `1px solid ${colors.border}` }}>
                            <h4 className="text-[11px] font-bold uppercase tracking-wider mb-2" style={{ color: colors.textMuted }}>
                              Investment Thesis
                            </h4>
                            <p className="text-[13px] font-semibold mb-3" style={{ color: colors.textPrimary }}>
                              {memo.thesis.headline}
                            </p>
                            <ul className="space-y-1">
                              {memo.thesis.rationale.map((r: string, i: number) => (
                                <li key={i} className="text-[12px] flex items-start gap-2" style={{ color: colors.textSecondary }}>
                                  <CheckCircle size={12} className="mt-0.5 flex-shrink-0" style={{ color: colors.success }} />
                                  {r}
                                </li>
                              ))}
                            </ul>
                          </div>
                        )}

                        {/* Deal Terms */}
                        {memo.deal && (
                          <div className="p-4 rounded-lg" style={{ background: colors.bgTertiary, border: `1px solid ${colors.border}` }}>
                            <h4 className="text-[11px] font-bold uppercase tracking-wider mb-3" style={{ color: colors.textMuted }}>
                              Deal Terms
                            </h4>
                            <div className="grid grid-cols-2 gap-3">
                              <div>
                                <p className="text-[10px]" style={{ color: colors.textMuted }}>Investment</p>
                                <p className="text-[14px] font-bold" style={{ color: colors.success }}>
                                  ${(memo.deal.investment_amount / 1000000).toFixed(1)}M
                                </p>
                              </div>
                              <div>
                                <p className="text-[10px]" style={{ color: colors.textMuted }}>Pre-Money</p>
                                <p className="text-[14px] font-bold" style={{ color: colors.textPrimary }}>
                                  ${(memo.deal.pre_money_valuation / 1000000).toFixed(0)}M
                                </p>
                              </div>
                              <div>
                                <p className="text-[10px]" style={{ color: colors.textMuted }}>Ownership</p>
                                <p className="text-[14px] font-bold" style={{ color: colors.unicorn }}>
                                  {memo.deal.ownership_percentage.toFixed(2)}%
                                </p>
                              </div>
                              <div>
                                <p className="text-[10px]" style={{ color: colors.textMuted }}>Instrument</p>
                                <p className="text-[14px] font-bold" style={{ color: colors.textPrimary }}>
                                  {memo.deal.instrument}
                                </p>
                              </div>
                            </div>
                          </div>
                        )}

                        {/* Top Risks */}
                        {memo.top_risks && (
                          <div className="p-4 rounded-lg" style={{ background: `${colors.error}10`, border: `1px solid ${colors.error}30` }}>
                            <h4 className="text-[11px] font-bold uppercase tracking-wider mb-2" style={{ color: colors.error }}>
                              Key Risks
                            </h4>
                            <div className="space-y-2">
                              {memo.top_risks.map((risk: any, i: number) => (
                                <div key={i} className="flex items-start justify-between gap-2">
                                  <span className="text-[12px]" style={{ color: colors.textSecondary }}>{risk.risk}</span>
                                  <span className={`text-[10px] px-2 py-0.5 rounded font-medium ${
                                    risk.severity === 'HIGH' ? 'bg-red-500/20 text-red-400' :
                                    risk.severity === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' :
                                    'bg-green-500/20 text-green-400'
                                  }`}>{risk.severity}</span>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </>
                    )
                  })()}
                </div>
              )}

              {/* Risk Register View */}
              {selectedDeliverableType === 'risk_register' && selectedCompanyForDeliverable && deliverables.risk_registers?.[selectedCompanyForDeliverable] && (
                <div className="space-y-4">
                  {(() => {
                    const register = deliverables.risk_registers[selectedCompanyForDeliverable]
                    return (
                      <>
                        {/* Header */}
                        <div className="p-4 rounded-xl" style={{ background: `${colors.error}10`, border: `1px solid ${colors.error}30` }}>
                          <div className="flex items-center justify-between mb-2">
                            <div className="flex items-center gap-2">
                              <Shield size={16} style={{ color: colors.error }} />
                              <h3 className="text-[14px] font-bold" style={{ color: colors.textPrimary }}>
                                Risk Register - {register.company_name}
                              </h3>
                            </div>
                            <span className={`px-3 py-1 rounded-lg text-[11px] font-bold uppercase ${
                              register.overall_risk_rating === 'CRITICAL' ? 'bg-red-600/20 text-red-400' :
                              register.overall_risk_rating === 'HIGH' ? 'bg-red-500/20 text-red-400' :
                              register.overall_risk_rating === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' :
                              'bg-green-500/20 text-green-400'
                            }`}>
                              {register.overall_risk_rating} RISK
                            </span>
                          </div>
                          <div className="flex items-center gap-4 mt-3">
                            <div>
                              <p className="text-[10px]" style={{ color: colors.textMuted }}>Risk Score</p>
                              <p className="text-[18px] font-bold" style={{ color: colors.error }}>{register.risk_score}/100</p>
                            </div>
                            <div>
                              <p className="text-[10px]" style={{ color: colors.textMuted }}>Trend</p>
                              <p className="text-[14px] font-semibold" style={{ color: colors.textPrimary }}>{register.risk_trend}</p>
                            </div>
                          </div>
                        </div>

                        {/* Risk Summary */}
                        <div className="grid grid-cols-4 gap-2">
                          {[
                            { label: 'Critical', count: register.critical_risks, color: '#EF4444' },
                            { label: 'High', count: register.high_risks, color: '#F97316' },
                            { label: 'Medium', count: register.medium_risks, color: '#EAB308' },
                            { label: 'Low', count: register.low_risks, color: '#22C55E' },
                          ].map((item) => (
                            <div key={item.label} className="p-3 rounded-lg text-center" style={{ background: colors.bgTertiary }}>
                              <p className="text-[20px] font-bold" style={{ color: item.color }}>{item.count}</p>
                              <p className="text-[10px]" style={{ color: colors.textMuted }}>{item.label}</p>
                            </div>
                          ))}
                        </div>

                        {/* Risks List */}
                        <div>
                          <h4 className="text-[11px] font-bold uppercase tracking-wider mb-3" style={{ color: colors.textMuted }}>
                            Identified Risks
                          </h4>
                          <div className="space-y-2">
                            {register.risks?.map((risk: any) => (
                              <div key={risk.id} className="p-3 rounded-lg" style={{ background: colors.bgTertiary, border: `1px solid ${colors.border}` }}>
                                <div className="flex items-start justify-between gap-2 mb-2">
                                  <p className="text-[12px] font-semibold" style={{ color: colors.textPrimary }}>{risk.title}</p>
                                  <span className={`text-[9px] px-2 py-0.5 rounded font-bold ${
                                    risk.severity === 'CRITICAL' ? 'bg-red-600/20 text-red-400' :
                                    risk.severity === 'HIGH' ? 'bg-red-500/20 text-red-400' :
                                    risk.severity === 'MEDIUM' ? 'bg-yellow-500/20 text-yellow-400' :
                                    'bg-green-500/20 text-green-400'
                                  }`}>{risk.severity}</span>
                                </div>
                                <p className="text-[11px] mb-2" style={{ color: colors.textSecondary }}>{risk.description}</p>
                                <div className="flex items-center gap-3 text-[10px]" style={{ color: colors.textMuted }}>
                                  <span>Likelihood: {(risk.likelihood * 100).toFixed(0)}%</span>
                                  <span>Impact: {(risk.impact_score * 100).toFixed(0)}%</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      </>
                    )
                  })()}
                </div>
              )}

              {/* Executive Brief View */}
              {selectedDeliverableType === 'executive_brief' && selectedCompanyForDeliverable && deliverables.executive_briefs?.[selectedCompanyForDeliverable] && (
                <div className="space-y-4">
                  {(() => {
                    const brief = deliverables.executive_briefs[selectedCompanyForDeliverable]
                    return (
                      <>
                        {/* Header */}
                        <div className="p-4 rounded-xl text-center" style={{ background: `linear-gradient(135deg, ${colors.bgTertiary} 0%, ${colors.bgElevated} 100%)`, border: `1px solid ${colors.border}` }}>
                          <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: colors.textMuted }}>
                            Executive Decision Brief
                          </p>
                          <h3 className="text-[18px] font-bold mb-1" style={{ color: colors.textPrimary }}>
                            {brief.title}
                          </h3>
                          <p className="text-[11px]" style={{ color: colors.textMuted }}>
                            Prepared for: {brief.prepared_for}
                          </p>
                        </div>

                        {/* The Ask */}
                        <div className="p-4 rounded-lg" style={{ background: `${colors.accent}10`, border: `1px solid ${colors.accent}30` }}>
                          <p className="text-[10px] uppercase tracking-wider mb-1" style={{ color: colors.accent }}>
                            Decision Required
                          </p>
                          <p className="text-[13px] font-semibold" style={{ color: colors.textPrimary }}>
                            {brief.decision_required}
                          </p>
                          <p className="text-[11px] mt-1" style={{ color: colors.textMuted }}>
                            Deadline: {brief.deadline}
                          </p>
                        </div>

                        {/* Recommendation */}
                        <div className="p-4 rounded-lg" style={{ background: colors.bgTertiary }}>
                          <div className="flex items-center justify-between mb-2">
                            <p className="text-[10px] uppercase tracking-wider" style={{ color: colors.textMuted }}>
                              Recommendation
                            </p>
                            <span className={`px-3 py-1 rounded-lg text-[11px] font-bold uppercase ${
                              brief.recommendation === 'STRONG_YES' ? 'bg-green-500/20 text-green-400' :
                              brief.recommendation === 'YES' ? 'bg-green-400/20 text-green-300' :
                              brief.recommendation === 'CONDITIONAL' ? 'bg-yellow-500/20 text-yellow-400' :
                              'bg-red-500/20 text-red-400'
                            }`}>
                              {brief.recommendation.replace('_', ' ')}
                            </span>
                          </div>
                          <p className="text-[13px]" style={{ color: colors.textSecondary }}>
                            {brief.recommendation_text}
                          </p>
                          <div className="mt-2">
                            <span className="text-[10px] px-2 py-1 rounded-full" style={{ background: colors.accentMuted, color: colors.accent }}>
                              {(brief.confidence * 100).toFixed(0)}% Confidence
                            </span>
                          </div>
                        </div>

                        {/* Key Points */}
                        <div>
                          <h4 className="text-[11px] font-bold uppercase tracking-wider mb-2" style={{ color: colors.textMuted }}>
                            Key Points
                          </h4>
                          <ul className="space-y-1.5">
                            {brief.key_points?.map((point: string, i: number) => (
                              <li key={i} className="flex items-start gap-2 text-[12px]" style={{ color: colors.textSecondary }}>
                                <span className="w-5 h-5 rounded-full flex items-center justify-center text-[10px] font-bold flex-shrink-0"
                                  style={{ background: colors.accentMuted, color: colors.accent }}>
                                  {i + 1}
                                </span>
                                {point}
                              </li>
                            ))}
                          </ul>
                        </div>

                        {/* Key Metrics */}
                        {brief.key_metrics && (
                          <div className="grid grid-cols-2 gap-2">
                            {Object.entries(brief.key_metrics).map(([key, value]) => (
                              <div key={key} className="p-3 rounded-lg" style={{ background: colors.bgTertiary }}>
                                <p className="text-[10px]" style={{ color: colors.textMuted }}>{key}</p>
                                <p className="text-[14px] font-bold" style={{ color: colors.textPrimary }}>{value as string}</p>
                              </div>
                            ))}
                          </div>
                        )}
                      </>
                    )
                  })()}
                </div>
              )}

              {/* No Selection State */}
              {(selectedDeliverableType === 'investment_memo' || selectedDeliverableType === 'risk_register' || selectedDeliverableType === 'executive_brief') && !selectedCompanyForDeliverable && (
                <div className="flex flex-col items-center justify-center py-12 text-center">
                  <FileBarChart size={32} style={{ color: colors.textMuted }} className="mb-3" />
                  <p className="text-[13px] font-medium" style={{ color: colors.textSecondary }}>
                    Select a company above
                  </p>
                  <p className="text-[11px]" style={{ color: colors.textMuted }}>
                    to view {selectedDeliverableType.replace('_', ' ')}
                  </p>
                </div>
              )}
            </div>

            {/* Footer with Export */}
            <div className="p-4 flex items-center justify-between" style={{ borderTop: `1px solid ${colors.border}` }}>
              <p className="text-[10px]" style={{ color: colors.textMuted }}>
                Generated {deliverables.generated_at ? new Date(deliverables.generated_at).toLocaleDateString() : 'Today'}
              </p>
              <div className="flex items-center gap-2">
                <button className="px-3 py-1.5 rounded-lg text-[11px] font-medium flex items-center gap-2"
                  style={{ background: colors.bgTertiary, color: colors.textSecondary, border: `1px solid ${colors.border}` }}>
                  <Copy size={12} />
                  Copy
                </button>
                <button className="px-3 py-1.5 rounded-lg text-[11px] font-medium flex items-center gap-2"
                  style={{ background: colors.accent, color: 'white' }}>
                  <Download size={12} />
                  Export PDF
                </button>
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
