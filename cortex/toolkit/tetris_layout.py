"""
CORTEX Tetris Layout Tool
=========================
Analyses HTML/CSS two-column (or N-column) grid panels and emits the
CSS patch that makes every column fill its shared row height — no blank
space, no overflow.  Named after the Tetris principle: every piece must
fill the available space, leaving no gaps.

SSOT: cortex-registry/knowledge/sdlc/tetris-layout-spec.yaml (auto-generated)
Prompt integration: .github/prompts/cortex-doc.prompt.md § Tetris-Fit Layout
Agent: .github/agents/docs/tetris-layout-agent.md

Usage (CLI):
    python3 -m cortex.toolkit.tetris_layout analyse --html docs/index.html \\
        --selector ".macc__body-inner"

Usage (API):
    from cortex.toolkit.tetris_layout import TetrisLayoutEngine
    engine = TetrisLayoutEngine()
    patch = engine.analyse_panel(panel_spec)
    print(patch.css)

Triggers:
    - User says "tetris fit", "tetris layout", "fill blank space",
      "no dead space", "fill like tetris", "stretch to fill",
      "align bottoms", "remove whitespace", "no gaps" in the context of
      HTML layout — the Documentation Orchestrator delegates to this tool.
"""

from __future__ import annotations

import json
import textwrap
from dataclasses import dataclass, field
from typing import Literal, Optional

# ── Type aliases ──────────────────────────────────────────────────────────────

FlexDirection = Literal["row", "column"]
GridFill = Literal["stretch", "start", "end", "center"]
ColumnRole = Literal["prose", "metric", "mixed", "role-grid", "custom"]


# ── Data models ───────────────────────────────────────────────────────────────

@dataclass
class ColumnSpec:
    """Describes a single column inside a multi-column panel."""

    selector: str
    """CSS selector for this column element, e.g. '.macc__desc'"""

    role: ColumnRole = "prose"
    """Semantic role — drives which flex/grid strategies are applied."""

    child_selectors: list[str] = field(default_factory=list)
    """Selectors for direct children that should participate in fill."""

    flex_children: list[str] = field(default_factory=list)
    """Children that should receive 'flex: 1' to absorb leftover height."""

    notes: str = ""
    """Human-readable description of what this column contains."""


@dataclass
class PanelSpec:
    """Describes a complete multi-column panel to be Tetris-fitted."""

    container_selector: str
    """CSS selector for the grid/flex container, e.g. '.macc__body-inner'"""

    layout: Literal["grid", "flex"] = "grid"
    """Whether the container uses CSS Grid or Flexbox."""

    columns: list[ColumnSpec] = field(default_factory=list)
    """Ordered list of column specs — left to right."""

    align_strategy: GridFill = "stretch"
    """Grid align-items or flex align-items value for the container."""

    notes: str = ""


@dataclass
class TetrisPatch:
    """Output of a Tetris layout analysis — a CSS patch + explanation."""

    panel: PanelSpec
    css: str
    """Ready-to-paste CSS block."""

    explanation: list[str]
    """Human-readable list of rules applied and why."""

    wcag_notes: list[str]
    """WCAG 2.2 / a11y reminders relevant to the layout change."""


# ── Core engine ───────────────────────────────────────────────────────────────

