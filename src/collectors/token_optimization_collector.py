"""
CORTEX 3.0 - Token Optimization Metrics Collector
=================================================

Real-time collection of token usage and optimization metrics.
Monitors token reduction achievements and cost savings.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #3 (Week 1)
Effort: Part of 4 hours (core collectors implementation)
Target: Track token optimization progress in real-time
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from pathlib import Path
import json
import re
import logging

from .base_collector import BaseCollector, CollectorMetric, CollectorPriority


class TokenOptimizationCollector(BaseCollector):
    """
    Collects token usage and optimization metrics for CORTEX operations.
    
    Metrics collected:
    - Current token usage across prompts
    - Token reduction achievements (before/after optimization)
    - Cost savings calculations
    - Optimization effectiveness scores
    - File size reductions
    """
    
    def __init__(self, brain_path: str, workspace_root: str):
        super().__init__(
            collector_id="token_optimization",
            name="Token Optimization Metrics",
            priority=CollectorPriority.HIGH,
            collection_interval_seconds=120.0,  # Collect every 2 minutes
            brain_path=brain_path
        )
        self.workspace_root = Path(workspace_root)
        self.brain_path = Path(brain_path)
        
        # Token counting configuration
        self.prompt_directories = [
            "prompts/shared",
            "prompts/user", 
            ".github/prompts",
            "cortex-brain/response-templates"
        ]
        
        # Optimization tracking
        self.baseline_metrics = {}
        self.optimization_history = []
        
    def _initialize(self) -> bool:
        """Initialize token optimization collector"""
        try:
            # Verify workspace and brain paths exist
            if not self.workspace_root.exists():
                self.logger.error(f"Workspace root does not exist: {self.workspace_root}")
                return False
                
            if not self.brain_path.exists():
                self.logger.error(f"Brain path does not exist: {self.brain_path}")
                return False
            
            # Load baseline metrics if available
            self._load_baseline_metrics()
            
            self.logger.info("Token optimization collector initialized successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize token optimization collector: {e}")
            return False
    
    def _collect_metrics(self) -> List[CollectorMetric]:
        """Collect token optimization metrics"""
        metrics = []
        timestamp = datetime.now(timezone.utc)
        
        # Collect current token usage
        metrics.extend(self._collect_current_token_usage(timestamp))
        
        # Collect optimization achievements
        metrics.extend(self._collect_optimization_achievements(timestamp))
        
        # Collect cost savings metrics
        metrics.extend(self._collect_cost_savings(timestamp))
        
        # Collect file size metrics
        metrics.extend(self._collect_file_size_metrics(timestamp))
        
        return metrics
    
    def _collect_current_token_usage(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect current token usage across prompt files"""
        metrics = []
        
        try:
            total_tokens = 0
            file_count = 0
            
            for prompt_dir in self.prompt_directories:
                dir_path = self.workspace_root / prompt_dir
                if not dir_path.exists():
                    continue
                    
                dir_tokens, dir_files = self._count_tokens_in_directory(dir_path)
                total_tokens += dir_tokens
                file_count += dir_files
                
                # Per-directory metrics
                metrics.append(CollectorMetric(
                    name="token_usage_by_directory",
                    value=dir_tokens,
                    timestamp=timestamp,
                    tags={"directory": prompt_dir, "files": str(dir_files)},
                    metadata={"type": "token_count"}
                ))
            
            # Total token usage
            metrics.append(CollectorMetric(
                name="total_token_usage",
                value=total_tokens,
                timestamp=timestamp,
                tags={"type": "total", "files": str(file_count)},
                metadata={"directories_scanned": len(self.prompt_directories)}
            ))
            
            # Token density (tokens per file)
            if file_count > 0:
                metrics.append(CollectorMetric(
                    name="token_density",
                    value=round(total_tokens / file_count, 2),
                    timestamp=timestamp,
                    tags={"type": "density", "unit": "tokens_per_file"}
                ))
            
        except Exception as e:
            self.logger.warning(f"Failed to collect current token usage: {e}")
            
        return metrics
    
    def _collect_optimization_achievements(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect token reduction achievements"""
        metrics = []
        
        try:
            # Load optimization history from brain
            optimization_data = self._load_optimization_history()
            
            if optimization_data:
                # Calculate total reduction
                total_reduction_percent = optimization_data.get('total_reduction_percent', 0)
                metrics.append(CollectorMetric(
                    name="token_reduction_achievement_percent",
                    value=total_reduction_percent,
                    timestamp=timestamp,
                    tags={"type": "achievement", "unit": "percent"},
                    metadata={"baseline": "CORTEX 1.0"}
                ))
                
                # Tokens saved
                tokens_saved = optimization_data.get('tokens_saved', 0)
                metrics.append(CollectorMetric(
                    name="tokens_saved_total",
                    value=tokens_saved,
                    timestamp=timestamp,
                    tags={"type": "savings", "unit": "tokens"}
                ))
                
                # Optimization score (0-100)
                optimization_score = self._calculate_optimization_score()
                metrics.append(CollectorMetric(
                    name="optimization_effectiveness_score",
                    value=optimization_score,
                    timestamp=timestamp,
                    tags={"type": "score", "scale": "0-100"}
                ))
            
        except Exception as e:
            self.logger.warning(f"Failed to collect optimization achievements: {e}")
            
        return metrics
    
    def _collect_cost_savings(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect cost savings metrics"""
        metrics = []
        
        try:
            # Get current token usage
            current_tokens = self._get_total_current_tokens()
            
            # Calculate monthly cost at current usage
            # GitHub Copilot pricing: (input × 1.0 + output × 1.5) × $0.00001
            # Assume average 2000 output tokens per 2000 input tokens
            monthly_requests = 1000  # Assumed monthly usage
            
            input_cost = current_tokens * 1.0 * 0.00001
            output_cost = 2000 * 1.5 * 0.00001  # Assume 2000 output tokens
            cost_per_request = input_cost + output_cost
            monthly_cost = cost_per_request * monthly_requests
            
            metrics.append(CollectorMetric(
                name="estimated_monthly_cost_usd",
                value=round(monthly_cost, 2),
                timestamp=timestamp,
                tags={"type": "cost", "currency": "USD", "period": "monthly"},
                metadata={"assumptions": "1000 requests/month, 2000 output tokens avg"}
            ))
            
            # Calculate savings vs baseline (if available)
            baseline_tokens = self.baseline_metrics.get('total_tokens', current_tokens)
            if baseline_tokens > current_tokens:
                baseline_cost = (baseline_tokens * 1.0 + 2000 * 1.5) * 0.00001 * monthly_requests
                monthly_savings = baseline_cost - monthly_cost
                
                metrics.append(CollectorMetric(
                    name="estimated_monthly_savings_usd",
                    value=round(monthly_savings, 2),
                    timestamp=timestamp,
                    tags={"type": "savings", "currency": "USD", "period": "monthly"}
                ))
                
                # Annual savings
                metrics.append(CollectorMetric(
                    name="estimated_annual_savings_usd",
                    value=round(monthly_savings * 12, 2),
                    timestamp=timestamp,
                    tags={"type": "savings", "currency": "USD", "period": "annual"}
                ))
            
        except Exception as e:
            self.logger.warning(f"Failed to collect cost savings metrics: {e}")
            
        return metrics
    
    def _collect_file_size_metrics(self, timestamp: datetime) -> List[CollectorMetric]:
        """Collect file size reduction metrics"""
        metrics = []
        
        try:
            total_size_kb = 0
            largest_files = []
            
            for prompt_dir in self.prompt_directories:
                dir_path = self.workspace_root / prompt_dir
                if not dir_path.exists():
                    continue
                    
                for file_path in dir_path.rglob("*.md"):
                    if file_path.is_file():
                        size_kb = file_path.stat().st_size / 1024
                        total_size_kb += size_kb
                        largest_files.append((str(file_path.relative_to(self.workspace_root)), size_kb))
            
            # Sort and get top 5 largest files
            largest_files.sort(key=lambda x: x[1], reverse=True)
            top_files = largest_files[:5]
            
            metrics.append(CollectorMetric(
                name="total_prompt_files_size_kb",
                value=round(total_size_kb, 2),
                timestamp=timestamp,
                tags={"type": "file_size", "unit": "kb"}
            ))
            
            # Largest file metric
            if top_files:
                metrics.append(CollectorMetric(
                    name="largest_prompt_file_size_kb", 
                    value=round(top_files[0][1], 2),
                    timestamp=timestamp,
                    tags={"type": "file_size", "unit": "kb"},
                    metadata={"filename": top_files[0][0]}
                ))
            
        except Exception as e:
            self.logger.warning(f"Failed to collect file size metrics: {e}")
            
        return metrics
    
    def _count_tokens_in_directory(self, directory: Path) -> tuple[int, int]:
        """Count tokens in all markdown files in a directory"""
        total_tokens = 0
        file_count = 0
        
        try:
            for file_path in directory.rglob("*.md"):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            tokens = self._estimate_token_count(content)
                            total_tokens += tokens
                            file_count += 1
                    except Exception as e:
                        self.logger.debug(f"Could not read {file_path}: {e}")
                        
        except Exception as e:
            self.logger.warning(f"Error counting tokens in {directory}: {e}")
            
        return total_tokens, file_count
    
    def _estimate_token_count(self, text: str) -> int:
        """Estimate token count for text (approximate GPT tokenization)"""
        # Rough estimation: 1 token ≈ 4 characters for English text
        # More sophisticated tokenization could use tiktoken library
        
        # Clean text
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Rough token estimation
        char_count = len(text)
        estimated_tokens = char_count // 4
        
        return max(1, estimated_tokens)
    
    def _load_baseline_metrics(self) -> None:
        """Load baseline metrics for comparison"""
        try:
            baseline_file = self.brain_path / "optimization-baseline.json"
            if baseline_file.exists():
                with open(baseline_file, 'r') as f:
                    self.baseline_metrics = json.load(f)
                    self.logger.info("Loaded baseline metrics for token optimization")
        except Exception as e:
            self.logger.warning(f"Could not load baseline metrics: {e}")
            
    def _load_optimization_history(self) -> Dict[str, Any]:
        """Load optimization history from brain"""
        try:
            history_file = self.brain_path / "optimization-history.json"
            if history_file.exists():
                with open(history_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.debug(f"Could not load optimization history: {e}")
            
        return {}
    
    def _calculate_optimization_score(self) -> float:
        """Calculate overall optimization effectiveness score (0-100)"""
        try:
            score = 50.0  # Base score
            
            # Current vs baseline comparison
            current_tokens = self._get_total_current_tokens()
            baseline_tokens = self.baseline_metrics.get('total_tokens', current_tokens)
            
            if baseline_tokens > 0:
                reduction_ratio = (baseline_tokens - current_tokens) / baseline_tokens
                
                if reduction_ratio > 0.9:  # >90% reduction
                    score = 95
                elif reduction_ratio > 0.8:  # >80% reduction
                    score = 85
                elif reduction_ratio > 0.5:  # >50% reduction
                    score = 75
                elif reduction_ratio > 0.2:  # >20% reduction
                    score = 65
                elif reduction_ratio > 0:  # Some reduction
                    score = 60
                else:  # No reduction or increase
                    score = 40
            
            return score
            
        except Exception as e:
            self.logger.warning(f"Failed to calculate optimization score: {e}")
            return 50.0
    
    def _get_total_current_tokens(self) -> int:
        """Get total current token usage"""
        try:
            total_tokens = 0
            for prompt_dir in self.prompt_directories:
                dir_path = self.workspace_root / prompt_dir
                if dir_path.exists():
                    dir_tokens, _ = self._count_tokens_in_directory(dir_path)
                    total_tokens += dir_tokens
            return total_tokens
        except Exception:
            return 0


# Export for use in collector manager
__all__ = ['TokenOptimizationCollector']