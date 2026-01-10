#!/usr/bin/env python3
"""
Level 1 Page Configurations
============================

Configuration data for all Level 1 pages defining sections, cards, and content.
This is the source of truth for page regeneration.

Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

from typing import Dict, List, Any


# ═══════════════════════════════════════════════════════════════
# COLOR ROTATION (7-color palette)
# ═══════════════════════════════════════════════════════════════
GLASS_COLORS = ['purple', 'emerald', 'amber', 'cyan', 'teal', 'indigo', 'pink']


# ═══════════════════════════════════════════════════════════════
# PAGE CONFIGURATIONS
# ═══════════════════════════════════════════════════════════════

LEVEL1_PAGES: Dict[str, Dict[str, Any]] = {
    'architecture': {
        'title': 'System Architecture',
        'subtitle': 'Four-tier brain structure with specialized orchestrators and agents',
        'hero_icon': 'fa-sitemap',
        'sections': [
            {
                'title': 'Four-Tier Brain',
                'subtitle': 'Hierarchical long-term memory system',
                'color': 'purple',
                'cards': [
                    {
                        'title': 'Tier 0: Governance',
                        'description': 'Core identity, rules, and compliance frameworks that define CORTEX operational boundaries',
                        'icon': 'fa-gavel',
                        'link': 'tier0-governance.html',
                        'stats': [
                            {'label': 'Rules', 'value': '5'},
                            {'label': 'Priority', 'value': 'Highest'},
                        ]
                    },
                    {
                        'title': 'Tier 1: Working Memory',
                        'description': 'Active context and hot data for immediate operations and decision-making processes',
                        'icon': 'fa-bolt',
                        'link': 'tier1-working-memory.html',
                        'stats': [
                            {'label': 'Capacity', 'value': '10MB'},
                            {'label': 'Access', 'value': '<1ms'},
                        ]
                    },
                    {
                        'title': 'Tier 2: Knowledge Graph',
                        'description': 'Semantic relationships and structured learning paths for intelligent navigation',
                        'icon': 'fa-diagram-project',
                        'link': 'tier2-knowledge-graph.html',
                        'stats': [
                            {'label': 'Nodes', 'value': '~500'},
                            {'label': 'Edges', 'value': '~2000'},
                        ]
                    },
                    {
                        'title': 'Tier 3: Dev Context',
                        'description': 'Project-specific context including codebase structure and development patterns',
                        'icon': 'fa-code',
                        'link': 'tier3-dev-context.html',
                        'stats': [
                            {'label': 'Projects', 'value': 'Unlimited'},
                            {'label': 'Isolation', 'value': '100%'},
                        ]
                    },
                ]
            },
            {
                'title': 'Orchestrator Ecosystem',
                'subtitle': 'Eight autonomous workflow engines',
                'color': 'emerald',
                'cards': [
                    {
                        'title': 'Planning System v5',
                        'description': 'YAML-based autonomous plan generation with multi-phase execution',
                        'icon': 'fa-sitemap',
                        'link': '../orchestrators/planning.html',
                        'stats': [
                            {'label': 'Phases', 'value': '1-15'},
                            {'label': 'Format', 'value': 'YAML'},
                        ]
                    },
                    {
                        'title': 'TDD v2',
                        'description': 'Test-Driven Development with RED→GREEN→REFACTOR enforcement',
                        'icon': 'fa-vial',
                        'link': '../orchestrators/tdd.html',
                        'stats': [
                            {'label': 'Coverage', 'value': '>80%'},
                            {'label': 'Mode', 'value': 'Autonomous'},
                        ]
                    },
                ]
            },
        ]
    },
    'security': {
        'title': 'Security & Compliance',
        'subtitle': 'Multi-layered security architecture with SKULL rule enforcement',
        'hero_icon': 'fa-shield-halved',
        'sections': [
            {
                'title': 'Security Layers',
                'subtitle': 'Four-tier protection framework',
                'color': 'purple',
                'cards': [
                    {
                        'title': 'Brain Protection',
                        'description': 'SKULL rules enforce governance boundaries',
                        'icon': 'fa-brain',
                        'link': 'brain-protection.html',
                        'stats': [
                            {'label': 'Rules', 'value': '5'},
                            {'label': 'Enforcement', 'value': 'Auto'},
                        ]
                    },
                    {
                        'title': 'Code Isolation',
                        'description': 'CORTEX/user repo separation enforced',
                        'icon': 'fa-code-branch',
                        'link': 'code-isolation.html',
                        'stats': [
                            {'label': 'Isolation', 'value': '100%'},
                            {'label': 'Violations', 'value': '0'},
                        ]
                    },
                    {
                        'title': 'TDD Enforcement',
                        'description': 'Tests must fail before implementation',
                        'icon': 'fa-vial',
                        'link': 'tdd-enforcement.html',
                        'stats': [
                            {'label': 'RED→GREEN', 'value': 'Required'},
                            {'label': 'Coverage', 'value': '>80%'},
                        ]
                    },
                ]
            },
            {
                'title': 'Access Control',
                'subtitle': 'Permission management and audit logging',
                'color': 'emerald',
                'cards': [
                    {
                        'title': 'Role-Based Access',
                        'description': 'Granular permission control per operation',
                        'icon': 'fa-user-shield',
                        'link': 'access-control.html',
                        'stats': [
                            {'label': 'Roles', 'value': '4'},
                            {'label': 'Permissions', 'value': '12'},
                        ]
                    },
                    {
                        'title': 'Audit Trail',
                        'description': 'Complete logging of all security events',
                        'icon': 'fa-file-lines',
                        'link': 'audit-logging.html',
                        'stats': [
                            {'label': 'Events/day', 'value': '~500'},
                            {'label': 'Retention', 'value': '90d'},
                        ]
                    },
                ]
            },
            {
                'title': 'Data Protection',
                'subtitle': 'Sanitization and encryption',
                'color': 'amber',
                'cards': [
                    {
                        'title': 'PII Sanitization',
                        'description': 'Automatic removal of sensitive data',
                        'icon': 'fa-user-secret',
                        'link': 'sanitization.html',
                        'stats': [
                            {'label': 'Patterns', 'value': '15'},
                            {'label': 'Detection', 'value': '99.8%'},
                        ]
                    },
                    {
                        'title': 'Encryption',
                        'description': 'AES-256 for sensitive data at rest',
                        'icon': 'fa-lock',
                        'link': 'encryption.html',
                        'stats': [
                            {'label': 'Algorithm', 'value': 'AES-256'},
                            {'label': 'Key Rotation', 'value': '30d'},
                        ]
                    },
                ]
            },
        ]
    },
    
    'features': {
        'title': 'Core Features',
        'subtitle': 'Eight autonomous orchestrators and two specialist agents',
        'hero_icon': 'fa-layer-group',
        'sections': [
            {
                'title': 'Orchestrators',
                'subtitle': 'Workflow automation engines',
                'color': 'cyan',
                'cards': [
                    {
                        'title': 'Planning System v5',
                        'description': 'YAML-based autonomous plan generation',
                        'icon': 'fa-sitemap',
                        'link': '../orchestrators/planning.html',
                        'stats': [
                            {'label': 'Format', 'value': 'YAML'},
                            {'label': 'Phases', 'value': '1-15'},
                        ]
                    },
                    {
                        'title': 'TDD v2',
                        'description': 'RED→GREEN→REFACTOR cycle enforcement',
                        'icon': 'fa-vial',
                        'link': '../orchestrators/tdd.html',
                        'stats': [
                            {'label': 'Mode', 'value': 'Autonomous'},
                            {'label': 'Coverage', 'value': '>80%'},
                        ]
                    },
                    {
                        'title': 'Vacuum v2',
                        'description': 'Deep filesystem cleanup and optimization',
                        'icon': 'fa-broom',
                        'link': '../orchestrators/vacuum.html',
                        'stats': [
                            {'label': 'Depth', 'value': 'Recursive'},
                            {'label': 'Safety', 'value': 'Dry-run'},
                        ]
                    },
                ]
            },
            {
                'title': 'Specialist Agents',
                'subtitle': 'Intelligent assistants',
                'color': 'teal',
                'cards': [
                    {
                        'title': 'Intent Classifier',
                        'description': 'LLM-powered request routing',
                        'icon': 'fa-brain',
                        'link': '../agents/intent-classifier.html',
                        'stats': [
                            {'label': 'Accuracy', 'value': '98.5%'},
                            {'label': 'Latency', 'value': '<100ms'},
                        ]
                    },
                    {
                        'title': 'Context Broker',
                        'description': 'Multi-tier context management',
                        'icon': 'fa-network-wired',
                        'link': '../agents/context-broker.html',
                        'stats': [
                            {'label': 'Tiers', 'value': '4'},
                            {'label': 'Cache Hit', 'value': '85%'},
                        ]
                    },
                ]
            },
        ]
    },
    
    'story': {
        'title': 'The CORTEX Story',
        'subtitle': 'From concept to production-ready AI assistant',
        'hero_icon': 'fa-book-open',
        'sections': [
            {
                'title': 'Genesis',
                'subtitle': 'Why CORTEX was created',
                'color': 'indigo',
                'cards': [
                    {
                        'title': 'The Problem',
                        'description': 'AI assistants lack memory and context',
                        'icon': 'fa-lightbulb',
                        'link': 'problem.html',
                        'stats': [
                            {'label': 'Context Loss', 'value': '~80%'},
                            {'label': 'Repeatability', 'value': 'Low'},
                        ]
                    },
                    {
                        'title': 'The Vision',
                        'description': 'Long-term memory with strategic planning',
                        'icon': 'fa-eye',
                        'link': 'vision.html',
                        'stats': [
                            {'label': 'Memory Tiers', 'value': '4'},
                            {'label': 'Retention', 'value': 'Permanent'},
                        ]
                    },
                ]
            },
            {
                'title': 'Evolution',
                'subtitle': 'Key milestones in development',
                'color': 'pink',
                'cards': [
                    {
                        'title': 'v1.0 - Foundation',
                        'description': 'Initial brain structure and orchestrators',
                        'icon': 'fa-rocket',
                        'link': 'v1-foundation.html',
                        'stats': [
                            {'label': 'Date', 'value': 'Q4 2024'},
                            {'label': 'Features', 'value': '5'},
                        ]
                    },
                    {
                        'title': 'v5.0 - Autonomy',
                        'description': 'Fully autonomous execution framework',
                        'icon': 'fa-robot',
                        'link': 'v5-autonomy.html',
                        'stats': [
                            {'label': 'Date', 'value': 'Q1 2026'},
                            {'label': 'Orchestrators', 'value': '8'},
                        ]
                    },
                ]
            },
        ]
    },
    
    'sts': {
        'title': 'STS (Self-Tuning System)',
        'subtitle': 'Adaptive optimization with machine learning',
        'hero_icon': 'fa-gauge-high',
        'sections': [
            {
                'title': 'Performance Optimization',
                'subtitle': 'Real-time tuning and adaptation',
                'color': 'purple',
                'cards': [
                    {
                        'title': 'Auto-Tuning',
                        'description': 'ML-powered parameter optimization',
                        'icon': 'fa-sliders',
                        'link': 'auto-tuning.html',
                        'stats': [
                            {'label': 'Parameters', 'value': '12'},
                            {'label': 'Improvement', 'value': '+35%'},
                        ]
                    },
                    {
                        'title': 'Load Balancing',
                        'description': 'Dynamic resource allocation',
                        'icon': 'fa-scale-balanced',
                        'link': 'load-balancing.html',
                        'stats': [
                            {'label': 'Efficiency', 'value': '92%'},
                            {'label': 'Latency', 'value': '-40%'},
                        ]
                    },
                ]
            },
            {
                'title': 'Monitoring & Alerts',
                'subtitle': 'Proactive system health management',
                'color': 'emerald',
                'cards': [
                    {
                        'title': 'Health Checks',
                        'description': '11-phase system diagnostics',
                        'icon': 'fa-heartbeat',
                        'link': 'health-checks.html',
                        'stats': [
                            {'label': 'Phases', 'value': '11'},
                            {'label': 'Frequency', 'value': '1h'},
                        ]
                    },
                    {
                        'title': 'Alerting',
                        'description': 'Multi-channel notification system',
                        'icon': 'fa-bell',
                        'link': 'alerting.html',
                        'stats': [
                            {'label': 'Channels', 'value': '4'},
                            {'label': 'Response', 'value': '<5min'},
                        ]
                    },
                ]
            },
        ]
    },
    
    'getting-started': {
        'title': 'Getting Started',
        'subtitle': 'Quick start guide and installation',
        'hero_icon': 'fa-play-circle',
        'sections': [
            {
                'title': 'Installation',
                'subtitle': 'Get CORTEX running in minutes',
                'color': 'cyan',
                'cards': [
                    {
                        'title': 'Prerequisites',
                        'description': 'Python 3.9+, VS Code, Git',
                        'icon': 'fa-list-check',
                        'link': 'prerequisites.html',
                        'stats': [
                            {'label': 'Python', 'value': '3.9+'},
                            {'label': 'VS Code', 'value': 'Latest'},
                        ]
                    },
                    {
                        'title': 'Quick Install',
                        'description': 'One-command setup script',
                        'icon': 'fa-download',
                        'link': 'installation.html',
                        'stats': [
                            {'label': 'Time', 'value': '<5min'},
                            {'label': 'Commands', 'value': '1'},
                        ]
                    },
                ]
            },
            {
                'title': 'First Steps',
                'subtitle': 'Learn the basics',
                'color': 'teal',
                'cards': [
                    {
                        'title': 'Hello CORTEX',
                        'description': 'Your first interaction',
                        'icon': 'fa-hand-wave',
                        'link': 'hello-cortex.html',
                        'stats': [
                            {'label': 'Difficulty', 'value': 'Easy'},
                            {'label': 'Duration', 'value': '5min'},
                        ]
                    },
                    {
                        'title': 'Create a Plan',
                        'description': 'Generate your first execution plan',
                        'icon': 'fa-sitemap',
                        'link': 'first-plan.html',
                        'stats': [
                            {'label': 'Complexity', 'value': 'Low'},
                            {'label': 'Output', 'value': 'YAML'},
                        ]
                    },
                ]
            },
        ]
    },
    
    'knowledge': {
        'title': 'Knowledge Graph',
        'subtitle': 'Tier 2: Structured learning and relationships',
        'hero_icon': 'fa-diagram-project',
        'sections': [
            {
                'title': 'Graph Structure',
                'subtitle': 'Nodes, edges, and relationships',
                'color': 'indigo',
                'cards': [
                    {
                        'title': 'Concept Nodes',
                        'description': 'Core concepts and definitions',
                        'icon': 'fa-circle-nodes',
                        'link': 'concept-nodes.html',
                        'stats': [
                            {'label': 'Nodes', 'value': '~500'},
                            {'label': 'Categories', 'value': '8'},
                        ]
                    },
                    {
                        'title': 'Relationships',
                        'description': 'Semantic connections between concepts',
                        'icon': 'fa-link',
                        'link': 'relationships.html',
                        'stats': [
                            {'label': 'Edges', 'value': '~2000'},
                            {'label': 'Types', 'value': '12'},
                        ]
                    },
                ]
            },
            {
                'title': 'Learning Paths',
                'subtitle': 'Guided knowledge acquisition',
                'color': 'pink',
                'cards': [
                    {
                        'title': 'Beginner Track',
                        'description': 'Fundamentals and basic operations',
                        'icon': 'fa-graduation-cap',
                        'link': 'beginner-track.html',
                        'stats': [
                            {'label': 'Lessons', 'value': '12'},
                            {'label': 'Duration', 'value': '2h'},
                        ]
                    },
                    {
                        'title': 'Advanced Track',
                        'description': 'Custom orchestrators and agents',
                        'icon': 'fa-user-graduate',
                        'link': 'advanced-track.html',
                        'stats': [
                            {'label': 'Lessons', 'value': '8'},
                            {'label': 'Duration', 'value': '4h'},
                        ]
                    },
                ]
            },
        ]
    },
    
    'learning-paths': {
        'title': 'Learning Paths',
        'subtitle': 'Structured curriculum for mastering CORTEX',
        'hero_icon': 'fa-map',
        'sections': [
            {
                'title': 'Core Paths',
                'subtitle': 'Essential skills for all users',
                'color': 'purple',
                'cards': [
                    {
                        'title': 'Fundamentals',
                        'description': 'Core concepts and architecture',
                        'icon': 'fa-book',
                        'link': 'fundamentals.html',
                        'stats': [
                            {'label': 'Modules', 'value': '6'},
                            {'label': 'Time', 'value': '3h'},
                        ]
                    },
                    {
                        'title': 'Orchestrators',
                        'description': 'Mastering workflow automation',
                        'icon': 'fa-gears',
                        'link': 'orchestrators.html',
                        'stats': [
                            {'label': 'Modules', 'value': '8'},
                            {'label': 'Time', 'value': '5h'},
                        ]
                    },
                ]
            },
            {
                'title': 'Specialized Paths',
                'subtitle': 'Advanced topics',
                'color': 'emerald',
                'cards': [
                    {
                        'title': 'Custom Agents',
                        'description': 'Building your own agents',
                        'icon': 'fa-robot',
                        'link': 'custom-agents.html',
                        'stats': [
                            {'label': 'Modules', 'value': '4'},
                            {'label': 'Time', 'value': '4h'},
                        ]
                    },
                    {
                        'title': 'Brain Architecture',
                        'description': 'Deep dive into 4-tier memory',
                        'icon': 'fa-brain',
                        'link': 'brain-architecture.html',
                        'stats': [
                            {'label': 'Modules', 'value': '5'},
                            {'label': 'Time', 'value': '6h'},
                        ]
                    },
                ]
            },
        ]
    },
    
    'lens': {
        'title': 'CORTEX Lens',
        'subtitle': 'Visual analytics and insights dashboard',
        'hero_icon': 'fa-chart-line',
        'sections': [
            {
                'title': 'Dashboards',
                'subtitle': 'Real-time metrics and visualizations',
                'color': 'amber',
                'cards': [
                    {
                        'title': 'Performance',
                        'description': 'System performance metrics',
                        'icon': 'fa-tachometer-alt',
                        'link': 'performance-dashboard.html',
                        'stats': [
                            {'label': 'Metrics', 'value': '15'},
                            {'label': 'Refresh', 'value': '5s'},
                        ]
                    },
                    {
                        'title': 'Usage Analytics',
                        'description': 'Feature adoption and trends',
                        'icon': 'fa-chart-pie',
                        'link': 'usage-analytics.html',
                        'stats': [
                            {'label': 'Reports', 'value': '8'},
                            {'label': 'History', 'value': '90d'},
                        ]
                    },
                ]
            },
            {
                'title': 'Reports',
                'subtitle': 'Automated analysis and exports',
                'color': 'cyan',
                'cards': [
                    {
                        'title': 'Health Reports',
                        'description': 'System health summaries',
                        'icon': 'fa-file-medical',
                        'link': 'health-reports.html',
                        'stats': [
                            {'label': 'Frequency', 'value': 'Daily'},
                            {'label': 'Format', 'value': 'PDF/JSON'},
                        ]
                    },
                    {
                        'title': 'Audit Logs',
                        'description': 'Complete activity trail',
                        'icon': 'fa-file-lines',
                        'link': 'audit-logs.html',
                        'stats': [
                            {'label': 'Retention', 'value': '90d'},
                            {'label': 'Export', 'value': 'CSV/JSON'},
                        ]
                    },
                ]
            },
        ]
    },
    
    'token-optimization': {
        'title': 'Token Optimization',
        'subtitle': 'Intelligent context compression and caching',
        'hero_icon': 'fa-compress',
        'sections': [
            {
                'title': 'Compression',
                'subtitle': 'Reduce token usage without loss',
                'color': 'teal',
                'cards': [
                    {
                        'title': 'Smart Truncation',
                        'description': 'Importance-based content pruning',
                        'icon': 'fa-scissors',
                        'link': 'smart-truncation.html',
                        'stats': [
                            {'label': 'Reduction', 'value': '~40%'},
                            {'label': 'Accuracy', 'value': '98%'},
                        ]
                    },
                    {
                        'title': 'Semantic Compression',
                        'description': 'Meaning-preserving summarization',
                        'icon': 'fa-file-zipper',
                        'link': 'semantic-compression.html',
                        'stats': [
                            {'label': 'Ratio', 'value': '3:1'},
                            {'label': 'Fidelity', 'value': '95%'},
                        ]
                    },
                ]
            },
            {
                'title': 'Caching',
                'subtitle': 'Multi-tier context storage',
                'color': 'indigo',
                'cards': [
                    {
                        'title': 'L1 Cache',
                        'description': 'Hot context (immediate access)',
                        'icon': 'fa-bolt',
                        'link': 'l1-cache.html',
                        'stats': [
                            {'label': 'Size', 'value': '10MB'},
                            {'label': 'Hit Rate', 'value': '92%'},
                        ]
                    },
                    {
                        'title': 'L2 Cache',
                        'description': 'Warm context (frequent access)',
                        'icon': 'fa-database',
                        'link': 'l2-cache.html',
                        'stats': [
                            {'label': 'Size', 'value': '100MB'},
                            {'label': 'Hit Rate', 'value': '78%'},
                        ]
                    },
                ]
            },
        ]
    },
    
    'toolkit-manager': {
        'title': 'Toolkit Manager',
        'subtitle': 'Extension and plugin management',
        'hero_icon': 'fa-toolbox',
        'sections': [
            {
                'title': 'Core Toolkits',
                'subtitle': 'Built-in utilities and helpers',
                'color': 'pink',
                'cards': [
                    {
                        'title': 'File Operations',
                        'description': 'Safe filesystem manipulation',
                        'icon': 'fa-folder-open',
                        'link': 'file-operations.html',
                        'stats': [
                            {'label': 'Tools', 'value': '12'},
                            {'label': 'Safety', 'value': 'Dry-run'},
                        ]
                    },
                    {
                        'title': 'Git Integration',
                        'description': 'Version control automation',
                        'icon': 'fa-code-branch',
                        'link': 'git-integration.html',
                        'stats': [
                            {'label': 'Commands', 'value': '15'},
                            {'label': 'Auto-commit', 'value': 'Yes'},
                        ]
                    },
                ]
            },
            {
                'title': 'Extensions',
                'subtitle': 'Third-party and custom tools',
                'color': 'purple',
                'cards': [
                    {
                        'title': 'Plugin API',
                        'description': 'Create custom toolkits',
                        'icon': 'fa-plug',
                        'link': 'plugin-api.html',
                        'stats': [
                            {'label': 'Endpoints', 'value': '8'},
                            {'label': 'Documentation', 'value': 'Full'},
                        ]
                    },
                    {
                        'title': 'Marketplace',
                        'description': 'Browse and install extensions',
                        'icon': 'fa-store',
                        'link': 'marketplace.html',
                        'stats': [
                            {'label': 'Extensions', 'value': '~20'},
                            {'label': 'Rating', 'value': '4.8/5'},
                        ]
                    },
                ]
            },
        ]
    },
}
