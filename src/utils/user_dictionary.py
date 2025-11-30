"""
CORTEX User Dictionary - Personalized Shortcut Management

Tracks user-defined shortcuts and abbreviations for natural conversation.

Features:
- Add new shortcuts with context
- Lookup shortcuts to expand
- List all shortcuts by category
- Track usage statistics
- Auto-save to YAML

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class UserDictionary:
    """
    Manages user-defined shortcuts and abbreviations.
    
    Example:
        >>> ud = UserDictionary()
        >>> ud.add_shortcut("EPM", "Entry Point Module", "architecture")
        >>> ud.lookup("EPM")
        "Entry Point Module"
    """
    
    def __init__(self, dictionary_path: Optional[Path] = None):
        """
        Initialize user dictionary.
        
        Args:
            dictionary_path: Path to user-dictionary.yaml. If None, uses default.
        """
        if dictionary_path is None:
            # Default: cortex-brain/user-dictionary.yaml
            import os
            cortex_root = os.environ.get("CORTEX_ROOT", str(Path.cwd()))
            brain_path = Path(cortex_root) / "cortex-brain"
            dictionary_path = brain_path / "user-dictionary.yaml"
        
        self.dictionary_path = Path(dictionary_path)
        self.data = self._load()
    
    def _load(self) -> Dict:
        """Load dictionary from YAML file."""
        if not self.dictionary_path.exists():
            # Create default structure
            return {
                "version": "1.0",
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
                "shortcuts": {},
                "categories": {
                    "architecture": {"description": "System architecture and design patterns"},
                    "operations": {"description": "CORTEX operations and workflows"},
                    "technical": {"description": "Technical terms and abbreviations"},
                    "user_specific": {"description": "User's personal shortcuts and preferences"}
                },
                "stats": {
                    "total_shortcuts": 0,
                    "most_used": None,
                    "last_added": None
                }
            }
        
        with open(self.dictionary_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def _save(self):
        """Save dictionary to YAML file."""
        # Update metadata
        self.data["last_updated"] = datetime.now().isoformat()
        self.data["stats"]["total_shortcuts"] = len(self.data["shortcuts"])
        
        # Calculate most used
        if self.data["shortcuts"]:
            most_used = max(
                self.data["shortcuts"].items(),
                key=lambda x: x[1].get("usage_count", 0)
            )
            self.data["stats"]["most_used"] = most_used[0]
        
        # Write to file
        self.dictionary_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.dictionary_path, 'w', encoding='utf-8') as f:
            yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)
    
    def add_shortcut(
        self,
        shortcut: str,
        full_term: str,
        category: str = "user_specific",
        description: str = "",
        context: str = ""
    ) -> bool:
        """
        Add a new shortcut to the dictionary.
        
        Args:
            shortcut: The abbreviation (e.g., "EPM")
            full_term: The full term (e.g., "Entry Point Module")
            category: Category (architecture, operations, technical, user_specific)
            description: Optional description
            context: Optional usage context
            
        Returns:
            True if added successfully, False if already exists
        """
        if shortcut in self.data["shortcuts"]:
            return False
        
        self.data["shortcuts"][shortcut] = {
            "full_term": full_term,
            "category": category,
            "description": description,
            "context": context,
            "created": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        self.data["stats"]["last_added"] = shortcut
        self._save()
        return True
    
    def lookup(self, shortcut: str, track_usage: bool = True) -> Optional[str]:
        """
        Look up a shortcut and return the full term.
        
        Args:
            shortcut: The abbreviation to look up
            track_usage: Whether to increment usage count
            
        Returns:
            Full term if found, None otherwise
        """
        if shortcut not in self.data["shortcuts"]:
            return None
        
        if track_usage:
            self.data["shortcuts"][shortcut]["usage_count"] += 1
            self._save()
        
        return self.data["shortcuts"][shortcut]["full_term"]
    
    def get_details(self, shortcut: str) -> Optional[Dict]:
        """
        Get full details for a shortcut.
        
        Args:
            shortcut: The abbreviation
            
        Returns:
            Dictionary with all details, or None if not found
        """
        return self.data["shortcuts"].get(shortcut)
    
    def list_shortcuts(self, category: Optional[str] = None) -> List[Tuple[str, str]]:
        """
        List all shortcuts, optionally filtered by category.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of (shortcut, full_term) tuples
        """
        shortcuts = []
        
        for shortcut, details in self.data["shortcuts"].items():
            if category is None or details["category"] == category:
                shortcuts.append((shortcut, details["full_term"]))
        
        return sorted(shortcuts)
    
    def remove_shortcut(self, shortcut: str) -> bool:
        """
        Remove a shortcut from the dictionary.
        
        Args:
            shortcut: The abbreviation to remove
            
        Returns:
            True if removed, False if not found
        """
        if shortcut not in self.data["shortcuts"]:
            return False
        
        del self.data["shortcuts"][shortcut]
        self._save()
        return True
    
    def update_shortcut(
        self,
        shortcut: str,
        full_term: Optional[str] = None,
        category: Optional[str] = None,
        description: Optional[str] = None,
        context: Optional[str] = None
    ) -> bool:
        """
        Update an existing shortcut.
        
        Args:
            shortcut: The abbreviation to update
            full_term: New full term (optional)
            category: New category (optional)
            description: New description (optional)
            context: New context (optional)
            
        Returns:
            True if updated, False if not found
        """
        if shortcut not in self.data["shortcuts"]:
            return False
        
        if full_term is not None:
            self.data["shortcuts"][shortcut]["full_term"] = full_term
        if category is not None:
            self.data["shortcuts"][shortcut]["category"] = category
        if description is not None:
            self.data["shortcuts"][shortcut]["description"] = description
        if context is not None:
            self.data["shortcuts"][shortcut]["context"] = context
        
        self._save()
        return True
    
    def expand_text(self, text: str) -> str:
        """
        Expand all shortcuts in a text string.
        
        Args:
            text: Text containing shortcuts
            
        Returns:
            Text with shortcuts expanded
        """
        import re
        
        # Find all words in text
        words = re.findall(r'\b[A-Z]{2,}\b', text)  # Find potential acronyms
        
        for word in words:
            full_term = self.lookup(word, track_usage=False)
            if full_term:
                # Replace with full term (keep original case for first occurrence)
                text = re.sub(
                    rf'\b{word}\b',
                    f"{word} ({full_term})",
                    text,
                    count=1  # Only expand first occurrence
                )
        
        return text
    
    def get_stats(self) -> Dict:
        """Get usage statistics."""
        return self.data["stats"]
    
    def print_summary(self):
        """Print a formatted summary of the dictionary."""
        print("=" * 80)
        print("CORTEX USER DICTIONARY")
        print("=" * 80)
        print()
        
        stats = self.get_stats()
        print(f"Total shortcuts: {stats['total_shortcuts']}")
        print(f"Most used: {stats['most_used']}")
        print(f"Last added: {stats['last_added']}")
        print()
        
        # Group by category
        categories = {}
        for shortcut, details in self.data["shortcuts"].items():
            cat = details["category"]
            if cat not in categories:
                categories[cat] = []
            categories[cat].append((shortcut, details))
        
        # Print by category
        for category, shortcuts in sorted(categories.items()):
            cat_desc = self.data["categories"].get(category, {}).get("description", "")
            print(f"\n{category.upper()} ({cat_desc})")
            print("-" * 80)
            
            for shortcut, details in sorted(shortcuts, key=lambda x: x[0]):
                print(f"  {shortcut:<10} → {details['full_term']}")
                if details.get("description"):
                    print(f"             {details['description']}")
                print(f"             Used: {details['usage_count']} times")
        
        print()
        print("=" * 80)


def main():
    """CLI entry point for testing."""
    import sys
    
    ud = UserDictionary()
    
    if len(sys.argv) < 2:
        ud.print_summary()
        return
    
    command = sys.argv[1].lower()
    
    if command == "add":
        if len(sys.argv) < 4:
            print("Usage: python user_dictionary.py add <shortcut> <full_term> [category] [description]")
            return
        
        shortcut = sys.argv[2]
        full_term = sys.argv[3]
        category = sys.argv[4] if len(sys.argv) > 4 else "user_specific"
        description = sys.argv[5] if len(sys.argv) > 5 else ""
        
        if ud.add_shortcut(shortcut, full_term, category, description):
            print(f"✅ Added: {shortcut} → {full_term}")
        else:
            print(f"❌ Shortcut '{shortcut}' already exists")
    
    elif command == "lookup":
        if len(sys.argv) < 3:
            print("Usage: python user_dictionary.py lookup <shortcut>")
            return
        
        shortcut = sys.argv[2]
        full_term = ud.lookup(shortcut)
        
        if full_term:
            print(f"{shortcut} → {full_term}")
            details = ud.get_details(shortcut)
            if details.get("description"):
                print(f"Description: {details['description']}")
            if details.get("context"):
                print(f"Context: {details['context']}")
        else:
            print(f"❌ Shortcut '{shortcut}' not found")
    
    elif command == "list":
        category = sys.argv[2] if len(sys.argv) > 2 else None
        shortcuts = ud.list_shortcuts(category)
        
        print(f"\nShortcuts ({len(shortcuts)}):")
        for shortcut, full_term in shortcuts:
            print(f"  {shortcut:<10} → {full_term}")
    
    elif command == "expand":
        if len(sys.argv) < 3:
            print("Usage: python user_dictionary.py expand <text>")
            return
        
        text = " ".join(sys.argv[2:])
        expanded = ud.expand_text(text)
        print(f"Original:  {text}")
        print(f"Expanded:  {expanded}")
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: add, lookup, list, expand")


if __name__ == "__main__":
    main()
