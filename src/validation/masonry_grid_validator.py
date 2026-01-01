"""
Masonry Grid Validation Tool
Ensures Tetris/masonry layouts completely fill containing panels without gaps.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

from typing import List, Tuple, Dict
from dataclasses import dataclass


@dataclass
class GridCard:
    """Represents a single card in the masonry grid."""
    id: int
    col_span: int
    row_span: int
    name: str


@dataclass
class ValidationResult:
    """Result of grid validation."""
    is_valid: bool
    total_cells: int
    filled_cells: int
    coverage_percent: float
    gaps: List[Tuple[int, int]]  # (row, col) positions of gaps
    message: str


class MasonryGridValidator:
    """
    Validates masonry grid layouts to ensure complete fills.
    
    Grid Rules:
    - Standard grid: 3 columns × N rows
    - Each card: (col_span, row_span)
    - Validation: All cells must be filled (100% coverage)
    """
    
    def __init__(self, num_columns: int = 3):
        """
        Initialize validator.
        
        Args:
            num_columns: Number of columns in grid (default: 3)
        """
        self.num_columns = num_columns
    
    def validate_layout(
        self,
        cards: List[GridCard],
        panel_name: str = "Unknown"
    ) -> ValidationResult:
        """
        Validate that cards completely fill the grid.
        
        Args:
            cards: List of GridCard objects
            panel_name: Name of panel for error reporting
            
        Returns:
            ValidationResult with validation status and details
        """
        # Calculate minimum rows needed
        total_cell_area = sum(card.col_span * card.row_span for card in cards)
        min_rows = (total_cell_area + self.num_columns - 1) // self.num_columns
        
        # Create grid matrix
        grid = [[False] * self.num_columns for _ in range(min_rows)]
        
        # Place cards in grid
        current_row = 0
        current_col = 0
        
        for card in cards:
            # Find next available position
            placed = False
            for row in range(min_rows):
                for col in range(self.num_columns):
                    if self._can_place_card(grid, row, col, card):
                        self._place_card(grid, row, col, card)
                        placed = True
                        break
                if placed:
                    break
            
            if not placed:
                return ValidationResult(
                    is_valid=False,
                    total_cells=self.num_columns * min_rows,
                    filled_cells=self._count_filled(grid),
                    coverage_percent=0.0,
                    gaps=self._find_gaps(grid),
                    message=f"❌ {panel_name}: Cannot place card '{card.name}' "
                           f"({card.col_span}×{card.row_span}) - grid overflow"
                )
        
        # Count filled cells
        filled = self._count_filled(grid)
        total = self.num_columns * min_rows
        coverage = (filled / total * 100) if total > 0 else 0
        
        # Find gaps
        gaps = self._find_gaps(grid)
        
        if gaps:
            gap_positions = ", ".join(f"({r},{c})" for r, c in gaps[:5])
            return ValidationResult(
                is_valid=False,
                total_cells=total,
                filled_cells=filled,
                coverage_percent=coverage,
                gaps=gaps,
                message=f"❌ {panel_name}: {len(gaps)} gaps found at {gap_positions}"
            )
        
        return ValidationResult(
            is_valid=True,
            total_cells=total,
            filled_cells=filled,
            coverage_percent=100.0,
            gaps=[],
            message=f"✅ {panel_name}: Complete fill validated "
                   f"({len(cards)} cards, {total} cells, {min_rows} rows)"
        )
    
    def _can_place_card(
        self,
        grid: List[List[bool]],
        row: int,
        col: int,
        card: GridCard
    ) -> bool:
        """Check if card can be placed at position."""
        if row + card.row_span > len(grid):
            return False
        if col + card.col_span > self.num_columns:
            return False
        
        for r in range(row, row + card.row_span):
            for c in range(col, col + card.col_span):
                if grid[r][c]:
                    return False
        
        return True
    
    def _place_card(
        self,
        grid: List[List[bool]],
        row: int,
        col: int,
        card: GridCard
    ):
        """Place card in grid."""
        for r in range(row, row + card.row_span):
            for c in range(col, col + card.col_span):
                grid[r][c] = True
    
    def _count_filled(self, grid: List[List[bool]]) -> int:
        """Count filled cells in grid."""
        return sum(sum(row) for row in grid)
    
    def _find_gaps(self, grid: List[List[bool]]) -> List[Tuple[int, int]]:
        """Find unfilled cell positions."""
        gaps = []
        for r, row in enumerate(grid):
            for c, filled in enumerate(row):
                if not filled:
                    gaps.append((r, c))
        return gaps
    
    def generate_css_rules(
        self,
        cards: List[GridCard],
        selector_prefix: str
    ) -> str:
        """
        Generate CSS rules for validated layout.
        
        Args:
            cards: List of GridCard objects (already validated)
            selector_prefix: CSS selector prefix (e.g., "#panel .card")
            
        Returns:
            CSS string with grid-column and grid-row rules
        """
        css_lines = [f"/* Validated masonry grid: {len(cards)} cards */"]
        
        for card in cards:
            css_lines.append(
                f"{selector_prefix}:nth-child({card.id}) {{\n"
                f"    grid-column: span {card.col_span};\n"
                f"    grid-row: span {card.row_span};\n"
                f"}}"
            )
        
        return "\n".join(css_lines)


# Predefined validated layouts for CORTEX panels
VALIDATED_LAYOUTS = {
    "planning": [
        GridCard(1, 3, 1, "Planning System"),
        GridCard(2, 3, 1, "ADO Orchestrator"),
        GridCard(3, 3, 1, "ADO Operations"),
        GridCard(4, 3, 1, "ADO Planning"),
    ],
    "execution": [
        GridCard(1, 3, 2, "TDD Orchestrator"),
        GridCard(2, 3, 2, "Execution Orchestrator"),
    ],
    "system": [
        GridCard(1, 2, 2, "Cleanup Orchestrator"),
        GridCard(2, 1, 1, "Sanitization"),
        GridCard(3, 1, 1, "System Integrity"),
        GridCard(4, 3, 2, "Git Checkpoint"),
    ],
    "analysis": [
        GridCard(1, 3, 2, "Refinement"),
        GridCard(2, 3, 1, "CORTEX Lens"),
        GridCard(3, 3, 1, "Architectural Review"),
    ],
    "debug": [
        GridCard(1, 2, 3, "Debug Orchestrator"),
        GridCard(2, 1, 3, "Rollback Orchestrator"),
    ],
}


def validate_all_cortex_layouts() -> Dict[str, ValidationResult]:
    """Validate all predefined CORTEX panel layouts."""
    validator = MasonryGridValidator(num_columns=3)
    results = {}
    
    for panel_name, cards in VALIDATED_LAYOUTS.items():
        results[panel_name] = validator.validate_layout(cards, panel_name.title())
    
    return results


if __name__ == "__main__":
    # Validate all layouts
    print("🔍 CORTEX Masonry Grid Validation\n")
    
    results = validate_all_cortex_layouts()
    
    all_valid = True
    for panel_name, result in results.items():
        print(result.message)
        if not result.is_valid:
            all_valid = False
            print(f"   Coverage: {result.coverage_percent:.1f}%")
            print(f"   Gaps: {len(result.gaps)}")
    
    print(f"\n{'✅ All layouts valid!' if all_valid else '❌ Validation failed!'}")
