"""
RCA Agent - Root Cause Analysis Intent Handler

Purpose: Routes RCA-related requests to RCAOrchestrator
Architecture: Lightweight routing agent following BaseAgent pattern

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse


class RCAAgent(BaseAgent):
    """
    Agent for Root Cause Analysis operations
    
    Handles:
    - Import RCA documents (DOCX → Markdown)
    - Start 5 Whys analysis
    - Answer Why questions
    - Generate executive reports
    - List active RCAs
    """
    
    def __init__(self, name: str = "rca_agent", brain_path: Optional[Path] = None):
        super().__init__(name)
        self.logger = logging.getLogger(__name__)
        
        if not brain_path:
            from src.utils.config_loader import get_cortex_config
            config = get_cortex_config()
            brain_path = Path(config.get('brainPath', 'cortex-brain'))
        
        from src.orchestrators.rca_orchestrator import RCAOrchestrator
        self.rca_orchestrator = RCAOrchestrator(brain_path)
    
    def can_handle(self, request: AgentRequest) -> bool:
        """Check if this agent can handle the request"""
        
        intent = request.intent.lower()
        query = request.query.lower()
        
        # RCA-specific intents
        rca_intents = [
            'rca',
            'root_cause_analysis',
            'analyze_rca',
            'import_rca',
            '5_whys',
            'five_whys'
        ]
        
        # RCA-specific keywords
        rca_keywords = [
            'root cause',
            '5 whys',
            'five whys',
            'rca analysis',
            'rca report',
            'import rca',
            'analyze rca'
        ]
        
        if any(rca_intent in intent for rca_intent in rca_intents):
            return True
        
        if any(keyword in query for keyword in rca_keywords):
            return True
        
        return False
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """Execute RCA operation"""
        
        try:
            intent = request.intent.lower()
            query = request.query.lower()
            context = request.context or {}
            
            # Route to appropriate operation
            if 'import' in query or 'import_rca' in intent:
                return self._handle_import_rca(request)
            
            elif 'list' in query or 'show' in query and 'active' in query:
                return self._handle_list_rcas(request)
            
            elif 'analyze' in query or 'start' in query or '5_whys' in intent:
                return self._handle_start_analysis(request)
            
            elif 'answer' in query or 'why' in query:
                return self._handle_answer_why(request)
            
            elif 'report' in query or 'generate' in query:
                return self._handle_generate_report(request)
            
            else:
                # Default: Show help
                return self._handle_help()
        
        except Exception as e:
            self.logger.error(f"Error executing RCA operation: {e}", exc_info=True)
            return AgentResponse(
                success=False,
                result={},
                message=f"Error: {str(e)}",
                needs_user_input=False
            )
    
    def _handle_import_rca(self, request: AgentRequest) -> AgentResponse:
        """Handle RCA document import"""
        
        # Extract file path from query or context
        file_path = self._extract_file_path(request.query, request.context)
        
        if not file_path:
            return AgentResponse(
                success=False,
                result={},
                message="Please provide the path to the RCA DOCX file.\n\nUsage: `import rca [file_path]`\nor attach the file to your message.",
                needs_user_input=True
            )
        
        result = self.rca_orchestrator.import_rca_document(Path(file_path))
        
        return AgentResponse(
            success=result['success'],
            result=result,
            message=self._format_import_result(result),
            needs_user_input=False
        )
    
    def _handle_list_rcas(self, request: AgentRequest) -> AgentResponse:
        """Handle list active RCAs"""
        
        result = self.rca_orchestrator.list_active_rcas()
        
        return AgentResponse(
            success=result['success'],
            result=result,
            message=self._format_list_result(result),
            needs_user_input=False
        )
    
    def _handle_start_analysis(self, request: AgentRequest) -> AgentResponse:
        """Handle start 5 Whys analysis"""
        
        # Extract analysis ID from query
        analysis_id = self._extract_analysis_id(request.query)
        
        if not analysis_id:
            # Show active RCAs to choose from
            list_result = self.rca_orchestrator.list_active_rcas()
            
            if list_result['count'] == 0:
                return AgentResponse(
                    success=False,
                    result={},
                    message="No active RCA analyses found. Import an RCA document first:\n\n`import rca [file_path]`",
                    needs_user_input=True
                )
            
            return AgentResponse(
                success=False,
                result=list_result,
                message=f"Found {list_result['count']} active RCA(s). Please specify which one:\n\n" + 
                        self._format_list_result(list_result) +
                        "\n\nUsage: `analyze rca [analysis_id]`",
                needs_user_input=True
            )
        
        # Start 5 Whys analysis
        result = self.rca_orchestrator.start_5_whys_analysis(analysis_id)
        
        return AgentResponse(
            success=result['success'],
            result=result,
            message=self._format_analysis_start(result),
            needs_user_input=result.get('success', False)
        )
    
    def _handle_answer_why(self, request: AgentRequest) -> AgentResponse:
        """Handle answer to Why question"""
        
        # Extract analysis ID and answer
        analysis_id = self._extract_analysis_id(request.query)
        answer = self._extract_answer(request.query)
        
        if not analysis_id or not answer:
            return AgentResponse(
                success=False,
                result={},
                message="Please provide both analysis ID and answer.\n\nUsage: `answer rca [analysis_id]: [your answer]`",
                needs_user_input=True
            )
        
        # Record answer and get next question
        result = self.rca_orchestrator.answer_why_question(analysis_id, answer)
        
        return AgentResponse(
            success=result['success'],
            result=result,
            message=self._format_why_response(result),
            needs_user_input=result.get('success', False)
        )
    
    def _handle_generate_report(self, request: AgentRequest) -> AgentResponse:
        """Handle generate executive report"""
        
        analysis_id = self._extract_analysis_id(request.query)
        
        if not analysis_id:
            return AgentResponse(
                success=False,
                result={},
                message="Please specify the analysis ID.\n\nUsage: `report rca [analysis_id]`",
                needs_user_input=True
            )
        
        # Generate report
        result = self.rca_orchestrator.generate_executive_report(analysis_id)
        
        return AgentResponse(
            success=result['success'],
            result=result,
            message=self._format_report_result(result),
            needs_user_input=False
        )
    
    def _handle_help(self) -> AgentResponse:
        """Show RCA help"""
        
        help_message = """## 🔍 CORTEX RCA (Root Cause Analysis) Commands

