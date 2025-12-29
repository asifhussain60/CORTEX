"""
CORTEX Toolkit Registry

Provides discovery and invocation of toolkit tools across repositories.
"""
from pathlib import Path
import yaml
import os
import sys
import subprocess
from typing import Dict, List, Optional, Any
import platform


class ToolkitRegistry:
    """Registry for discovering and invoking toolkit tools."""
    
    def __init__(self, toolkit_root: Optional[Path] = None):
        """
        Initialize toolkit registry.
        
        Args:
            toolkit_root: Path to toolkit root directory. Auto-discovers if None.
        """
        self.toolkit_root = toolkit_root or self._discover_toolkit_root()
        self.manifest_path = self.toolkit_root / "toolkit-manifest.yaml"
        self.manifest = self._load_manifest()
        self.version = self._load_version()
    
    def _discover_toolkit_root(self) -> Path:
        """
        Auto-discover toolkit root from environment or config.
        
        Returns:
            Path to toolkit root directory.
            
        Raises:
            RuntimeError: If toolkit root cannot be discovered.
        """
        # Check environment variable
        if env_root := os.getenv("CORTEX_TOOLKIT_ROOT"):
            return Path(env_root)
        
        # Check user config
        user_config = Path.home() / ".cortex" / "config.yaml"
        if user_config.exists():
            try:
                config = yaml.safe_load(user_config.read_text(encoding='utf-8'))
                if "cortex_toolkit_root" in config:
                    return Path(config["cortex_toolkit_root"])
            except Exception:
                pass
        
        # Check global workspace config
        for project_root in [Path.cwd(), Path.cwd().parent, Path.cwd().parent.parent]:
            global_config = project_root / "global-workspace-config.yaml"
            if global_config.exists():
                try:
                    config = yaml.safe_load(global_config.read_text(encoding='utf-8'))
                    if "cortex_toolkit_root" in config:
                        return Path(config["cortex_toolkit_root"])
                except Exception:
                    pass
        
        # Fallback: relative to this file
        fallback = Path(__file__).parent.parent
        if (fallback / "toolkit-manifest.yaml").exists():
            return fallback
        
        raise RuntimeError(
            "Cannot discover CORTEX toolkit root. "
            "Set CORTEX_TOOLKIT_ROOT environment variable or create ~/.cortex/config.yaml"
        )
    
    def _load_manifest(self) -> Dict:
        """
        Load toolkit manifest.
        
        Returns:
            Manifest dictionary.
            
        Raises:
            FileNotFoundError: If manifest not found.
        """
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Toolkit manifest not found: {self.manifest_path}")
        
        return yaml.safe_load(self.manifest_path.read_text(encoding='utf-8'))
    
    def _load_version(self) -> str:
        """Load toolkit version."""
        version_file = self.toolkit_root / "VERSION"
        if version_file.exists():
            return version_file.read_text(encoding='utf-8').strip()
        return "unknown"
    
    def list_categories(self) -> List[str]:
        """
        List all tool categories.
        
        Returns:
            List of category names.
        """
        return list(self.manifest["categories"].keys())
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict]:
        """
        List all tools or tools in a specific category.
        
        Args:
            category: Category name. If None, list all tools.
            
        Returns:
            List of tool metadata dictionaries.
        """
        if category:
            if category not in self.manifest["categories"]:
                raise ValueError(f"Unknown category: {category}")
            return self.manifest["categories"][category]["tools"]
        
        all_tools = []
        for cat_data in self.manifest["categories"].values():
            all_tools.extend(cat_data["tools"])
        return all_tools
    
    def get_tool(self, name: str) -> Optional[Dict]:
        """
        Get tool metadata by name.
        
        Args:
            name: Tool name.
            
        Returns:
            Tool metadata dictionary or None if not found.
        """
        for tool in self.list_tools():
            if tool["name"] == name:
                return tool
        return None
    
    def get_category_description(self, category: str) -> str:
        """Get category description."""
        if category in self.manifest["categories"]:
            return self.manifest["categories"][category]["description"]
        return ""
    
    def resolve_script_path(self, tool_name: str) -> Optional[Path]:
        """
        Resolve absolute path to tool script.
        
        Args:
            tool_name: Tool name.
            
        Returns:
            Absolute path to script or None if tool not found.
        """
        if tool := self.get_tool(tool_name):
            return self.toolkit_root / tool["script"]
        return None
    
    def resolve_wrapper_path(self, tool_name: str) -> Optional[Path]:
        """
        Resolve absolute path to tool wrapper (if exists).
        
        Args:
            tool_name: Tool name.
            
        Returns:
            Absolute path to wrapper or None if no wrapper.
        """
        if tool := self.get_tool(tool_name):
            if "wrapper" in tool:
                return self.toolkit_root / tool["wrapper"]
        return None
    
    def is_platform_supported(self, tool_name: str) -> bool:
        """
        Check if current platform is supported by tool.
        
        Args:
            tool_name: Tool name.
            
        Returns:
            True if platform supported, False otherwise.
        """
        tool = self.get_tool(tool_name)
        if not tool:
            return False
        
        current_platform = platform.system().lower()
        platform_map = {
            "windows": "windows",
            "linux": "linux",
            "darwin": "macos"
        }
        
        platform_name = platform_map.get(current_platform, "unknown")
        return platform_name in tool.get("platforms", [])
    
    def invoke_tool(self, name: str, args: List[str] = None, **kwargs) -> int:
        """
        Invoke a tool with arguments.
        
        Args:
            name: Tool name.
            args: Command-line arguments.
            **kwargs: Additional subprocess.run() arguments.
            
        Returns:
            Exit code from tool execution.
            
        Raises:
            ValueError: If tool not found or platform not supported.
            FileNotFoundError: If script not found.
        """
        args = args or []
        tool = self.get_tool(name)
        
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        
        if not self.is_platform_supported(name):
            raise ValueError(
                f"Tool '{name}' not supported on platform: {platform.system()}"
            )
        
        # Resolve script path
        execution_method = tool.get("execution_method", "cli")
        
        if execution_method == "cli_wrapper":
            wrapper_path = self.resolve_wrapper_path(name)
            if not wrapper_path or not wrapper_path.exists():
                raise FileNotFoundError(f"Wrapper not found: {wrapper_path}")
            script_path = wrapper_path
        elif execution_method == "cli":
            script_path = self.resolve_script_path(name)
            if not script_path or not script_path.exists():
                raise FileNotFoundError(f"Script not found: {script_path}")
        else:
            raise ValueError(
                f"Cannot invoke tool '{name}' with execution_method: {execution_method}. "
                f"Use Copilot Chat for {execution_method} tools."
            )
        
        # Execute
        return self._run_python_script(script_path, args, **kwargs)
    
    def _run_python_script(self, script_path: Path, args: List[str], **kwargs) -> int:
        """
        Execute Python script with arguments.
        
        Args:
            script_path: Path to Python script.
            args: Command-line arguments.
            **kwargs: Additional subprocess.run() arguments.
            
        Returns:
            Exit code.
        """
        cmd = [sys.executable, str(script_path)] + args
        result = subprocess.run(cmd, **kwargs)
        return result.returncode
    
    def print_summary(self):
        """Print toolkit summary."""
        print(f"CORTEX Toolkit v{self.version}")
        print(f"Root: {self.toolkit_root}")
        print(f"\nCategories: {len(self.list_categories())}")
        print(f"Total Tools: {len(self.list_tools())}")
        print("\nCategories:")
        for category in self.list_categories():
            tools = self.list_tools(category)
            desc = self.get_category_description(category)
            print(f"  {category}: {len(tools)} tools - {desc}")
    
    def print_tools(self, category: Optional[str] = None):
        """
        Print tool list.
        
        Args:
            category: Category name. If None, print all tools.
        """
        if category:
            print(f"\n{category.upper()} Tools:")
            print("=" * 60)
            tools = self.list_tools(category)
        else:
            print("\nAll Tools:")
            print("=" * 60)
            tools = self.list_tools()
        
        for tool in tools:
            name = tool["name"]
            command = tool["command"]
            desc = tool["description"]
            method = tool.get("execution_method", "cli")
            print(f"\n{name} ({command})")
            print(f"  Description: {desc}")
            print(f"  Execution: {method}")
            print(f"  Platforms: {', '.join(tool.get('platforms', []))}")
            if tool.get("requires_admin"):
                print("  ⚠️  Requires admin privileges")


