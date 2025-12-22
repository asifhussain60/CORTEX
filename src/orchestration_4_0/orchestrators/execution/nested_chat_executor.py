"""
Nested Chat Executor for Execution Orchestrator

Executes hierarchical teams of orchestrators.

Author: Asif Hussain
Version: 1.0
"""

from typing import Dict, Any, List, Optional
import logging


class NestedChatExecutor:
    """
    Execute hierarchical teams of orchestrators.
    
    Pattern: Frontend Team + Backend Team → Integration Team
    
    Use cases:
    - System maintenance (healthcheck team + optimization team + docs team)
    - Complex feature development with sub-teams
    - Cross-domain coordination
    """
    
    def __init__(
        self,
        orchestrator: Any,
        parallel_executor: Any,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize nested chat executor.
        
        Args:
            orchestrator: Parent orchestrator with sub_orchestrators
            parallel_executor: ParallelGroupChatExecutor for team execution
            logger: Optional logger instance
        """
        self.orchestrator = orchestrator
        self.parallel_executor = parallel_executor
        self.logger = logger or logging.getLogger(__name__)
    
    async def execute_nested_chat(
        self,
        team_structure: Dict[str, List[str]],
        context: Dict[str, Any],
        synthesize_per_team: bool = True,
        final_synthesis: bool = True
    ) -> Dict[str, Any]:
        """
        Execute nested teams.
        
        Args:
            team_structure: Dict of team_name -> list of orchestrator names
                Example:
                {
                    'frontend_team': ['ReactOrch', 'CSSOrch'],
                    'backend_team': ['APIOrch', 'DatabaseOrch'],
                    'integration_team': ['E2ETestOrch']
                }
            context: Shared context for all teams
            synthesize_per_team: Synthesize results within each team
            final_synthesis: Synthesize results across all teams
            
        Returns:
            Nested execution result with team results
        """
        self.logger.info(
            f"🎭 Nested chat: {len(team_structure)} teams"
        )
        
        team_results = {}
        
        # Execute each team
        for team_name, orchestrator_names in team_structure.items():
            self.logger.info(f"  Executing team: {team_name} ({len(orchestrator_names)} orchestrators)")
            
            if len(orchestrator_names) == 0:
                self.logger.warning(f"⚠️ Team {team_name} has no orchestrators")
                team_results[team_name] = {
                    'success': False,
                    'error': 'No orchestrators in team'
                }
                continue
            
            elif len(orchestrator_names) == 1:
                # Single orchestrator - execute directly
                orch_name = orchestrator_names[0]
                
                if orch_name not in self.orchestrator.sub_orchestrators:
                    self.logger.error(f"❌ Orchestrator not found: {orch_name}")
                    team_results[team_name] = {
                        'success': False,
                        'error': f'Orchestrator not found: {orch_name}'
                    }
                    continue
                
                try:
                    sub_orchestrator = self.orchestrator.sub_orchestrators[orch_name]
                    result = await sub_orchestrator.execute(context)
                    team_results[team_name] = result
                    self.logger.info(f"  ✅ Team {team_name} completed")
                except Exception as e:
                    self.logger.error(f"❌ Team {team_name} failed: {e}")
                    team_results[team_name] = {
                        'success': False,
                        'error': str(e)
                    }
            
            else:
                # Multiple orchestrators - use parallel group chat
                try:
                    result = await self.parallel_executor.execute_parallel_group_chat(
                        orchestrator_names=orchestrator_names,
                        context=context,
                        manager_prompt=f"Synthesize {team_name} results",
                        synthesize=synthesize_per_team
                    )
                    team_results[team_name] = result
                    self.logger.info(f"  ✅ Team {team_name} completed")
                except Exception as e:
                    self.logger.error(f"❌ Team {team_name} failed: {e}")
                    team_results[team_name] = {
                        'success': False,
                        'error': str(e)
                    }
        
        # Final synthesis across teams
        if final_synthesis:
            final_result = await self._synthesize_team_results(
                team_results,
                team_structure
            )
        else:
            final_result = {
                'team_results': team_results
            }
        
        # Calculate overall success
        all_successful = all(
            result.get('success', False)
            for result in team_results.values()
        )
        
        self.logger.info(
            f"✅ Nested chat complete: {len(team_structure)} teams "
            f"({'all successful' if all_successful else 'some failures'})"
        )
        
        return {
            'success': all_successful,
            'team_results': team_results,
            'final_synthesis': final_result,
            'total_teams': len(team_structure),
            'successful_teams': sum(
                1 for result in team_results.values()
                if result.get('success', False)
            )
        }
    
    async def _synthesize_team_results(
        self,
        team_results: Dict[str, Dict[str, Any]],
        team_structure: Dict[str, List[str]]
    ) -> Dict[str, Any]:
        """
        Synthesize results across all teams.
        
        Args:
            team_results: Results from each team
            team_structure: Original team structure
            
        Returns:
            Synthesized cross-team result
        """
        self.logger.debug(f"🤔 Synthesizing {len(team_results)} team results")
        
        # Simple synthesis: aggregate key findings
        # In production, would use LLM for intelligent cross-team synthesis
        
        synthesis = {
            'total_teams': len(team_results),
            'successful_teams': [],
            'failed_teams': [],
            'key_findings': [],
            'cross_team_recommendations': []
        }
        
        for team_name, result in team_results.items():
            if result.get('success', False):
                synthesis['successful_teams'].append(team_name)
                
                # Extract key findings
                if 'synthesized_results' in result:
                    synth_results = result['synthesized_results']
                    if 'common_findings' in synth_results:
                        for finding in synth_results['common_findings']:
                            synthesis['key_findings'].append({
                                'team': team_name,
                                'finding': finding
                            })
            else:
                synthesis['failed_teams'].append({
                    'team': team_name,
                    'error': result.get('error', 'Unknown error')
                })
        
        # Generate cross-team recommendations
        # In production, would analyze dependencies and interactions
        if len(synthesis['successful_teams']) > 1:
            synthesis['cross_team_recommendations'].append({
                'type': 'integration',
                'recommendation': f"Coordinate between {', '.join(synthesis['successful_teams'])}"
            })
        
        self.logger.info(
            f"✅ Cross-team synthesis complete: {len(synthesis['key_findings'])} findings"
        )
        
        return synthesis
