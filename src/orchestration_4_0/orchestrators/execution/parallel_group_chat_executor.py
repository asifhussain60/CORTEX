"""
Parallel Group Chat Executor for Execution Orchestrator

Executes orchestrators in parallel with group chat synthesis.

Author: Asif Hussain
Version: 1.0
"""

from typing import Dict, Any, List, Optional
import logging
import asyncio
import json


class ParallelGroupChatExecutor:
    """
    Execute phases in parallel with group chat synthesis.
    
    Pattern: Multiple code reviewers → Manager synthesizes feedback
    
    Use cases:
    - Planning System parallel analysis (complexity + risk + domain + integration)
    - Simultaneous document generation
    - Multi-perspective code analysis
    """
    
    def __init__(
        self,
        orchestrator: Any,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize parallel group chat executor.
        
        Args:
            orchestrator: Parent orchestrator with sub_orchestrators
            logger: Optional logger instance
        """
        self.orchestrator = orchestrator
        self.logger = logger or logging.getLogger(__name__)
    
    async def execute_parallel_group_chat(
        self,
        orchestrator_names: List[str],
        context: Dict[str, Any],
        manager_prompt: Optional[str] = None,
        synthesize: bool = True
    ) -> Dict[str, Any]:
        """
        Execute orchestrators in parallel, synthesize results with manager.
        
        Args:
            orchestrator_names: List of orchestrator names to execute in parallel
            context: Shared context for all orchestrators
            manager_prompt: Optional prompt for result synthesis
            synthesize: Whether to synthesize results (default: True)
            
        Returns:
            Synthesized result or raw results
        """
        self.logger.info(
            f"🎭 Group chat: {len(orchestrator_names)} orchestrators in parallel"
        )
        
        # Execute all orchestrators in parallel
        tasks = []
        for orch_name in orchestrator_names:
            if orch_name in self.orchestrator.sub_orchestrators:
                sub_orchestrator = self.orchestrator.sub_orchestrators[orch_name]
                tasks.append(self._execute_with_name(sub_orchestrator, orch_name, context))
            else:
                self.logger.warning(f"⚠️ Sub-orchestrator not found: {orch_name}")
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        successful_results = []
        failed_results = []
        
        for i, result in enumerate(results):
            orch_name = orchestrator_names[i] if i < len(orchestrator_names) else f"unknown_{i}"
            
            if isinstance(result, Exception):
                self.logger.error(f"❌ {orch_name} failed: {result}")
                failed_results.append({
                    'orchestrator': orch_name,
                    'success': False,
                    'error': str(result)
                })
            elif isinstance(result, dict):
                if result.get('success', True):
                    successful_results.append({
                        'orchestrator': orch_name,
                        'success': True,
                        'output': result
                    })
                    self.logger.info(f"✅ {orch_name} completed")
                else:
                    failed_results.append({
                        'orchestrator': orch_name,
                        'success': False,
                        'error': result.get('error', 'Unknown error')
                    })
                    self.logger.warning(f"⚠️ {orch_name} reported failure")
        
        # Manager synthesizes results if requested
        if synthesize and successful_results:
            synthesized = await self._synthesize_results(
                successful_results,
                manager_prompt or "Synthesize parallel execution results"
            )
            
            return {
                'success': len(failed_results) == 0,
                'synthesized_results': synthesized,
                'raw_results': successful_results,
                'failed_results': failed_results,
                'total_orchestrators': len(orchestrator_names),
                'successful_count': len(successful_results),
                'failed_count': len(failed_results)
            }
        else:
            return {
                'success': len(failed_results) == 0,
                'raw_results': successful_results,
                'failed_results': failed_results,
                'total_orchestrators': len(orchestrator_names),
                'successful_count': len(successful_results),
                'failed_count': len(failed_results)
            }
    
    async def _execute_with_name(
        self,
        orchestrator: Any,
        name: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute orchestrator and include name in result.
        
        Args:
            orchestrator: Orchestrator to execute
            name: Orchestrator name
            context: Execution context
            
        Returns:
            Orchestrator result with name
        """
        try:
            result = await orchestrator.execute(context)
            result['_orchestrator_name'] = name
            return result
        except Exception as e:
            self.logger.error(f"❌ Error in {name}: {e}")
            raise
    
    async def _synthesize_results(
        self,
        results: List[Dict[str, Any]],
        manager_prompt: str
    ) -> Dict[str, Any]:
        """
        Manager synthesizes parallel results.
        
        This is a simplified version. In production, this would use LLM
        to intelligently synthesize multiple perspectives.
        
        Args:
            results: List of successful results
            manager_prompt: Synthesis instructions
            
        Returns:
            Synthesized result
        """
        self.logger.debug(f"🤔 Synthesizing {len(results)} results")
        
        # Simple synthesis: merge all results
        # In production, would use LLM for intelligent synthesis
        
        synthesized = {
            'synthesis_prompt': manager_prompt,
            'perspectives': len(results),
            'merged_recommendations': [],
            'common_findings': [],
            'conflicts': []
        }
        
        # Extract recommendations from each result
        for result in results:
            orch_name = result.get('orchestrator', 'unknown')
            output = result.get('output', {})
            
            if 'recommendations' in output:
                for rec in output['recommendations']:
                    synthesized['merged_recommendations'].append({
                        'source': orch_name,
                        'recommendation': rec
                    })
            
            if 'findings' in output:
                for finding in output['findings']:
                    synthesized['common_findings'].append({
                        'source': orch_name,
                        'finding': finding
                    })
        
        # Detect conflicts (simple heuristic: opposite recommendations)
        # In production, would use semantic analysis
        
        self.logger.info(
            f"✅ Synthesis complete: {len(synthesized['merged_recommendations'])} recommendations"
        )
        
        return synthesized
