"""
Shell syntax adapters for cross-platform command generation.

Provides syntax adaptation for PowerShell, bash, zsh, and cmd.
"""

from typing import Dict


class ShellAdapter:
    """Utility for adapting command syntax across shells."""
    
    # Command translations
    COMMAND_MAP = {
        "bash": {
            "dir": "ls",
            "type": "cat",
            "del": "rm",
            "copy": "cp",
            "move": "mv",
        },
        "zsh": {
            "dir": "ls",
            "type": "cat",
            "del": "rm",
            "copy": "cp",
            "move": "mv",
        },
    }
    
    @staticmethod
    def adapt_command(command: str, target_shell: str) -> str:
        """
        Adapt command syntax for target shell.
        
        Args:
            command: Original command
            target_shell: Target shell type
            
        Returns:
            Adapted command
        """
        if target_shell not in ["bash", "zsh"]:
            return command
        
        # Get translation map
        translation_map = ShellAdapter.COMMAND_MAP.get(target_shell, {})
        
        # Check if command starts with a translatable keyword
        for windows_cmd, unix_cmd in translation_map.items():
            if command.startswith(windows_cmd):
                return command.replace(windows_cmd, unix_cmd, 1)
        
        return command
    
    @staticmethod
    def format_env_var(var_name: str, shell: str) -> str:
        """
        Format environment variable reference for shell.
        
        Args:
            var_name: Variable name
            shell: Shell type
            
        Returns:
            Formatted variable reference
        """
        if shell == "PowerShell":
            return f"$env:{var_name}"
        else:  # bash, zsh, cmd
            return f"${var_name}"
    
    @staticmethod
    def get_line_continuation(shell: str) -> str:
        """
        Get line continuation character for shell.
        
        Args:
            shell: Shell type
            
        Returns:
            Line continuation character
        """
        if shell == "PowerShell":
            return "`"
        else:  # bash, zsh, cmd
            return "\\"
    
    @staticmethod
    def get_path_separator(shell: str) -> str:
        """Get path separator for shell."""
        if shell in ["PowerShell", "cmd"]:
            return ";"
        return ":"