### Import RCA Document
```
import rca [file_path]
```
Converts DOCX RCA document to markdown and prepares for 5 Whys analysis.

### Start 5 Whys Analysis
```
analyze rca [analysis_id]
```
Begins interactive 5 Whys questioning to identify root cause.

### Answer Why Question
```
answer rca [analysis_id]: [your answer]
```
Provide answer to current Why question. System will guide you through 5 levels.

### Generate Executive Report
```
report rca [analysis_id]
```
Creates executive-ready RCA report for senior leadership.

### List Active RCAs
```
list rcas
```
Shows all active RCA analyses in progress.

### Example Workflow

1. **Import:** `import rca docs/rca/incident-2024.docx`
2. **Analyze:** `analyze rca 20241201-incident-2024`
3. **Answer Why 1:** `answer rca 20241201: Service crashed due to memory leak`
4. **Continue through Why 2-5** (system guides you)
5. **Generate Report:** `report rca 20241201`
6. **Share with leadership**

### Features

✅ Interactive 5 Whys methodology
✅ Intelligent question suggestions based on patterns
✅ Confidence scoring for answers
✅ Executive-ready reports (copy-paste to email)
✅ Pattern learning from historical RCAs
✅ Integration with CORTEX Investigation System
"""
        
        return AgentResponse(
            success=True,
            result={},
            message=help_message,
            needs_user_input=False
        )
    
    def _extract_file_path(self, query: str, context: Dict[str, Any]) -> Optional[str]:
        """Extract file path from query or context"""
        
        if context and 'file_path' in context:
            return context['file_path']
        
        # Extract from query (after 'import rca')
        import re
        match = re.search(r'import\s+rca\s+(.+?)(?:\s|$)', query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _extract_analysis_id(self, query: str) -> Optional[str]:
        """Extract analysis ID from query"""
        
        import re
        
        # Try pattern: "analyze rca [id]"
        match = re.search(r'(?:analyze|answer|report|show)\s+rca\s+([^\s:]+)', query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        # Try pattern: "rca [id]"
        match = re.search(r'rca\s+([^\s:]+)', query, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        
        return None
    
    def _extract_answer(self, query: str) -> Optional[str]:
        """Extract answer from query"""
        
        # Answer typically comes after colon
        if ':' in query:
            parts = query.split(':', 1)
            return parts[1].strip()
        
        return None
    
    def _format_import_result(self, result: Dict[str, Any]) -> str:
        """Format import result message"""
        
        if not result['success']:
            return f"❌ Import failed: {result.get('error', 'Unknown error')}"
        
        message = f"""✅ RCA Document Imported Successfully

