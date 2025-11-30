"""
ADO Planning Template Parser
CORTEX 2.1 - Simplified ADO System

Parses simplified ADO template and stores in SQLite with auto-generated DoD.
"""

import re
import uuid
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ADOTemplateParser:
    """Parse and import ADO planning templates."""
    
    # DoD templates by work item type
    DOD_TEMPLATES = {
        "Bug": [
            "Root cause identified and documented",
            "Fix implemented and code reviewed",
            "Unit tests added/updated for bug scenario",
            "Regression tests passing",
            "No new bugs introduced (full test suite passing)",
            "Fix verified in staging environment",
            "Documentation updated (if bug affected documented behavior)",
            "Related bug reports checked and resolved"
        ],
        "Feature": [
            "All acceptance criteria met",
            "Code implemented and reviewed",
            "Unit tests written (≥80% coverage for new code)",
            "Integration tests passing",
            "Documentation updated (API docs, user guides)",
            "Performance tested (meets requirements)",
            "Security review completed (no high/critical vulnerabilities)",
            "Deployed to staging environment",
            "Stakeholder approval obtained"
        ],
        "Task": [
            "Task completed as specified",
            "Code changes reviewed (if applicable)",
            "Tests passing (if code changes made)",
            "Documentation updated (if required)",
            "Changes verified in target environment",
            "Related tasks checked for dependencies"
        ]
    }
    
    def __init__(self, db_path: str = "cortex-brain/tier1/ado_planning.db"):
        """Initialize parser with database path."""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize database with schema."""
        schema_path = Path("cortex-brain/schemas/ado_planning.sql")
        if schema_path.exists():
            with sqlite3.connect(self.db_path) as conn:
                schema_sql = schema_path.read_text()
                conn.executescript(schema_sql)
    
    def parse_template(self, file_path: Path) -> Dict:
        """
        Parse ADO template file and extract fields.
        
        Returns:
            Dict with parsed fields: ado_number, type, acceptance_criteria, technical_notes
        """
        content = file_path.read_text(encoding='utf-8')
        
        # Extract ADO number
        ado_match = re.search(r'ADO-(\d+)', content, re.IGNORECASE)
        if not ado_match:
            raise ValueError("ADO number not found. Format: ADO-12345")
        ado_number = f"ADO-{ado_match.group(1)}"
        
        # Extract type (Bug, Feature, or Task)
        type_match = re.search(r'\*\*Type:\*\*.*?(?:^|\n)(?:-\s*)?(Bug|Feature|Task)', 
                               content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
        if not type_match:
            raise ValueError("Type not selected. Choose Bug, Feature, or Task")
        work_type = type_match.group(1).capitalize()
        
        # Extract acceptance criteria
        ac_section = re.search(
            r'## 🎯 Acceptance Criteria.*?(?=##|$)', 
            content, 
            re.DOTALL
        )
        if not ac_section:
            raise ValueError("Acceptance Criteria section not found")
        
        # Parse numbered acceptance criteria
        ac_text = ac_section.group(0)
        ac_items = re.findall(r'^\d+\.\s+\[?(.+?)\]?$', ac_text, re.MULTILINE)
        
        if not ac_items or all(item.startswith('[') for item in ac_items):
            raise ValueError("No acceptance criteria filled out. Add at least one criterion.")
        
        # Clean up criteria (remove placeholder text)
        criteria = [
            item for item in ac_items 
            if not item.startswith('[') and len(item.strip()) > 10
        ]
        
        if not criteria:
            raise ValueError("Acceptance criteria too vague. Be more specific.")
        
        # Extract technical notes (optional)
        notes_section = re.search(
            r'## 📝 Technical Notes.*?(?=##|\*\*Generated DoD:\*\*|$)', 
            content, 
            re.DOTALL
        )
        technical_notes = ""
        if notes_section:
            notes_text = notes_section.group(0)
            # Remove section header and placeholder text
            notes_text = re.sub(r'## 📝 Technical Notes', '', notes_text)
            notes_text = re.sub(r'\*\*Context for implementation:\*\*', '', notes_text)
            notes_text = re.sub(r'\[.*?\]', '', notes_text)  # Remove placeholders
            notes_text = re.sub(r'\*Optional:.*', '', notes_text)
            technical_notes = notes_text.strip()
        
        return {
            "ado_number": ado_number,
            "type": work_type,
            "acceptance_criteria": criteria,
            "technical_notes": technical_notes if technical_notes else None
        }
    
    def generate_dod(self, work_type: str, acceptance_criteria: List[str]) -> List[str]:
        """
        Generate Definition of Done based on work item type.
        
        Returns:
            List of DoD checklist items
        """
        base_dod = self.DOD_TEMPLATES.get(work_type, self.DOD_TEMPLATES["Task"])
        
        # For features, add AC verification items
        if work_type == "Feature":
            ac_dod = [f"Verified: {ac}" for ac in acceptance_criteria[:3]]
            return ac_dod + base_dod
        
        return base_dod
    
    def import_to_database(self, parsed_data: Dict, file_path: Path) -> str:
        """
        Import parsed ADO data to SQLite database.
        
        Returns:
            UUID of created ADO item
        """
        ado_id = str(uuid.uuid4())
        generated_dod = self.generate_dod(
            parsed_data["type"], 
            parsed_data["acceptance_criteria"]
        )
        
        with sqlite3.connect(self.db_path) as conn:
            # Check for duplicate ADO number
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id FROM ado_items WHERE ado_number = ?",
                (parsed_data["ado_number"],)
            )
            existing = cursor.fetchone()
            if existing:
                raise ValueError(
                    f"{parsed_data['ado_number']} already exists in database. "
                    f"Use 'resume ado {parsed_data['ado_number']}' to continue."
                )
            
            # Insert ADO item
            cursor.execute("""
                INSERT INTO ado_items 
                (id, ado_number, type, acceptance_criteria, technical_notes, 
                 generated_dod, status, file_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                ado_id,
                parsed_data["ado_number"],
                parsed_data["type"],
                json.dumps(parsed_data["acceptance_criteria"]),
                parsed_data["technical_notes"],
                json.dumps(generated_dod),
                "planning",
                str(file_path.absolute())
            ))
            
            # Insert DoD items as separate rows for tracking
            for dod_item in generated_dod:
                cursor.execute("""
                    INSERT INTO ado_dod_items (ado_id, dod_item, is_completed)
                    VALUES (?, ?, 0)
                """, (ado_id, dod_item))
            
            # Log creation activity
            cursor.execute("""
                INSERT INTO ado_activity (ado_id, activity_type, notes)
                VALUES (?, 'created', ?)
            """, (
                ado_id,
                f"Created {parsed_data['type']}: {parsed_data['ado_number']}"
            ))
            
            conn.commit()
        
        return ado_id
    
    def get_ado_by_number(self, ado_number: str) -> Optional[Dict]:
        """Retrieve ADO item by number."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    id, ado_number, type, acceptance_criteria, 
                    technical_notes, generated_dod, status, file_path,
                    created_at, updated_at, completed_at
                FROM ado_items
                WHERE ado_number = ?
            """, (ado_number,))
            row = cursor.fetchone()
            
            if row:
                return {
                    "id": row["id"],
                    "ado_number": row["ado_number"],
                    "type": row["type"],
                    "acceptance_criteria": json.loads(row["acceptance_criteria"]),
                    "technical_notes": row["technical_notes"],
                    "generated_dod": json.loads(row["generated_dod"]),
                    "status": row["status"],
                    "file_path": row["file_path"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "completed_at": row["completed_at"]
                }
            return None
    
    def list_active_ados(self) -> List[Dict]:
        """List all active (non-completed) ADO items."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("""
                SELECT ado_number, type, status, created_at
                FROM active_ados
            """)
            return [dict(row) for row in cursor.fetchall()]
    
    def update_status(self, ado_number: str, new_status: str):
        """Update ADO item status."""
        valid_statuses = ['planning', 'in-progress', 'blocked', 'completed']
        if new_status not in valid_statuses:
            raise ValueError(f"Invalid status. Must be one of: {', '.join(valid_statuses)}")
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE ado_items 
                SET status = ?
                WHERE ado_number = ?
            """, (new_status, ado_number))
            
            if cursor.rowcount == 0:
                raise ValueError(f"ADO item {ado_number} not found")
            
            conn.commit()


