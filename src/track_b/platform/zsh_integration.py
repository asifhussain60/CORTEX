"""
CORTEX 3.0 Track B: Zsh Shell Integration
=========================================

Advanced Zsh shell integration for CORTEX Track B on macOS.
Provides deep shell integration, command enhancement, and intelligent command execution.

Key Features:
- Zsh configuration optimization
- Custom CORTEX functions and aliases
- Command history integration with CORTEX brain
- Intelligent command suggestions
- Shell performance optimization

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import os
import sys
import logging
import subprocess
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import tempfile
import json


class ZshFeature(Enum):
    """Available Zsh integration features."""
    COMPLETION = "completion"
    HISTORY = "history" 
    ALIASES = "aliases"
    FUNCTIONS = "functions"
    PROMPT = "prompt"
    PERFORMANCE = "performance"


class IntegrationLevel(Enum):
    """Zsh integration levels."""
    MINIMAL = "minimal"        # Basic integration only
    STANDARD = "standard"      # Standard feature set
    ENHANCED = "enhanced"      # Full feature integration


@dataclass
class ZshConfig:
    """Zsh configuration settings."""
    zsh_path: str
    config_file: str
    backup_file: str
    cortex_config_file: str
    integration_level: IntegrationLevel
    enabled_features: List[ZshFeature]
    custom_prompt: bool = True
    history_integration: bool = True
    completion_enhancement: bool = True


@dataclass
class ZshInstallationResult:
    """Result of Zsh integration installation."""
    success: bool
    features_installed: List[str]
    config_file_modified: bool
    backup_created: bool
    warnings: List[str] = field(default_factory=list)
    error_message: Optional[str] = None


class ZshIntegration:
    """
    Zsh Shell Integration for CORTEX Track B
    
    Provides comprehensive Zsh shell integration including:
    - Custom CORTEX commands and aliases
    - Intelligent command completion
    - Shell history integration with CORTEX brain
    - Performance optimizations for macOS
    """
    
    def __init__(self, integration_level: IntegrationLevel = IntegrationLevel.STANDARD):
        self.logger = logging.getLogger("cortex.track_b.zsh_integration")
        self.integration_level = integration_level
        
        # Detect Zsh installation
        self.zsh_config = self._detect_zsh_config()
        
        # Integration state
        self.is_installed = False
        self.installation_result: Optional[ZshInstallationResult] = None
        
        # Check if already integrated
        self._check_existing_integration()
    
    def _detect_zsh_config(self) -> Optional[ZshConfig]:
        """Detect Zsh installation and configuration."""
        try:
            # Find Zsh executable
            zsh_path = shutil.which('zsh')
            if not zsh_path:
                self.logger.error("Zsh not found in PATH")
                return None
            
            # Check if Zsh is the default shell
            current_shell = os.environ.get('SHELL', '')
            if 'zsh' not in current_shell:
                self.logger.warning(f"Current shell is {current_shell}, not Zsh")
            
            # Locate configuration files
            home_dir = Path.home()
            zshrc_file = home_dir / '.zshrc'
            
            # Determine CORTEX config file location
            cortex_config_dir = home_dir / '.cortex'
            cortex_config_dir.mkdir(exist_ok=True)
            cortex_zsh_file = cortex_config_dir / 'zsh_integration.zsh'
            
            # Determine enabled features based on integration level
            if self.integration_level == IntegrationLevel.MINIMAL:
                enabled_features = [ZshFeature.ALIASES, ZshFeature.FUNCTIONS]
            elif self.integration_level == IntegrationLevel.STANDARD:
                enabled_features = [ZshFeature.ALIASES, ZshFeature.FUNCTIONS, 
                                  ZshFeature.COMPLETION, ZshFeature.HISTORY]
            else:  # ENHANCED
                enabled_features = list(ZshFeature)
            
            return ZshConfig(
                zsh_path=zsh_path,
                config_file=str(zshrc_file),
                backup_file=str(zshrc_file) + '.cortex_backup',
                cortex_config_file=str(cortex_zsh_file),
                integration_level=self.integration_level,
                enabled_features=enabled_features
            )
            
        except Exception as e:
            self.logger.error(f"Error detecting Zsh configuration: {e}")
            return None
    
    def _check_existing_integration(self):
        """Check if CORTEX Zsh integration is already installed."""
        if not self.zsh_config:
            return
        
        try:
            zshrc_path = Path(self.zsh_config.config_file)
            if zshrc_path.exists():
                content = zshrc_path.read_text()
                if '# CORTEX Zsh Integration' in content:
                    self.is_installed = True
                    self.logger.info("Existing CORTEX Zsh integration found")
                    
        except Exception as e:
            self.logger.debug(f"Error checking existing integration: {e}")
    
    def install_integration(self, force: bool = False) -> ZshInstallationResult:
        """Install CORTEX Zsh integration."""
        if not self.zsh_config:
            return ZshInstallationResult(
                success=False,
                features_installed=[],
                config_file_modified=False,
                backup_created=False,
                error_message="Zsh configuration not available"
            )
        
        if self.is_installed and not force:
            return ZshInstallationResult(
                success=True,
                features_installed=[],
                config_file_modified=False,
                backup_created=False,
                warnings=["Integration already installed - use force=True to reinstall"]
            )
        
        try:
            self.logger.info(f"Installing CORTEX Zsh integration (level: {self.integration_level.value})")
            
            warnings = []
            features_installed = []
            
            # Create backup of existing .zshrc
            backup_created = self._create_zshrc_backup()
            
            # Generate CORTEX integration file
            self._generate_cortex_integration_file()
            
            # Add source line to .zshrc
            config_modified = self._add_source_to_zshrc()
            
            # Install individual features
            for feature in self.zsh_config.enabled_features:
                if self._install_feature(feature):
                    features_installed.append(feature.value)
                else:
                    warnings.append(f"Failed to install {feature.value} feature")
            
            # Validate installation
            validation_result = self._validate_installation()
            if not validation_result['success']:
                warnings.extend(validation_result['warnings'])
            
            result = ZshInstallationResult(
                success=len(features_installed) > 0,
                features_installed=features_installed,
                config_file_modified=config_modified,
                backup_created=backup_created,
                warnings=warnings
            )
            
            self.installation_result = result
            if result.success:
                self.is_installed = True
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error installing Zsh integration: {e}")
            return ZshInstallationResult(
                success=False,
                features_installed=[],
                config_file_modified=False,
                backup_created=False,
                error_message=str(e)
            )
    
    def _create_zshrc_backup(self) -> bool:
        """Create backup of existing .zshrc file."""
        try:
            zshrc_path = Path(self.zsh_config.config_file)
            backup_path = Path(self.zsh_config.backup_file)
            
            if zshrc_path.exists():
                shutil.copy2(zshrc_path, backup_path)
                self.logger.info(f"Created .zshrc backup: {backup_path}")
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error creating .zshrc backup: {e}")
            return False
    
    def _generate_cortex_integration_file(self):
        """Generate the CORTEX Zsh integration file."""
        try:
            integration_content = self._build_integration_content()
            
            cortex_file = Path(self.zsh_config.cortex_config_file)
            cortex_file.write_text(integration_content)
            
            self.logger.info(f"Generated CORTEX integration file: {cortex_file}")
            
        except Exception as e:
            self.logger.error(f"Error generating integration file: {e}")
            raise
    
    def _build_integration_content(self) -> str:
        """Build the content for the CORTEX integration file."""
        content_parts = []
        
        # Header
        content_parts.append("""#!/usr/bin/env zsh