def main():
    """CLI entry point for toolkit registry."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Toolkit Registry",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "action",
        choices=["list", "info", "categories", "invoke", "version"],
        help="Action to perform"
    )
    parser.add_argument(
        "target",
        nargs="?",
        help="Target (category/tool name)"
    )
    parser.add_argument(
        "--args",
        nargs=argparse.REMAINDER,
        help="Arguments for tool invocation"
    )
    
    args = parser.parse_args()
    
    try:
        registry = ToolkitRegistry()
        
        if args.action == "version":
            print(f"CORTEX Toolkit v{registry.version}")
        
        elif args.action == "categories":
            print("Available Categories:")
            for category in registry.list_categories():
                desc = registry.get_category_description(category)
                print(f"  {category}: {desc}")
        
        elif args.action == "list":
            if args.target:
                registry.print_tools(args.target)
            else:
                registry.print_summary()
        
        elif args.action == "info":
            if not args.target:
                print("Error: Tool name required")
                return 1
            
            tool = registry.get_tool(args.target)
            if not tool:
                print(f"Error: Tool not found: {args.target}")
                return 1
            
            print(f"\nTool: {tool['name']}")
            print(f"Command: {tool['command']}")
            print(f"Description: {tool['description']}")
            print(f"Script: {tool['script']}")
            if "wrapper" in tool:
                print(f"Wrapper: {tool['wrapper']}")
            print(f"Platforms: {', '.join(tool['platforms'])}")
            print(f"Execution: {tool.get('execution_method', 'cli')}")
            print(f"Requires Admin: {tool.get('requires_admin', False)}")
        
        elif args.action == "invoke":
            if not args.target:
                print("Error: Tool name required")
                return 1
            
            invoke_args = args.args or []
            return registry.invoke_tool(args.target, invoke_args)
        
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