def main():
    """CLI entry point for ADO template parser."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python ado_parser.py <template_file_path>")
        print("   or: python ado_parser.py --list")
        print("   or: python ado_parser.py --resume <ADO-number>")
        sys.exit(1)
    
    parser = ADOTemplateParser()
    
    if sys.argv[1] == "--list":
        ados = parser.list_active_ados()
        if ados:
            print("\nActive ADO Items:")
            for ado in ados:
                print(f"  {ado['ado_number']} ({ado['type']}) - {ado['status']}")
        else:
            print("No active ADO items found.")
        return
    
    if sys.argv[1] == "--resume":
        if len(sys.argv) < 3:
            print("Error: ADO number required. Usage: --resume ADO-12345")
            sys.exit(1)
        ado_data = parser.get_ado_by_number(sys.argv[2])
        if ado_data:
            print(f"\nResumed {ado_data['ado_number']}:")
            print(f"  Type: {ado_data['type']}")
            print(f"  Status: {ado_data['status']}")
            print(f"  File: {ado_data['file_path']}")
        else:
            print(f"ADO item {sys.argv[2]} not found.")
        return
    
    # Parse and import template
    file_path = Path(sys.argv[1])
    if not file_path.exists():
        print(f"Error: File not found: {file_path}")
        sys.exit(1)
    
    try:
        print(f"Parsing {file_path.name}...")
        parsed = parser.parse_template(file_path)
        
        print(f"\n✓ Parsed successfully:")
        print(f"  ADO Number: {parsed['ado_number']}")
        print(f"  Type: {parsed['type']}")
        print(f"  Acceptance Criteria: {len(parsed['acceptance_criteria'])} items")
        
        print("\nGenerating Definition of Done...")
        dod = parser.generate_dod(parsed['type'], parsed['acceptance_criteria'])
        print(f"  Generated {len(dod)} DoD checklist items")
        
        print("\nImporting to database...")
        ado_id = parser.import_to_database(parsed, file_path)
        
        print(f"\n✅ Success! ADO item created:")
        print(f"  Tracking ID: {ado_id}")
        print(f"  ADO Number: {parsed['ado_number']}")
        print(f"  Status: planning")
        print(f"\nNext: Say 'resume ado {parsed['ado_number']}' to continue working")
        
    except ValueError as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