# CORTEX Zsh Integration
# Generated automatically - do not edit manually
# Author: Asif Hussain
# Copyright: © 2024-2025 Asif Hussain. All rights reserved.

""")
        
        # Environment variables
        content_parts.append(self._generate_environment_section())
        
        # Aliases
        if ZshFeature.ALIASES in self.zsh_config.enabled_features:
            content_parts.append(self._generate_aliases_section())
        
        # Functions
        if ZshFeature.FUNCTIONS in self.zsh_config.enabled_features:
            content_parts.append(self._generate_functions_section())
        
        # Completion
        if ZshFeature.COMPLETION in self.zsh_config.enabled_features:
            content_parts.append(self._generate_completion_section())
        
        # History integration
        if ZshFeature.HISTORY in self.zsh_config.enabled_features:
            content_parts.append(self._generate_history_section())
        
        # Prompt customization
        if ZshFeature.PROMPT in self.zsh_config.enabled_features:
            content_parts.append(self._generate_prompt_section())
        
        # Performance optimizations
        if ZshFeature.PERFORMANCE in self.zsh_config.enabled_features:
            content_parts.append(self._generate_performance_section())
        
        return '\n'.join(content_parts)
    
    def _generate_environment_section(self) -> str:
        """Generate environment variables section."""
        return """# CORTEX Environment Variables