class TetrisLayoutEngine:
    """
    Stateless engine that converts a PanelSpec into a TetrisPatch.

    Algorithm (Tetris-Fit, v1):
    ─────────────────────────────────────────────────────────────────
    1. Container  → align-items: stretch  (columns share tallest height)
    2. Each col   → height: 100%          (col fills the shared row height)
                  → display: flex; flex-direction: column
    3. Flex child → flex: 1              (last / expandable child grows)
    4. Grid child → align-content: stretch (grid rows expand proportionally)
    5. Viz/chart  → flex: 1; justify-content: space-between
                    (spacer rows distribute evenly inside the panel)
    ─────────────────────────────────────────────────────────────────
    The algorithm is intentionally CSS-only — no JS, no ResizeObserver,
    no fixed pixel heights.  Pure declarative layout.
    """

    # ── Public API ────────────────────────────────────────────────────────────

    def analyse_panel(self, spec: PanelSpec) -> TetrisPatch:
        """
        Given a PanelSpec, return the CSS patch that tetris-fits the panel.

        Parameters
        ----------
        spec : PanelSpec
            Description of the container and its columns.

        Returns
        -------
        TetrisPatch
            CSS string + explanation bullets + WCAG notes.
        """
        css_blocks: list[str] = []
        explanation: list[str] = []
        wcag_notes: list[str] = []

        # ── Step 1: Container ─────────────────────────────────────────────────
        css_blocks.append(self._container_rule(spec))
        explanation.append(
            f"{spec.container_selector}: align-items→stretch so all columns "
            "share the tallest sibling height (Tetris Rule 1)."
        )

        # ── Step 2–4: Per-column rules ────────────────────────────────────────
        for col in spec.columns:
            col_css, col_explanation = self._column_rules(col)
            css_blocks.extend(col_css)
            explanation.extend(col_explanation)

        # ── Step 5: WCAG notes ────────────────────────────────────────────────
        wcag_notes = self._wcag_notes(spec)

        css = "\n\n".join(css_blocks)
        return TetrisPatch(panel=spec, css=css, explanation=explanation, wcag_notes=wcag_notes)

    def emit_spec_from_dict(self, raw: dict) -> PanelSpec:
        """
        Build a PanelSpec from a plain dict (e.g. loaded from YAML/JSON).
        Enables CLI and agent-driven invocation without importing dataclasses.

        Parameters
        ----------
        raw : dict
            Dict with keys matching PanelSpec / ColumnSpec fields.

        Returns
        -------
        PanelSpec
        """
        columns = [
            ColumnSpec(
                selector=c["selector"],
                role=c.get("role", "prose"),
                child_selectors=c.get("child_selectors", []),
                flex_children=c.get("flex_children", []),
                notes=c.get("notes", ""),
            )
            for c in raw.get("columns", [])
        ]
        return PanelSpec(
            container_selector=raw["container_selector"],
            layout=raw.get("layout", "grid"),
            columns=columns,
            align_strategy=raw.get("align_strategy", "stretch"),
            notes=raw.get("notes", ""),
        )

    # ── Private helpers ───────────────────────────────────────────────────────

    def _container_rule(self, spec: PanelSpec) -> str:
        align_prop = (
            "align-items" if spec.layout == "flex" else "align-items"
        )
        return textwrap.dedent(f"""\
            /* TETRIS-FIT — container: columns share max row height */
            {spec.container_selector} {{
              {align_prop}: {spec.align_strategy};
            }}""")

    def _column_rules(self, col: ColumnSpec) -> tuple[list[str], list[str]]:
        css_blocks: list[str] = []
        explanation: list[str] = []

        # Every column must fill the container row height
        base_rule = textwrap.dedent(f"""\
            /* TETRIS-FIT — column: fills shared grid-row height */
            {col.selector} {{
              display: flex;
              flex-direction: column;
              height: 100%;
            }}""")
        css_blocks.append(base_rule)
        explanation.append(
            f"{col.selector}: height:100% + flex-column so it fills the "
            "shared grid row (Tetris Rule 2)."
        )

        # Role-specific child rules
        if col.role in ("prose", "mixed"):
            # Last flex child (e.g. role-grid, chip list) absorbs leftover
            for child in col.flex_children:
                css_blocks.append(self._flex_child_rule(child, col.role))
                explanation.append(
                    f"{child}: flex:1 so it expands to fill leftover column "
                    "height (Tetris Rule 3)."
                )

        elif col.role == "role-grid":
            # The grid itself stretches + rows fill cells
            for child in col.child_selectors:
                css_blocks.append(self._grid_fill_rule(child))
                explanation.append(
                    f"{child}: align-content:stretch so grid rows expand to "
                    "fill available height (Tetris Rule 4)."
                )

        elif col.role == "metric":
            # The viz/chart panel at the bottom absorbs leftover height
            for child in col.flex_children:
                css_blocks.append(self._viz_rule(child))
                explanation.append(
                    f"{child}: flex:1 + justify-content:space-between so the "
                    "chart/viz fills remaining column height (Tetris Rule 5)."
                )

        return css_blocks, explanation

    @staticmethod
    def _flex_child_rule(selector: str, role: ColumnRole) -> str:
        return textwrap.dedent(f"""\
            /* TETRIS-FIT — flex child absorbs leftover column height */
            {selector} {{
              flex: 1;
              align-content: stretch;  /* rows in nested grids also stretch */
            }}""")

    @staticmethod
    def _grid_fill_rule(selector: str) -> str:
        return textwrap.dedent(f"""\
            /* TETRIS-FIT — grid fill: rows expand proportionally */
            {selector} {{
              flex: 1;
              align-content: stretch;
            }}""")

    @staticmethod
    def _viz_rule(selector: str) -> str:
        return textwrap.dedent(f"""\
            /* TETRIS-FIT — viz/chart panel fills remaining height */
            {selector} {{
              flex: 1;
              justify-content: space-between;
            }}""")

    @staticmethod
    def _wcag_notes(spec: PanelSpec) -> list[str]:
        notes = [
            "SC 2.5.8 — ensure no interactive element loses its 24×24px "
            "minimum touch target due to height changes.",
            "SC 1.4.4 — verify text reflow at 320px width: "
            "single-column stacked layout must remain readable.",
            "SC 2.4.11 — sticky nav must not obscure focused elements "
            "after layout height changes; scroll-margin-top still required.",
        ]
        for col in spec.columns:
            if col.role == "metric" and col.flex_children:
                notes.append(
                    f"Motion: {col.flex_children[0]} height changes must use "
                    "transform/opacity only — no height animation (P1 rule)."
                )
        return notes

    # ── Convenience: describe a panel from the CORTEX mission section ─────────

    @classmethod
    def cortex_mission_panel(cls, panel_variant: Literal[
        "understand_everything",
        "empower_everyone",
        "build_fearlessly",
    ]) -> PanelSpec:
        """
        Pre-built PanelSpec for each of the three CORTEX mission accordion panels.
        Used by the docs HTML design workflow to auto-apply Tetris-fit without
        the agent needing to re-derive the spec from the HTML source.

        Parameters
        ----------
        panel_variant : str
            Which accordion panel to generate a spec for.

        Returns
        -------
        PanelSpec
        """
        base = dict(
            container_selector=".macc__body-inner",
            layout="grid",
            align_strategy="stretch",
        )
        if panel_variant == "understand_everything":
            return PanelSpec(
                **base,
                notes="Item 01 — Understand Everything (cyan). "
                      "Left: 2 paragraphs. Right: 4 metric tiles + viz bar.",
                columns=[
                    ColumnSpec(
                        selector=".macc__desc",
                        role="prose",
                        notes="2 paragraphs — height driven by right column",
                    ),
                    ColumnSpec(
                        selector=".macc__metrics-col",
                        role="metric",
                        flex_children=[".macc__viz"],
                        notes="4 metric tiles (fixed) + viz bar (flex:1)",
                    ),
                ],
            )
        elif panel_variant == "empower_everyone":
            return PanelSpec(
                **base,
                notes="Item 02 — Empower Everyone (violet). "
                      "Left: 2 paragraphs + 6-pill 2×3 role grid (flex:1). "
                      "Right: 4 metric tiles + viz bar (flex:1).",
                columns=[
                    ColumnSpec(
                        selector=".macc__desc",
                        role="mixed",
                        flex_children=[".macc__role-grid"],
                        notes="2 paragraphs + role grid. Grid is the flex child.",
                    ),
                    ColumnSpec(
                        selector=".macc__metrics-col",
                        role="metric",
                        flex_children=[".macc__viz"],
                        notes="4 metric tiles + viz bar",
                    ),
                ],
            )
        else:  # build_fearlessly
            return PanelSpec(
                **base,
                notes="Item 03 — Build Fearlessly (emerald). "
                      "Left: 2 paragraphs. Right: 4 metric tiles + viz bar.",
                columns=[
                    ColumnSpec(
                        selector=".macc__desc",
                        role="prose",
                        notes="2 paragraphs — height driven by right column",
                    ),
                    ColumnSpec(
                        selector=".macc__metrics-col",
                        role="metric",
                        flex_children=[".macc__viz"],
                        notes="4 metric tiles + viz bar",
                    ),
                ],
            )