**Analysis ID:** {result['analysis_id']}
**Status:** {result['status']}
**File:** {result['analysis_file']}

### Next Steps

"""
        
        for i, step in enumerate(result.get('next_steps', []), 1):
            message += f"{i}. {step}\n"
        
        return message
    
    def _format_list_result(self, result: Dict[str, Any]) -> str:
        """Format list of active RCAs"""
        
        if result['count'] == 0:
            return "No active RCA analyses found."
        
        message = f"**Active RCA Analyses ({result['count']})**\n\n"
        
        for analysis in result['analyses']:
            message += f"- **{analysis['analysis_id']}** - {analysis['title']}\n"
            message += f"  Status: {analysis['status']} | Updated: {analysis['updated']}\n\n"
        
        return message
    
    def _format_analysis_start(self, result: Dict[str, Any]) -> str:
        """Format 5 Whys analysis start message"""
        
        if not result['success']:
            return f"❌ {result.get('error', 'Could not start analysis')}\n\n{result.get('suggestion', '')}"
        
        message = f"""## 🔍 5 Whys Analysis Started

**Analysis ID:** {result['analysis_id']}
**Incident:** {result['context']['incident_title']}
**Severity:** {result['context']['severity']}

---

### {result['question']}

**Instructions:** {result['instruction']}

### Suggestions (based on similar incidents):

"""
        
        for i, suggestion in enumerate(result.get('suggestions', []), 1):
            message += f"{i}. {suggestion}\n"
        
        message += f"\n\n**To answer:** `answer rca {result['analysis_id']}: [your answer]`"
        
        return message
    
    def _format_why_response(self, result: Dict[str, Any]) -> str:
        """Format Why question response"""
        
        if not result['success']:
            return f"❌ {result.get('error', 'Could not process answer')}"
        
        if 'root_cause' in result:
            message = f"""## ✅ Root Cause Identified

**Confidence:** {result['confidence']:.0%}
**Category:** {result['category']}

### Root Cause

{result['root_cause']}

### Causal Chain

"""
            for chain_item in result.get('causal_chain', []):
                message += f"- {chain_item}\n"
            
            message += "\n### Next Steps\n\n"
            for i, step in enumerate(result.get('next_steps', []), 1):
                message += f"{i}. {step}\n"
            
            return message
        
        # Continue with next Why
        message = f"""## Progress: {result.get('progress', 'In Progress')}

**Previous Answer Confidence:** {result.get('previous_answer_confidence', 0):.0%}

---

### {result['question']}

### Suggestions:

"""
        
        for i, suggestion in enumerate(result.get('suggestions', []), 1):
            message += f"{i}. {suggestion}\n"
        
        message += "\n### Causal Chain So Far\n\n"
        
        for chain_item in result.get('causal_chain', []):
            message += f"- {chain_item}\n"
        
        message += f"\n\n**To answer:** `answer rca {result['analysis_id']}: [your answer]`"
        
        return message
    
    def _format_report_result(self, result: Dict[str, Any]) -> str:
        """Format report generation result"""
        
        if not result['success']:
            return f"❌ Report generation failed: {result.get('error', 'Unknown error')}"
        
        message = f"""## 📊 Executive Report Generated

**Analysis ID:** {result['analysis_id']}
**Report File:** {result['report_file']}
**Sections:** {result['sections']}
**Status:** {result['status']}

### Next Steps

"""
        
        for i, step in enumerate(result.get('next_steps', []), 1):
            message += f"{i}. {step}\n"
        
        message += """

### Report Ready

The executive report is formatted for senior leadership and includes:
- Executive Summary
- Incident Timeline
- Root Cause Analysis (5 Whys)
- Impact Assessment
- Corrective Actions
- Prevention Strategy
- Recommendations

**The report is ready to share with stakeholders.**
"""
        
        return message
