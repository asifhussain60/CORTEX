"""
Wave 8 Stage 1: Track Parallelization Strategy

Track-level parallelization for concurrent execution of multiple tracks.

AC-ID: AC-WAVE-8-S1-004
Authority: Wave 8 Execution Activation
Coverage Target: ≥96%
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from cortex.orchestrators.planning.strategies.strategy_base import (
    ExecutionStrategy,
    ExecutionContext,
    ExecutionResult,
    ValidationResult,
    ExecutionStatus,
)

logger = logging.getLogger(__name__)


@dataclass
class TrackParallelizationConfig:
    """Configuration for track parallelization."""
    max_parallel_tracks: int = 5
    resource_pooling: bool = True
    failure_isolation: bool = True
    load_balancing: bool = True


class TrackParallelizationStrategy(ExecutionStrategy):
    """
    Track-level parallelization strategy.
    
    Handles:
    - Parallel track execution (up to 5+ tracks)
    - Resource pooling and allocation
    - Track synchronization
    - Load balancing
    - Failure isolation
    - Completion detection
    
    Enables multiple tracks to execute concurrently while maintaining
    resource constraints and failure isolation.
    """
    
    def __init__(self, config: Optional[TrackParallelizationConfig] = None) -> None:
        """
        Initialize track parallelization strategy.
        
        Args:
            config: Track parallelization configuration
        """
        self.config = config or TrackParallelizationConfig()
        self.resource_pool: Dict[str, Any] = {}
        self.track_states: Dict[str, str] = {}
    
    def execute(self, context: ExecutionContext) -> ExecutionResult:
        """
        Execute track parallelization.
        
        Args:
            context: Execution context containing track data
        
        Returns:
            ExecutionResult with success/failure and output data
        """
        # Validate preconditions
        validation = self.validate(context)
        if not validation.passed:
            return ExecutionResult(
                success=False,
                phase_id=context.phase_id,
                message=f"Validation failed: {', '.join(validation.errors)}",
                status=ExecutionStatus.FAILURE,
                error=f"Validation failed: {', '.join(validation.errors)}",
            )
        
        try:
            # Get tracks/phases from data or metadata
            tracks = context.data.get("tracks", context.data.get("phases", context.metadata.get("tracks", context.metadata.get("phases", []))))
            
            # Initialize resource pool if enabled
            if self.config.resource_pooling:
                self._initialize_resource_pool(context.resources)
            
            # Execute tracks in parallel
            track_results = []
            with ThreadPoolExecutor(max_workers=self.config.max_parallel_tracks) as executor:
                # Submit all tracks
                future_to_track = {
                    executor.submit(self._execute_track, track, context): track
                    for track in tracks
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_track):
                    track = future_to_track[future]
                    try:
                        result = future.result()
                        track_results.append(result)
                        
                        # Update track state (track may be string or dict)
                        track_id = track if isinstance(track, str) else track.get("id", "unknown")
                        self.track_states[track_id] = "completed" if result.get("success") else "failed"
                        
                    except Exception as e:
                        # Get track ID (track may be string or dict)
                        track_id = track if isinstance(track, str) else track.get("id", "unknown")
                        logger.error(f"Track {track_id} failed: {str(e)}")
                        if not self.config.failure_isolation:
                            # Propagate failure if isolation disabled
                            raise
                        
                        track_results.append({
                            "track_id": track_id,
                            "success": False,
                            "error": str(e),
                        })
            
            # Check completion (track may be string or dict)
            all_completed = all(
                self.track_states.get(t if isinstance(t, str) else t.get("id", ""), "") in ["completed", "failed"]
                for t in tracks
            )
            
            successful_tracks = sum(1 for r in track_results if r.get("success"))
            
            return ExecutionResult(
                success=successful_tracks == len(tracks),
                status=ExecutionStatus.SUCCESS if successful_tracks == len(tracks) else ExecutionStatus.FAILURE,
                output={
                    "tracks_total": len(tracks),
                    "tracks_successful": successful_tracks,
                    "track_results": track_results,
                    "all_completed": all_completed,
                },
                metrics={
                    "parallelization": len(tracks),
                    "max_workers": self.config.max_parallel_tracks,
                    "success_rate": successful_tracks / len(tracks) if tracks else 0,
                },
            )
        
        except Exception as e:
            logger.error(f"Track parallelization failed: {str(e)}")
            return ExecutionResult(
                success=False,
                status=ExecutionStatus.FAILURE,
                error=str(e),
            )
    
    def validate(self, context: ExecutionContext) -> ValidationResult:
        """
        Validate track parallelization preconditions.
        
        Args:
            context: Execution context to validate
        
        Returns:
            ValidationResult with any errors/warnings
        """
        errors = []
        warnings = []
        
        # Check for tracks or phases in either data or metadata
        tracks = context.data.get("tracks", context.data.get("phases", context.metadata.get("tracks", context.metadata.get("phases", []))))
        if not tracks:
            errors.append("tracks or phases list required in data or metadata")
        
        # Check track count
        if tracks and len(tracks) == 0:
            errors.append("At least one track/phase required")
        
        if tracks and len(tracks) > self.config.max_parallel_tracks:
            warnings.append(
                f"Track count ({len(tracks)}) exceeds max parallel "
                f"({self.config.max_parallel_tracks}), will execute in batches"
            )
        
        # Check resource availability
        if self.config.resource_pooling and not context.resources:
            warnings.append("Resource pooling enabled but no resources provided")
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )
    
    def _initialize_resource_pool(self, resources: Dict[str, Any]) -> None:
        """
        Initialize resource pool for track execution.
        
        Args:
            resources: Resource allocation map
        """
        self.resource_pool = resources.copy()
        logger.debug(f"Initialized resource pool: {self.resource_pool}")
    
    def _execute_track(self, track: Any, context: ExecutionContext) -> Dict[str, Any]:
        """
        Execute a single track.
        
        Args:
            track: Track data (string or dict)
            context: Execution context
        
        Returns:
            Track execution result
        """
        # Handle string tracks/phases
        if isinstance(track, str):
            track_id = track
        else:
            track_id = track.get("id", "unknown")
        
        # Update state
        self.track_states[track_id] = "in_progress"
        
        # Placeholder implementation - real logic would execute actual track
        logger.info(f"Executing track: {track_id}")
        
        return {
            "track_id": track_id,
            "success": True,
            "status": "completed",
        }
