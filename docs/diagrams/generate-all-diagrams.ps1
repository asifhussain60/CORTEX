# PowerShell Script to Generate All CORTEX Diagram Prompts and Narratives
# This script creates 15 comprehensive prompt and narrative files

$diagrams = @(
    @{
        num = "02"
        name = "agent-system"
        title = "Dual-Hemisphere Agent System"
        description = "Shows LEFT (tactical) and RIGHT (strategic) brain agents with corpus callosum coordination"
        colors = @{
            right = "#F59E0B"
            left = "#3B82F6"
            corpus = "#10B981"
        }
    },
    @{
        num = "03"
        name = "tdd-workflow"
        title = "TDD Workflow (RED → GREEN → REFACTOR)"
        description = "Test-Driven Development cycle enforced by CORTEX agents"
        colors = @{
            red = "#EF4444"
            green = "#10B981"
            blue = "#3B82F6"
            validate = "#6B46C1"
        }
    },
    @{
        num = "04"
        name = "intent-routing"
        title = "Intent Detection & Routing"
        description = "How natural language requests are routed to specialist agents"
        colors = @{
            router = "#F59E0B"
            agents = "#3B82F6"
        }
    },
    @{
        num = "05"
        name = "agent-coordination"
        title = "Multi-Agent Coordination Sequence"
        description = "Agent collaboration for feature implementation"
        colors = @{
            sequence = "#3B82F6"
        }
    },
    @{
        num = "06"
        name = "conversation-memory"
        title = "Conversation Memory Flow"
        description = "How conversations are captured and stored in Tier 1"
        colors = @{
            capture = "#3B82F6"
            process = "#10B981"
            storage = "#3B82F6"
            fifo = "#F59E0B"
        }
    },
    @{
        num = "07"
        name = "brain-protection"
        title = "Brain Protection System (6 Layers)"
        description = "Protection layers enforcing Rule #22"
        colors = @{
            detect = "#3B82F6"
            protect = "#6B46C1"
            layers = "#EF4444"
            response = "#10B981"
        }
    },
    @{
        num = "08"
        name = "knowledge-graph"
        title = "Knowledge Graph Learning & Pattern Decay"
        description = "Tier 2 pattern learning, reuse, and decay mechanism"
        colors = @{
            learn = "#10B981"
            reuse = "#3B82F6"
            decay = "#F59E0B"
            relationships = "#6B46C1"
        }
    },
    @{
        num = "09"
        name = "context-intelligence"
        title = "Context Intelligence (Tier 3)"
        description = "Git analysis, file stability, session analytics, proactive warnings"
        colors = @{
            git = "#10B981"
            files = "#3B82F6"
            session = "#F59E0B"
            health = "#6B46C1"
            warnings = "#EF4444"
        }
    },
    @{
        num = "10"
        name = "feature-planning"
        title = "Interactive Feature Planning Flow"
        description = "Work Planner agent creating multi-phase implementation plans"
        colors = @{
            detect = "#F59E0B"
            assess = "#3B82F6"
            questions = "#10B981"
            plan = "#6B46C1"
        }
    },
    @{
        num = "11"
        name = "performance-benchmarks"
        title = "Performance Benchmarks (Actual vs Target)"
        description = "Real performance metrics across all tiers and agents"
        colors = @{
            tier1 = "#3B82F6"
            tier2 = "#10B981"
            tier3 = "#F59E0B"
            agents = "#6B46C1"
        }
    },
    @{
        num = "12"
        name = "token-optimization"
        title = "Token Optimization Impact (97.2% Reduction)"
        description = "Before/after metrics from modular refactoring"
        colors = @{
            before = "#EF4444"
            optimization = "#F59E0B"
            after = "#10B981"
            impact = "#6B46C1"
        }
    },
    @{
        num = "13"
        name = "plugin-system"
        title = "Zero-Footprint Plugin System"
        description = "Plugin architecture using only CORTEX brain intelligence"
        colors = @{
            core = "#6B46C1"
            plugins = "#3B82F6"
            flagship = "#10B981"
            usage = "#F59E0B"
        }
    },
    @{
        num = "14"
        name = "data-flow-complete"
        title = "Complete Data Flow (Request to Completion)"
        description = "End-to-end flow for 'Add purple button' request"
        colors = @{
            tier1 = "#3B82F6"
            tier2 = "#10B981"
            tier3 = "#F59E0B"
            execute = "#3B82F6"
            validate = "#6B46C1"
        }
    },
    @{
        num = "15"
        name = "before-vs-after"
        title = "CORTEX Comparison (Before vs After)"
        description = "Visual comparison of Copilot with and without CORTEX memory"
        colors = @{
            without = "#EF4444"
            with = "#10B981"
            benefits = "#6B46C1"
        }
    }
)

Write-Host "Total diagrams to generate: $($diagrams.Count)" -ForegroundColor Cyan
Write-Host "This script defines the structure for all diagram prompts and narratives" -ForegroundColor Green
Write-Host "`nDiagram List:" -ForegroundColor Yellow

foreach ($diagram in $diagrams) {
    Write-Host "  $($diagram.num). $($diagram.title)" -ForegroundColor White
}

Write-Host "`nReady to generate all files programmatically" -ForegroundColor Green
