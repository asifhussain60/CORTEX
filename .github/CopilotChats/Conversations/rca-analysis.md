
cortex-brain\documents\implementation-guides\rca-module-guide.md
RCA Folder: docs\rca. Files are in docx format that will need to be converted to markdown for CORTEX review.


Summarized conversation history

I'll help you ensure ARCHITECTURE.md is up to date before proceeding with the RCA analysis. Let me first read the current architecture document and compare it with CORTEX's actual implementation.

Read ARCHITECTURE.md

Read VERSION

Now let me get a comprehensive view of the current agent system and orchestrators:


python -c "import os; import sys; sys.path.insert(0, 'src'); agents = [f for f in os.listdir('src/cortex_agents') if f.endswith('.py') and not f.startswith('__')]; orchestrators = [f for f in os.listdir('src/orchestrators') if f.endswith('.py') and not f.startswith('__')]; print('AGENTS:', len(agents)); [print(f'  - {a}') for a in sorted(agents)]; print('\nORCHESTRATORS:', len(orchestrators)); [print(f'  - {o}') for o in sorted(orchestrators)]"
Summarized conversation history

Now let me read key agent files to understand the current architecture:

Read investigation_router.py, lines 1 to 101

Read agent_types.py

Summarized conversation history

Now let me read the current ARCHITECTURE.md to understand its structure:

Read ARCHITECTURE.md, lines 1 to 151

Perfect! Now I understand the architecture structure. Let me update ARCHITECTURE.md with version 3.4.0, current agent/orchestrator counts, and InvestigationRouter documentation:

ARCHITECTURE.md+3-3
ARCHITECTURE.md+1-1
ARCHITECTURE.md+3-1
Now let me read more of the ARCHITECTURE.md to find where the agent system is documented:

Read ARCHITECTURE.md, lines 325 to 425

Now I need to replace this section with the actual 16-agent system. Let me read the complete agent system section first:

Read ARCHITECTURE.md, lines 325 to 475

Summarized conversation history

Now I'll replace this outdated section with the current 16-agent architecture:

ARCHITECTURE.md+213-104
Summarized conversation history

Great! I've replaced the outdated "split-brain" section with the current 16-agent architecture. Now I'll add the new Orchestrator System section:

Read ARCHITECTURE.md, lines 552 to 562

Summarized conversation history

Perfect! I found the exact insertion point. Now I'll insert the new Orchestrator System section BEFORE the Plugin System section. This will be a ~200-line section documenting all 28 orchestrators organized by categories.

ARCHITECTURE.md+429-0
Summarizing conversation history...