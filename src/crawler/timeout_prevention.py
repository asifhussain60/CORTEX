"""
CORTEX Timeout Prevention System
Prevents crawler timeouts with time budgets and graceful degradation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import time
from typing import Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum


class TimeoutStrategy(Enum):
    """Strategies for handling timeout scenarios"""
    GRACEFUL_STOP = "GRACEFUL_STOP"          # Stop at chunk boundary
    COMPLETE_CHUNK = "COMPLETE_CHUNK"        # Finish current chunk
    IMMEDIATE_STOP = "IMMEDIATE_STOP"        # Stop immediately
    EXTEND_BUDGET = "EXTEND_BUDGET"          # Request extension


@dataclass
class TimeoutConfig:
    """Configuration for timeout prevention"""
    max_time_seconds: int
    warning_threshold: float  # 0.0 to 1.0 (e.g., 0.8 = 80%)
    strategy: TimeoutStrategy
    allow_extension: bool
    max_extensions: int


@dataclass
class TimeoutWarning:
    """Warning when approaching timeout"""
    elapsed_seconds: float
    remaining_seconds: float
    percentage_used: float
    files_processed: int
    estimated_completion_time: float
    will_timeout: bool
    recommended_action: str


class TimeoutPreventor:
    """
    Prevents crawler timeouts through monitoring and graceful degradation
    
    Features:
    - Real-time budget monitoring
    - Early warning system (80% threshold)
    - Graceful degradation strategies
    - Checkpoint-based recovery
    - Time extension requests
    """
    
    def __init__(self, config: TimeoutConfig):
        """
        Initialize timeout preventor
        
        Args:
            config: Timeout configuration
        """
        self.config = config
        self.start_time: Optional[float] = None
        self.extensions_used = 0
        self.warnings_issued = []
        self.last_checkpoint_time: Optional[float] = None
    
    def start_timer(self) -> None:
        """Start the timeout timer"""
        self.start_time = time.time()
        self.last_checkpoint_time = self.start_time
    
    def check_timeout(self, files_processed: int, files_total: int) -> Optional[TimeoutWarning]:
        """
        Check if timeout is approaching
        
        Args:
            files_processed: Files processed so far
            files_total: Total files to process
        
        Returns:
            TimeoutWarning if timeout approaching, None otherwise
        """
        if self.start_time is None:
            return None
        
        elapsed = time.time() - self.start_time
        remaining = self.config.max_time_seconds - elapsed
        percentage_used = elapsed / self.config.max_time_seconds
        
        # Check if warning threshold exceeded
        if percentage_used >= self.config.warning_threshold:
            # Estimate completion time
            if files_processed > 0:
                rate = elapsed / files_processed
                estimated_completion = rate * files_total
            else:
                estimated_completion = float('inf')
            
            will_timeout = estimated_completion > self.config.max_time_seconds
            
            # Determine recommended action
            if will_timeout:
                if self.config.allow_extension and self.extensions_used < self.config.max_extensions:
                    recommended_action = "Request time extension"
                elif self.config.strategy == TimeoutStrategy.GRACEFUL_STOP:
                    recommended_action = "Stop at next chunk boundary"
                elif self.config.strategy == TimeoutStrategy.COMPLETE_CHUNK:
                    recommended_action = "Complete current chunk and stop"
                else:
                    recommended_action = "Reduce sample rate and continue"
            else:
                recommended_action = "Continue with current strategy"
            
            warning = TimeoutWarning(
                elapsed_seconds=elapsed,
                remaining_seconds=remaining,
                percentage_used=percentage_used,
                files_processed=files_processed,
                estimated_completion_time=estimated_completion,
                will_timeout=will_timeout,
                recommended_action=recommended_action
            )
            
            self.warnings_issued.append(warning)
            return warning
        
        return None
    
    def should_stop(self) -> bool:
        """
        Check if crawling should stop due to timeout
        
        Returns:
            True if should stop
        """
        if self.start_time is None:
            return False
        
        elapsed = time.time() - self.start_time
        return elapsed >= self.config.max_time_seconds
    
    def request_extension(self, additional_seconds: int) -> bool:
        """
        Request additional time budget
        
        Args:
            additional_seconds: Additional time requested
        
        Returns:
            True if extension granted
        """
        if not self.config.allow_extension:
            return False
        
        if self.extensions_used >= self.config.max_extensions:
            return False
        
        # Grant extension
        self.config.max_time_seconds += additional_seconds
        self.extensions_used += 1
        return True
    
    def create_timeout_checkpoint(self) -> dict:
        """
        Create checkpoint when timeout occurs
        
        Returns:
            Checkpoint data for resumption
        """
        if self.start_time is None:
            return {}
        
        return {
            'elapsed_time': time.time() - self.start_time,
            'warnings_issued': len(self.warnings_issued),
            'extensions_used': self.extensions_used,
            'final_strategy': self.config.strategy.value,
            'checkpoint_hash': self._generate_checkpoint_hash()
        }
    
    def format_warning(self, warning: TimeoutWarning) -> str:
        """
        Format timeout warning for user display
        
        Args:
            warning: Timeout warning
        
        Returns:
            Formatted warning string
        """
        lines = [
            f"⚠️ **Timeout Warning**",
            f"   Time Used: {warning.percentage_used * 100:.0f}% ({warning.elapsed_seconds:.0f}s / {self.config.max_time_seconds}s)",
            f"   Time Remaining: {warning.remaining_seconds:.0f}s",
            f"   Files Processed: {warning.files_processed:,}",
            ""
        ]
        
        if warning.will_timeout:
            lines.extend([
                f"⏱️ **Timeout Likely:**",
                f"   Estimated completion: {warning.estimated_completion_time:.0f}s",
                f"   Exceeds budget by: {warning.estimated_completion_time - self.config.max_time_seconds:.0f}s",
                "",
                f"💡 **Recommended Action:** {warning.recommended_action}"
            ])
        else:
            lines.extend([
                f"✅ **On Track:**",
                f"   Estimated completion: {warning.estimated_completion_time:.0f}s",
                f"   Within budget"
            ])
        
        return "\n".join(lines)
    
    def format_timeout_report(self) -> str:
        """
        Format final timeout report
        
        Returns:
            Formatted report string
        """
        if self.start_time is None:
            return "No timing data available"
        
        elapsed = time.time() - self.start_time
        
        lines = [
            f"⏱️ **Timeout Prevention Report**",
            f"   Total Time: {elapsed:.1f}s / {self.config.max_time_seconds}s",
            f"   Budget Used: {(elapsed / self.config.max_time_seconds) * 100:.0f}%",
            f"   Warnings Issued: {len(self.warnings_issued)}",
            f"   Extensions Used: {self.extensions_used} / {self.config.max_extensions}",
            f"   Strategy: {self.config.strategy.value.replace('_', ' ').title()}"
        ]
        
        if elapsed > self.config.max_time_seconds:
            lines.append(f"   ⚠️ Budget exceeded by {elapsed - self.config.max_time_seconds:.1f}s")
        else:
            lines.append(f"   ✅ Completed within budget")
        
        return "\n".join(lines)
    
    def _generate_checkpoint_hash(self) -> str:
        """
        Generate checkpoint hash
        
        Returns:
            Checkpoint hash
        """
        import hashlib
        data = f"timeout_{time.time()}_{self.extensions_used}"
        return hashlib.md5(data.encode()).hexdigest()[:8]


class ProgressiveDisclosure:
    """
    Progressive disclosure of results during long-running operations
    
    Shows intermediate results while crawling continues in background
    """
    
    def __init__(self, update_callback: Optional[Callable[[str], None]] = None):
        """
        Initialize progressive disclosure
        
        Args:
            update_callback: Optional callback for result updates
        """
        self.update_callback = update_callback
        self.disclosed_results = []
    
    def disclose_batch(self, batch_results: dict, files_processed: int, files_total: int) -> None:
        """
        Disclose batch of results progressively
        
        Args:
            batch_results: Results from current batch
            files_processed: Files processed so far
            files_total: Total files
        """
        disclosure = {
            'timestamp': time.time(),
            'files_processed': files_processed,
            'progress_pct': (files_processed / files_total) * 100,
            'batch_results': batch_results
        }
        
        self.disclosed_results.append(disclosure)
        
        if self.update_callback:
            formatted = self._format_disclosure(disclosure, files_total)
            self.update_callback(formatted)
    
    def _format_disclosure(self, disclosure: dict, files_total: int) -> str:
        """
        Format disclosure for display
        
        Args:
            disclosure: Disclosure data
            files_total: Total files
        
        Returns:
            Formatted disclosure string
        """
        progress_pct = disclosure['progress_pct']
        files_processed = disclosure['files_processed']
        
        batch = disclosure['batch_results']
        
        return (
            f"📊 **Progress Update** ({progress_pct:.0f}% - {files_processed}/{files_total} files)\n"
            f"   Modules found: {len(batch.get('modules', []))}\n"
            f"   Relationships: {len(batch.get('relationships', {}))}\n"
        )
    
    def get_cumulative_results(self) -> dict:
        """
        Get cumulative results from all disclosures
        
        Returns:
            Combined results
        """
        combined = {
            'modules': set(),
            'relationships': {},
            'total_loc': 0
        }
        
        for disclosure in self.disclosed_results:
            batch = disclosure['batch_results']
            
            if 'modules' in batch:
                combined['modules'].update(batch['modules'])
            
            if 'relationships' in batch:
                combined['relationships'].update(batch['relationships'])
            
            if 'total_loc' in batch:
                combined['total_loc'] += batch['total_loc']
        
        combined['modules'] = list(combined['modules'])
        return combined