# ── CLI entry point ────────────────────────────────────────────────────────────

def _cli() -> None:
    """Minimal CLI: python3 -m cortex.toolkit.tetris_layout <json-spec>"""
    import argparse
    import sys

    parser = argparse.ArgumentParser(
        description="CORTEX Tetris Layout — emit CSS patch for gap-free panels"
    )
    sub = parser.add_subparsers(dest="cmd")

    # analyse sub-command: takes a JSON spec on stdin or --spec arg
    analyse = sub.add_parser("analyse", help="Analyse a panel spec and emit CSS")
    analyse.add_argument(
        "--spec", type=str, default=None,
        help="JSON panel spec string. Reads from stdin if omitted."
    )
    analyse.add_argument(
        "--variant", choices=[
            "understand_everything", "empower_everyone", "build_fearlessly"
        ],
        default=None,
        help="Use a pre-built CORTEX mission panel spec."
    )

    args = parser.parse_args()

    engine = TetrisLayoutEngine()

    if args.cmd == "analyse":
        if args.variant:
            spec = TetrisLayoutEngine.cortex_mission_panel(args.variant)
        elif args.spec:
            raw = json.loads(args.spec)
            spec = engine.emit_spec_from_dict(raw)
        else:
            raw = json.load(sys.stdin)
            spec = engine.emit_spec_from_dict(raw)

        patch = engine.analyse_panel(spec)

        print("/* ── TETRIS-FIT CSS PATCH ── */")
        print(patch.css)
        print("\n/* ── EXPLANATION ── */")
        for rule in patch.explanation:
            print(f"/*  {rule}  */")
        print("\n/* ── WCAG NOTES ── */")
        for note in patch.wcag_notes:
            print(f"/*  {note}  */")
    else:
        parser.print_help()


if __name__ == "__main__":
    _cli()