export CORTEX_SHELL_INTEGRATION="zsh"
export CORTEX_INTEGRATION_LEVEL="{level}"
export CORTEX_ZSH_VERSION="3.0.0"

""".format(level=self.integration_level.value)
    
    def _generate_aliases_section(self) -> str:
        """Generate CORTEX aliases section."""
        return """# CORTEX Aliases
alias cortex='python -m src.cortex'
alias crtx='cortex'
alias cx='cortex'

# Quick commands
alias cstatus='cortex status'
alias chelp='cortex help'
alias cconfig='cortex config'
alias clog='cortex log'

# Development shortcuts
alias cdev='cortex dev'
alias ctest='cortex test'
alias cbuild='cortex build'
alias cdeploy='cortex deploy'

# Git integration
alias cgit='cortex git'
alias ccommit='cortex git commit'
alias cpush='cortex git push'
alias cpull='cortex git pull'

# Memory and learning
alias cmemory='cortex memory'
alias clearn='cortex learn'
alias cpattern='cortex pattern'

"""
    
    def _generate_functions_section(self) -> str:
        """Generate CORTEX functions section."""
        return """# CORTEX Functions

# Quick CORTEX command with error handling
function cx() {
    if [[ $# -eq 0 ]]; then
        echo "CORTEX 3.0 - Cognitive Framework"
        echo "Usage: cx <command> [options]"
        echo "Try: cx help"
        return 0
    fi
    
    python -m src.cortex "$@"
    local exit_code=$?
    
    if [[ $exit_code -ne 0 ]]; then
        echo "❌ CORTEX command failed with exit code: $exit_code"
    fi
    
    return $exit_code
}

# CORTEX context-aware directory change
function ccd() {
    local target_dir="$1"
    
    if [[ -z "$target_dir" ]]; then
        echo "Usage: ccd <directory>"
        return 1
    fi
    
    # Let CORTEX suggest or validate the directory
    local suggested_dir=$(python -m src.cortex suggest-dir "$target_dir" 2>/dev/null)
    
    if [[ -n "$suggested_dir" && -d "$suggested_dir" ]]; then
        cd "$suggested_dir"
        echo "📁 Changed to: $(pwd)"
        
        # Notify CORTEX of directory change
        python -m src.cortex track directory-change "$(pwd)" &
    else
        # Fallback to normal cd
        cd "$target_dir"
    fi
}

# CORTEX-enhanced file search
function cfind() {
    local search_term="$1"
    
    if [[ -z "$search_term" ]]; then
        echo "Usage: cfind <search_term>"
        return 1
    fi
    
    echo "🔍 CORTEX-enhanced search for: $search_term"
    
    # Use CORTEX intelligent search if available
    python -m src.cortex search "$search_term" 2>/dev/null || {
        # Fallback to standard find
        find . -name "*$search_term*" -type f | head -20
    }
}

# CORTEX project initialization
function cinit() {
    local project_type="$1"
    local project_name="$2"
    
    echo "🚀 Initializing CORTEX project..."
    
    if [[ -n "$project_type" && -n "$project_name" ]]; then
        python -m src.cortex init "$project_type" "$project_name"
    else
        python -m src.cortex init
    fi
}

# CORTEX quick status with visual indicators
function cquick() {
    echo "⚡ CORTEX Quick Status"
    echo "===================="
    
    # System status
    local cpu_usage=$(python -c "import os; print(os.getloadavg()[0])" 2>/dev/null || echo "unknown")
    echo "🖥️  CPU Load: $cpu_usage"
    
    # Git status if in git repo
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        local git_status=$(git status --porcelain | wc -l | tr -d ' ')
        echo "📂 Git Changes: $git_status files"
    fi
    
    # CORTEX status
    python -m src.cortex status --quick 2>/dev/null || echo "🤖 CORTEX: Not available"
}

"""
    
    def _generate_completion_section(self) -> str:
        """Generate command completion section."""
        return """# CORTEX Command Completion

# Enable completion for CORTEX commands
if command -v python >/dev/null 2>&1; then
    # Basic completion for common CORTEX commands
    _cortex_completion() {
        local current_word="${COMP_WORDS[COMP_CWORD]}"
        local commands="help status config log memory learn pattern git dev test build deploy"
        
        COMPREPLY=($(compgen -W "$commands" -- "$current_word"))
    }
    
    # Register completion for CORTEX aliases
    complete -F _cortex_completion cortex
    complete -F _cortex_completion crtx
    complete -F _cortex_completion cx
fi

# Enhanced tab completion
setopt AUTO_MENU
setopt COMPLETE_IN_WORD
setopt ALWAYS_TO_END

"""
    
    def _generate_history_section(self) -> str:
        """Generate history integration section."""
        return """# CORTEX History Integration

# Enhanced history settings
HISTSIZE=10000
SAVEHIST=10000
HISTFILE=~/.zsh_history

# History options
setopt EXTENDED_HISTORY
setopt SHARE_HISTORY
setopt HIST_EXPIRE_DUPS_FIRST
setopt HIST_IGNORE_DUPS
setopt HIST_IGNORE_ALL_DUPS
setopt HIST_FIND_NO_DUPS
setopt HIST_IGNORE_SPACE
setopt HIST_SAVE_NO_DUPS
setopt HIST_REDUCE_BLANKS

# CORTEX command history tracking
function cortex_track_command() {
    if [[ -n "$1" ]]; then
        # Send command to CORTEX for learning (background process)
        python -m src.cortex track command "$1" &
    fi
}

# Hook into command execution
preexec() {
    # Track CORTEX-related commands
    if [[ "$1" == cortex* ]] || [[ "$1" == cx* ]] || [[ "$1" == c[a-z]* ]]; then
        cortex_track_command "$1"
    fi
}

"""
    
    def _generate_prompt_section(self) -> str:
        """Generate custom prompt section."""
        return """# CORTEX Custom Prompt

# CORTEX status indicator function
function cortex_prompt_indicator() {
    # Check if CORTEX is available
    if python -m src.cortex status --quiet >/dev/null 2>&1; then
        echo "%F{green}🧠%f"  # Green brain emoji when CORTEX is active
    else
        echo "%F{red}💤%f"   # Red sleep emoji when CORTEX is inactive
    fi
}

# Git status for prompt
function git_prompt_info() {
    if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
        local branch=$(git branch --show-current 2>/dev/null)
        local changes=$(git status --porcelain | wc -l | tr -d ' ')
        
        if [[ $changes -gt 0 ]]; then
            echo "%F{yellow}($branch*%f"
        else
            echo "%F{cyan}($branch)%f"
        fi
    fi
}

# Custom CORTEX prompt
if [[ "$CORTEX_PROMPT_ENABLED" != "false" ]]; then
    # Enable prompt substitution
    setopt PROMPT_SUBST
    
    # Set the prompt
    PROMPT='$(cortex_prompt_indicator) %F{blue}%~%f $(git_prompt_info) %F{magenta}❯%f '
    
    # Right prompt with time and CORTEX status
    RPROMPT='%F{gray}%T%f'
fi

"""
    
    def _generate_performance_section(self) -> str:
        """Generate performance optimization section."""
        return """# CORTEX Performance Optimizations

# Zsh performance improvements
setopt NO_BEEP
setopt NO_CASE_GLOB
setopt NUMERIC_GLOB_SORT

# Directory stack
setopt AUTO_PUSHD
setopt PUSHD_IGNORE_DUPS
setopt PUSHD_SILENT

# Correction
setopt CORRECT
setopt CORRECT_ALL

# Job control
setopt AUTO_RESUME
setopt NOTIFY

# Globbing
setopt EXTENDED_GLOB

# Key bindings for better performance
bindkey '^[[A' history-substring-search-up
bindkey '^[[B' history-substring-search-down

# CORTEX-specific optimizations
export CORTEX_SHELL_FAST_MODE=1
export CORTEX_BACKGROUND_LEARNING=1

"""
    
    def _add_source_to_zshrc(self) -> bool:
        """Add source line to .zshrc to load CORTEX integration."""
        try:
            zshrc_path = Path(self.zsh_config.config_file)
            cortex_source_line = f"source {self.zsh_config.cortex_config_file}"
            
            # Check if source line already exists
            if zshrc_path.exists():
                content = zshrc_path.read_text()
                if cortex_source_line in content:
                    self.logger.info("CORTEX source line already exists in .zshrc")
                    return False
            
            # Add source line to .zshrc
            with open(zshrc_path, 'a') as f:
                f.write(f"\n# CORTEX Zsh Integration\n")
                f.write(f"{cortex_source_line}\n")
            
            self.logger.info("Added CORTEX source line to .zshrc")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding source to .zshrc: {e}")
            return False
    
    def _install_feature(self, feature: ZshFeature) -> bool:
        """Install a specific Zsh feature."""
        try:
            self.logger.debug(f"Installing feature: {feature.value}")
            
            # Features are installed as part of the integration file generation
            # This method can be extended for feature-specific setup
            
            if feature == ZshFeature.COMPLETION:
                # Could add custom completion scripts here
                pass
            elif feature == ZshFeature.HISTORY:
                # Could set up history database integration
                pass
            elif feature == ZshFeature.PERFORMANCE:
                # Could apply performance-specific configurations
                pass
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error installing feature {feature.value}: {e}")
            return False
    
    def _validate_installation(self) -> Dict[str, Any]:
        """Validate the Zsh integration installation."""
        try:
            warnings = []
            
            # Check if files exist
            cortex_file = Path(self.zsh_config.cortex_config_file)
            if not cortex_file.exists():
                warnings.append("CORTEX integration file not found")
            
            # Check if .zshrc sources the integration
            zshrc_path = Path(self.zsh_config.config_file)
            if zshrc_path.exists():
                content = zshrc_path.read_text()
                if self.zsh_config.cortex_config_file not in content:
                    warnings.append(".zshrc does not source CORTEX integration")
            
            # Test basic functionality
            try:
                result = subprocess.run([self.zsh_config.zsh_path, '-c', 'source ~/.zshrc; echo "test"'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode != 0:
                    warnings.append("Zsh configuration test failed")
            except subprocess.TimeoutExpired:
                warnings.append("Zsh configuration test timed out")
            except Exception as e:
                warnings.append(f"Zsh configuration test error: {str(e)}")
            
            return {
                'success': len(warnings) == 0,
                'warnings': warnings
            }
            
        except Exception as e:
            return {
                'success': False,
                'warnings': [f"Validation error: {str(e)}"]
            }
    
    def uninstall_integration(self) -> bool:
        """Uninstall CORTEX Zsh integration."""
        try:
            self.logger.info("Uninstalling CORTEX Zsh integration")
            
            # Remove CORTEX integration file
            cortex_file = Path(self.zsh_config.cortex_config_file)
            if cortex_file.exists():
                cortex_file.unlink()
                self.logger.info("Removed CORTEX integration file")
            
            # Remove source line from .zshrc
            zshrc_path = Path(self.zsh_config.config_file)
            if zshrc_path.exists():
                content = zshrc_path.read_text()
                
                # Remove CORTEX section
                lines = content.split('\n')
                filtered_lines = []
                skip_section = False
                
                for line in lines:
                    if '# CORTEX Zsh Integration' in line:
                        skip_section = True
                        continue
                    elif skip_section and line.strip() == '':
                        skip_section = False
                        continue
                    elif not skip_section:
                        if 'cortex' not in line.lower() or not line.startswith('source'):
                            filtered_lines.append(line)
                
                zshrc_path.write_text('\n'.join(filtered_lines))
                self.logger.info("Removed CORTEX lines from .zshrc")
            
            # Restore backup if exists
            backup_path = Path(self.zsh_config.backup_file)
            if backup_path.exists():
                restore_backup = input("Restore .zshrc from backup? (y/N): ").lower().startswith('y')
                if restore_backup:
                    shutil.copy2(backup_path, zshrc_path)
                    self.logger.info("Restored .zshrc from backup")
            
            self.is_installed = False
            return True
            
        except Exception as e:
            self.logger.error(f"Error uninstalling integration: {e}")
            return False
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get current integration status."""
        if not self.zsh_config:
            return {
                'installed': False,
                'error': 'Zsh configuration not available'
            }
        
        # Check feature status
        feature_status = {}
        if self.is_installed:
            for feature in self.zsh_config.enabled_features:
                feature_status[feature.value] = self._check_feature_status(feature)
        
        return {
            'installed': self.is_installed,
            'zsh_path': self.zsh_config.zsh_path,
            'integration_level': self.zsh_config.integration_level.value,
            'config_file': self.zsh_config.config_file,
            'cortex_file': self.zsh_config.cortex_config_file,
            'enabled_features': [f.value for f in self.zsh_config.enabled_features],
            'feature_status': feature_status,
            'installation_result': self.installation_result.__dict__ if self.installation_result else None
        }
    
    def _check_feature_status(self, feature: ZshFeature) -> Dict[str, Any]:
        """Check the status of a specific feature."""
        try:
            cortex_file = Path(self.zsh_config.cortex_config_file)
            
            if not cortex_file.exists():
                return {'active': False, 'reason': 'Integration file not found'}
            
            content = cortex_file.read_text()
            
            # Check if feature content is present
            feature_markers = {
                ZshFeature.ALIASES: '# CORTEX Aliases',
                ZshFeature.FUNCTIONS: '# CORTEX Functions',
                ZshFeature.COMPLETION: '# CORTEX Command Completion',
                ZshFeature.HISTORY: '# CORTEX History Integration',
                ZshFeature.PROMPT: '# CORTEX Custom Prompt',
                ZshFeature.PERFORMANCE: '# CORTEX Performance Optimizations'
            }
            
            marker = feature_markers.get(feature)
            if marker and marker in content:
                return {'active': True, 'reason': 'Feature content found'}
            else:
                return {'active': False, 'reason': 'Feature content not found'}
                
        except Exception as e:
            return {'active': False, 'reason': f'Check failed: {str(e)}'}
    
    def test_integration(self) -> Dict[str, Any]:
        """Test the Zsh integration functionality."""
        if not self.is_installed:
            return {
                'success': False,
                'error': 'Integration not installed'
            }
        
        test_results = {}
        
        # Test basic shell functionality
        test_results['shell_test'] = self._test_shell_basic()
        
        # Test CORTEX aliases
        test_results['aliases_test'] = self._test_aliases()
        
        # Test CORTEX functions
        test_results['functions_test'] = self._test_functions()
        
        # Test completion (if enabled)
        if ZshFeature.COMPLETION in self.zsh_config.enabled_features:
            test_results['completion_test'] = self._test_completion()
        
        overall_success = all(result.get('success', False) for result in test_results.values())
        
        return {
            'success': overall_success,
            'test_results': test_results,
            'timestamp': datetime.now().isoformat()
        }
    
    def _test_shell_basic(self) -> Dict[str, Any]:
        """Test basic shell functionality."""
        try:
            result = subprocess.run([
                self.zsh_config.zsh_path, '-c', 
                f'source {self.zsh_config.cortex_config_file}; echo "CORTEX_ZSH_VERSION: $CORTEX_ZSH_VERSION"'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and 'CORTEX_ZSH_VERSION' in result.stdout:
                return {'success': True, 'output': result.stdout.strip()}
            else:
                return {'success': False, 'error': result.stderr or 'No output'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_aliases(self) -> Dict[str, Any]:
        """Test CORTEX aliases."""
        try:
            result = subprocess.run([
                self.zsh_config.zsh_path, '-c',
                f'source {self.zsh_config.cortex_config_file}; alias cx'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and 'cx=' in result.stdout:
                return {'success': True, 'output': 'cx alias found'}
            else:
                return {'success': False, 'error': 'cx alias not found'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_functions(self) -> Dict[str, Any]:
        """Test CORTEX functions."""
        try:
            result = subprocess.run([
                self.zsh_config.zsh_path, '-c',
                f'source {self.zsh_config.cortex_config_file}; typeset -f cx'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0 and 'function' in result.stdout:
                return {'success': True, 'output': 'cx function found'}
            else:
                return {'success': False, 'error': 'cx function not found'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _test_completion(self) -> Dict[str, Any]:
        """Test command completion."""
        try:
            # Test if completion system is loaded
            result = subprocess.run([
                self.zsh_config.zsh_path, '-c',
                f'source {self.zsh_config.cortex_config_file}; autoload -U compinit; compinit; echo "completion loaded"'
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                return {'success': True, 'output': 'Completion system loaded'}
            else:
                return {'success': False, 'error': 'Completion system failed to load'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}