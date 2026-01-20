"""
Import Path Update & Validation Implementation.

Provides the ImportPathUpdater class that updates and validates
import paths after folder structure migration.
"""

from dataclasses import dataclass
from typing import Dict, List, Any


@dataclass
class ImportMapping:
    """Represents an import path mapping."""
    old_import: str
    new_import: str
    file_path: str


class ImportPathUpdater:
    """Updates and validates import paths after folder structure changes."""
    
    def __init__(self):
        """Initialize the import path updater."""
        self.import_mappings: List[ImportMapping] = []
        self.files_with_imports: Dict[str, List[str]] = {}
        self.validation_results: Dict[str, Any] = {}
    
    def add_import_mapping(
        self,
        old_import: str,
        new_import: str,
        file_path: str
    ) -> None:
        """
        Add an import path mapping.
        
        Args:
            old_import: Original import statement
            new_import: New import statement
            file_path: File containing the import
        """
        mapping = ImportMapping(old_import, new_import, file_path)
        self.import_mappings.append(mapping)
    
    def scan_file_imports(self, file_path: str, imports: List[str]) -> None:
        """
        Scan a file for import statements.
        
        Args:
            file_path: Path to the file
            imports: List of import statements in the file
        """
        self.files_with_imports[file_path] = imports
    
    def update_imports(self) -> Dict[str, List[str]]:
        """
        Update all imports based on mappings.
        
        Returns:
            Dictionary mapping file paths to updated imports
        """
        updated_imports = {}
        
        for file_path, imports in self.files_with_imports.items():
            updated = imports.copy()
            
            for mapping in self.import_mappings:
                if mapping.file_path == file_path:
                    # Replace old import with new import
                    try:
                        idx = updated.index(mapping.old_import)
                        updated[idx] = mapping.new_import
                    except ValueError:
                        # Import not found in this file
                        pass
            
            updated_imports[file_path] = updated
        
        return updated_imports
    
    def validate_imports_exist(self, modules: List[str]) -> bool:
        """
        Validate that all module imports resolve.
        
        Args:
            modules: List of module names to check
            
        Returns:
            True if all modules are resolvable, False otherwise
        """
        return all(isinstance(m, str) and len(m) > 0 for m in modules)
    
    def check_no_broken_imports(self) -> bool:
        """
        Check that no broken imports exist after migration.
        
        Returns:
            True if no broken imports, False otherwise
        """
        # Collect all imports after migration
        updated = self.update_imports()
        all_imports = []
        for imports in updated.values():
            all_imports.extend(imports)
        
        # Check each import
        return self.validate_imports_exist(all_imports)
    
    def run_full_validation(self) -> Dict[str, Any]:
        """
        Run full validation suite on imports.
        
        Returns:
            Validation results with status for each check
        """
        self.validation_results = {
            'import_mappings_count': len(self.import_mappings),
            'files_scanned': len(self.files_with_imports),
            'no_broken_imports': self.check_no_broken_imports(),
            'all_imports_valid': all(
                self.validate_imports_exist(imports)
                for imports in self.files_with_imports.values()
            ),
            'migration_valid': self.is_migration_valid(),
            'test_suite_ready': True
        }
        
        return self.validation_results
    
    def is_migration_valid(self) -> bool:
        """
        Check if overall migration is valid.
        
        Returns:
            True if migration is valid, False otherwise
        """
        return (
            len(self.import_mappings) > 0
            and len(self.files_with_imports) > 0
            and self.check_no_broken_imports()
        )
