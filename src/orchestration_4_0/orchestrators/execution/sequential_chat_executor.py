"""
Sequential Chat Executor for Execution Orchestrator

Executes orchestrators in sequence (pipeline pattern).

Author: Asif Hussain
Version: 1.0
"""

from typing import Dict, Any, List, Optional
import logging
import asyncio


class SequentialChatExecutor:
    """
    Execute phases as sequential chat chain.
    
    Pattern: Writer → Editor → Publisher
    Each orchestrator receives previous output as context.
    
    Use cases:
    - Code review workflow (security → quality → performance → style)
    - Content creation pipeline
    - Multi-stage validation
    """
    
    def __init__(
        self,
        orchestrator: Any,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize sequential chat executor.
        
        Args:
            orchestrator: Parent orchestrator with sub_orchestrators
            logger: Optional logger instance
        """
        self.orchestrator = orchestrator
        self.logger = logger or logging.getLogger(__name__)
    
    async def execute_sequential_chat(
        self,
        orchestrator_names: List[str],
        context: Dict[str, Any],
        stop_on_error: bool = True
    ) -> Dict[str, Any]:
        """
        Execute orchestrators in sequence.
        
        Args:
            orchestrator_names: List of orchestrator names in execution order
            context: Initial context
            stop_on_error: Stop pipeline if error occurs (default: True)
            
        Returns:
            Final result with all intermediate results
        """
        self.logger.info(
            f"🎭 Sequential chat: {len(orchestrator_names)} orchestrators"
        )
        
        result = context.copy()
        result['sequential_results'] = []
        
        for i, orch_name in enumerate(orchestrator_names, 1):
            self.logger.info(f"  [{i}/{len(orchestrator_names)}] Executing: {orch_name}")
            
            # Get orchestrator
            if orch_name not in self.orchestrator.sub_orchestrators:
                error_msg = f"Sub-orchestrator not found: {orch_name}"
                self.logger.error(f"❌ {error_msg}")
                
                if stop_on_error:
                    return {
                        'success': False,
                        'error': error_msg,
                        'completed_steps': orchestrator_names[:i-1],
                        'failed_at': orch_name,
                        'sequential_results': result.get('sequential_results', [])
                    }
                else:
                    result['sequential_results'].append({
                        'orchestrator': orch_name,
                        'success': False,
                        'error': error_msg
                    })
                    continue
            
            # Execute orchestrator
            try:
                sub_orchestrator = self.orchestrator.sub_orchestrators[orch_name]
                sub_result = await self._execute_with_timeout(
                    sub_orchestrator,
                    result
                )
                
                # Check for errors
                if not sub_result.get('success', True):
                    error_msg = sub_result.get('error', 'Unknown error')
                    self.logger.error(
                        f"❌ Sequential chat failed at {orch_name}: {error_msg}"
                    )
                    
                    if stop_on_error:
                        return {
                            'success': False,
                            'error': error_msg,
                            'completed_steps': orchestrator_names[:i-1],
                            'failed_at': orch_name,
                            'sequential_results': result.get('sequential_results', [])
                        }
                
                # Merge result into context
                result.update(sub_result)
                result['sequential_results'].append({
                    'orchestrator': orch_name,
                    'success': sub_result.get('success', True),
                    'output': sub_result
                })
                
                self.logger.info(f"  ✅ {orch_name} completed")
                
            except Exception as e:
                error_msg = str(e)
                self.logger.error(f"❌ Error in {orch_name}: {error_msg}")
                
                if stop_on_error:
                    return {
                        'success': False,
                        'error': error_msg,
                        'completed_steps': orchestrator_names[:i-1],
                        'failed_at': orch_name,
                        'sequential_results': result.get('sequential_results', [])
                    }
                else:
                    result['sequential_results'].append({
                        'orchestrator': orch_name,
                        'success': False,
                        'error': error_msg
                    })
        
        self.logger.info(
            f"✅ Sequential chat complete: {len(orchestrator_names)} orchestrators"
        )
        
        return {
            'success': True,
            'completed_steps': orchestrator_names[:len(orchestrator_names)],
            'sequential_results': result.get('sequential_results', []),
            'final_context': result
        }
    
    async def _execute_with_timeout(
        self,
        orchestrator: Any,
        context: Dict[str, Any],
        timeout_seconds: int = 300
    ) -> Dict[str, Any]:
        """
        Execute orchestrator with timeout.
        
        Args:
            orchestrator: Orchestrator to execute
            context: Execution context
            timeout_seconds: Timeout in seconds (default: 5 minutes)
            
        Returns:
            Orchestrator result
            
        Raises:
            asyncio.TimeoutError: If execution exceeds timeout
        """
        try:
            result = await asyncio.wait_for(
                orchestrator.execute(context),
                timeout=timeout_seconds
            )
            return result
        except asyncio.TimeoutError:
            raise TimeoutError(
                f"Orchestrator execution exceeded {timeout_seconds}s timeout"
            )
