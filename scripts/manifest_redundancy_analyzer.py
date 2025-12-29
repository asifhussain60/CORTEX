#!/usr/bin/env python3
"""
Manifest Redundancy Analyzer
Quantifies redundancy across 14 CORTEX orchestrator manifests

Author: Asif Hussain
Created: 2025-12-22 (Week 15 Day 1)
Purpose: Calculate 60% redundancy baseline for modularization strategy
"""

import yaml
import json
from pathlib import Path
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
import difflib

# Manifest paths
MANIFEST_DIR = Path(__file__).parent.parent / "cortex-brain" / "manifests" / "orchestrators"

TARGET_MANIFESTS = [
    "manifest-schema.yaml",
    "planning-system-4.0-manifest.yaml",
    "tdd-orchestrator-v4-manifest.yaml",
    "ado-planning-manifest.yaml",
    "code-sanitization-manifest.yaml",
    "refinement-orchestrator-manifest.yaml",
    "debug-orchestrator-manifest.yaml",
    "cortex-lens-v3-manifest.yaml",
    "intelligent-dashboard-manifest.yaml",
    "orchestrator-enhancement-manifest.yaml",
    "technical-documentation-orchestrator-manifest.yaml",
]


class ManifestRedundancyAnalyzer:
    """Analyze redundancy patterns across CORTEX manifests"""
    
    def __init__(self):
        self.manifests: Dict[str, dict] = {}
        self.field_occurrences: Dict[str, List[str]] = defaultdict(list)
        self.value_similarities: Dict[str, Dict[str, float]] = defaultdict(dict)
        self.redundancy_metrics: Dict[str, any] = {}
        
    def load_manifests(self) -> int:
        """Load all target manifests"""
        loaded = 0
        for filename in TARGET_MANIFESTS:
            filepath = MANIFEST_DIR / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.manifests[filename] = yaml.safe_load(f)
                    loaded += 1
                    print(f"✓ Loaded: {filename}")
                except Exception as e:
                    print(f"✗ Failed to load {filename}: {e}")
            else:
                print(f"✗ Not found: {filename}")
        
        return loaded
    
    def extract_all_field_paths(self, data: dict, prefix: str = "") -> List[str]:
        """Recursively extract all field paths from nested dict"""
        paths = []
        
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{prefix}.{key}" if prefix else key
                paths.append(current_path)
                
                if isinstance(value, (dict, list)):
                    paths.extend(self.extract_all_field_paths(value, current_path))
        
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    paths.extend(self.extract_all_field_paths(item, f"{prefix}[{i}]"))
        
        return paths
    
    def analyze_field_redundancy(self):
        """Identify fields appearing across multiple manifests"""
        print("\n" + "="*60)
        print("FIELD REDUNDANCY ANALYSIS")
        print("="*60)
        
        for manifest_name, data in self.manifests.items():
            field_paths = self.extract_all_field_paths(data)
            
            for path in field_paths:
                self.field_occurrences[path].append(manifest_name)
        
        # Group by occurrence count
        by_count = defaultdict(list)
        for path, manifests in self.field_occurrences.items():
            count = len(manifests)
            if count > 1:  # Only redundant fields
                by_count[count].append((path, manifests))
        
        total_redundant_fields = sum(len(fields) for fields in by_count.values())
        
        print(f"\nTotal unique field paths analyzed: {len(self.field_occurrences)}")
        print(f"Redundant fields (appearing in 2+ manifests): {total_redundant_fields}")
        
        print("\n--- Top Redundant Fields ---")
        for count in sorted(by_count.keys(), reverse=True)[:5]:
            print(f"\n{count} manifests share these fields:")
            for path, manifests in by_count[count][:10]:  # Top 10 per count
                print(f"  • {path}")
                print(f"    In: {', '.join([m.split('-')[0] for m in manifests[:3]])}...")
        
        return total_redundant_fields, len(self.field_occurrences)
    
    def analyze_metadata_redundancy(self):
        """Analyze metadata section redundancy"""
        print("\n" + "="*60)
        print("METADATA REDUNDANCY ANALYSIS")
        print("="*60)
        
        metadata_fields = defaultdict(list)
        
        for manifest_name, data in self.manifests.items():
            if 'metadata' in data:
                meta = data['metadata']
                for field in meta.keys():
                    metadata_fields[field].append(manifest_name)
        
        print(f"\nTotal metadata fields found: {len(metadata_fields)}")
        
        # Standard metadata fields (should be in ALL manifests)
        standard_fields = [
            'orchestrator_name', 'version', 'description', 'category',
            'status', 'last_updated', 'maintainer'
        ]
        
        print("\n--- Standard Metadata Field Coverage ---")
        missing_standard = []
        for field in standard_fields:
            count = len(metadata_fields.get(field, []))
            coverage = (count / len(self.manifests)) * 100
            status = "✓" if coverage > 70 else "✗"
            print(f"{status} {field}: {count}/{len(self.manifests)} ({coverage:.1f}%)")
            
            if coverage < 70:
                missing_standard.append((field, coverage))
        
        redundancy_score = (len([f for f in metadata_fields if len(metadata_fields[f]) > 1]) / len(metadata_fields)) * 100
        
        return redundancy_score, missing_standard
    
    def analyze_phase_patterns(self):
        """Analyze phase structure redundancy"""
        print("\n" + "="*60)
        print("PHASE STRUCTURE REDUNDANCY ANALYSIS")
        print("="*60)
        
        phase_field_names = ['phases', 'workflow', 'execution_phases']
        
        manifests_with_phases = []
        common_phase_fields = Counter()
        phase_names = Counter()
        
        for manifest_name, data in self.manifests.items():
            for phase_key in phase_field_names:
                if phase_key in data:
                    manifests_with_phases.append(manifest_name)
                    phases = data[phase_key]
                    
                    if isinstance(phases, list):
                        for phase in phases:
                            if isinstance(phase, dict):
                                for field in phase.keys():
                                    common_phase_fields[field] += 1
                                
                                # Track phase names/ids
                                for name_key in ['name', 'id', 'phase_id']:
                                    if name_key in phase:
                                        phase_names[phase[name_key]] += 1
        
        print(f"\nManifests with phase structures: {len(set(manifests_with_phases))}")
        print(f"Unique phase field names: {len(common_phase_fields)}")
        
        print("\n--- Most Common Phase Fields ---")
        for field, count in common_phase_fields.most_common(15):
            print(f"  • {field}: appears {count} times")
        
        print("\n--- Most Common Phase Names ---")
        for name, count in phase_names.most_common(10):
            if count > 1:
                print(f"  • '{name}': appears in {count} manifests")
        
        redundancy_pct = (len([f for f, c in common_phase_fields.items() if c > 1]) / max(len(common_phase_fields), 1)) * 100
        
        return redundancy_pct
    
    def analyze_requirements_redundancy(self):
        """Analyze requirements section redundancy"""
        print("\n" + "="*60)
        print("REQUIREMENTS REDUNDANCY ANALYSIS")
        print("="*60)
        
        requirement_fields = Counter()
        requirement_patterns = []
        
        for manifest_name, data in self.manifests.items():
            if 'requirements' in data:
                reqs = data['requirements']
                
                if isinstance(reqs, list):
                    for req in reqs:
                        if isinstance(req, dict):
                            for field in req.keys():
                                requirement_fields[field] += 1
                            
                            # Extract requirement structure
                            req_structure = tuple(sorted(req.keys()))
                            requirement_patterns.append((manifest_name, req_structure))
        
        print(f"\nTotal requirement entries analyzed: {len(requirement_patterns)}")
        print(f"Unique requirement fields: {len(requirement_fields)}")
        
        print("\n--- Standard Requirement Fields ---")
        for field, count in requirement_fields.most_common(20):
            print(f"  • {field}: {count} occurrences")
        
        # Group by structure pattern
        structure_counts = Counter([s for _, s in requirement_patterns])
        print(f"\n--- Requirement Structure Patterns ---")
        print(f"Unique patterns found: {len(structure_counts)}")
        
        for i, (structure, count) in enumerate(structure_counts.most_common(3)):
            print(f"\nPattern {i+1} (used {count} times):")
            print(f"  Fields: {', '.join(structure[:5])}...")
        
        redundancy_pct = (len([f for f, c in requirement_fields.items() if c > 1]) / max(len(requirement_fields), 1)) * 100
        
        return redundancy_pct
    
    def calculate_textual_similarity(self):
        """Calculate textual similarity between manifests"""
        print("\n" + "="*60)
        print("TEXTUAL SIMILARITY ANALYSIS")
        print("="*60)
        
        # Convert each manifest to normalized text
        manifest_texts = {}
        for name, data in self.manifests.items():
            text = yaml.dump(data, default_flow_style=False)
            manifest_texts[name] = text
        
        # Pairwise comparison
        similarities = []
        manifest_names = list(manifest_texts.keys())
        
        for i in range(len(manifest_names)):
            for j in range(i + 1, len(manifest_names)):
                name1, name2 = manifest_names[i], manifest_names[j]
                text1, text2 = manifest_texts[name1], manifest_texts[name2]
                
                # Use SequenceMatcher for similarity
                ratio = difflib.SequenceMatcher(None, text1, text2).ratio()
                similarities.append((name1, name2, ratio))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[2], reverse=True)
        
        print(f"\nAnalyzed {len(similarities)} manifest pairs")
        print("\n--- Top 10 Most Similar Pairs ---")
        
        for name1, name2, ratio in similarities[:10]:
            pct = ratio * 100
            name1_short = name1.replace('-manifest.yaml', '').replace('-orchestrator', '')
            name2_short = name2.replace('-manifest.yaml', '').replace('-orchestrator', '')
            print(f"  {pct:5.1f}% similar: {name1_short:30s} ↔ {name2_short}")
        
        avg_similarity = sum(s[2] for s in similarities) / len(similarities) * 100
        print(f"\nAverage pairwise similarity: {avg_similarity:.1f}%")
        
        return avg_similarity, similarities
    
    def calculate_overall_redundancy(self, field_redundancy: float, metadata_redundancy: float,
                                      phase_redundancy: float, requirements_redundancy: float,
                                      textual_similarity: float) -> float:
        """Calculate weighted overall redundancy score"""
        
        # Weighted average (metadata and phases most important)
        weights = {
            'field': 0.15,
            'metadata': 0.25,
            'phase': 0.25,
            'requirements': 0.20,
            'textual': 0.15
        }
        
        overall = (
            field_redundancy * weights['field'] +
            metadata_redundancy * weights['metadata'] +
            phase_redundancy * weights['phase'] +
            requirements_redundancy * weights['requirements'] +
            textual_similarity * weights['textual']
        )
        
        return overall
    
    def generate_report(self, output_path: Path):
        """Generate comprehensive redundancy report"""
        
        # Run all analyses
        field_red_count, total_fields = self.analyze_field_redundancy()
        field_redundancy_pct = (field_red_count / max(total_fields, 1)) * 100
        
        metadata_redundancy, missing_std = self.analyze_metadata_redundancy()
        phase_redundancy = self.analyze_phase_patterns()
        requirements_redundancy = self.analyze_requirements_redundancy()
        textual_similarity, similarities = self.calculate_textual_similarity()
        
        overall_redundancy = self.calculate_overall_redundancy(
            field_redundancy_pct, metadata_redundancy, phase_redundancy,
            requirements_redundancy, textual_similarity
        )
        
        # Generate report
        print("\n" + "="*60)
        print("OVERALL REDUNDANCY SUMMARY")
        print("="*60)
        
        print(f"\n📊 Component Redundancy Scores:")
        print(f"   • Field Redundancy:        {field_redundancy_pct:5.1f}%")
        print(f"   • Metadata Redundancy:     {metadata_redundancy:5.1f}%")
        print(f"   • Phase Redundancy:        {phase_redundancy:5.1f}%")
        print(f"   • Requirements Redundancy: {requirements_redundancy:5.1f}%")
        print(f"   • Textual Similarity:      {textual_similarity:5.1f}%")
        print(f"\n🎯 OVERALL REDUNDANCY:        {overall_redundancy:5.1f}%")
        
        # Write detailed report
        report_content = f"""# Manifest Redundancy Audit Report
**Week 15 Day 1 - December 22, 2025**
**Author:** Asif Hussain
**Manifests Analyzed:** {len(self.manifests)}

---

## Executive Summary

**Overall Redundancy Score: {overall_redundancy:.1f}%**

This audit quantifies redundancy across {len(self.manifests)} CORTEX orchestrator manifests to establish
a baseline for modularization and inheritance strategies.

### Key Findings

1. **{field_redundancy_pct:.1f}% Field Redundancy**: {field_red_count} of {total_fields} unique field paths appear in multiple manifests
2. **{metadata_redundancy:.1f}% Metadata Redundancy**: Standard metadata fields are repeated across manifests
3. **{phase_redundancy:.1f}% Phase Structure Redundancy**: Common phase patterns duplicated
4. **{requirements_redundancy:.1f}% Requirements Redundancy**: Requirement structures overlap significantly
5. **{textual_similarity:.1f}% Average Textual Similarity**: Manifests share substantial boilerplate

---

## Component Analysis

### 1. Field Redundancy ({field_redundancy_pct:.1f}%)

**Total unique field paths:** {total_fields}
**Redundant fields:** {field_red_count}

Fields appearing across multiple manifests indicate opportunities for base schemas and inheritance.

### 2. Metadata Redundancy ({metadata_redundancy:.1f}%)

**Standard Fields Missing Coverage:**
"""
        
        for field, coverage in missing_std:
            report_content += f"\n- `{field}`: Only {coverage:.1f}% coverage (should be 100%)"
        
        report_content += f"""

**Recommendation:** Create `base-manifest.yaml` with all standard metadata fields.

### 3. Phase Redundancy ({phase_redundancy:.1f}%)

Common phase structures (DoR, DoD, validation, rollback) are duplicated across manifests.

**Recommendation:** Extract common phase templates into `cortex-brain/manifests/shared/phase-templates.yaml`

### 4. Requirements Redundancy ({requirements_redundancy:.1f}%)

Requirement structures follow similar patterns but are duplicated across manifests.

**Recommendation:** Create requirement templates with inheritance support.

### 5. Textual Similarity ({textual_similarity:.1f}%)

**Top Similar Manifest Pairs:**
"""
        
        for name1, name2, ratio in similarities[:10]:
            pct = ratio * 100
            name1_short = name1.replace('-manifest.yaml', '')
            name2_short = name2.replace('-manifest.yaml', '')
            report_content += f"\n- **{pct:.1f}%**: `{name1_short}` ↔ `{name2_short}`"
        
        report_content += f"""

---

## Modularization Strategy

### Goal: Reduce redundancy from {overall_redundancy:.1f}% to <40%

### Phase 1: Base Manifest Creation
- Create `base-orchestrator-manifest.yaml` with standard fields
- Define inheritance mechanism (`inherits_from` key)
- Establish merge rules (child overrides parent)

### Phase 2: Shared Component Library
- `shared/metadata-templates.yaml`: Standard metadata blocks
- `shared/phase-templates.yaml`: Common phase patterns
- `shared/requirement-templates.yaml`: Requirement structures
- `shared/validation-templates.yaml`: DoR/DoD patterns

### Phase 3: Manifest Refactoring
- Convert 14 manifests to use inheritance
- Extract redundant sections to shared templates
- Validate functionality preserved

### Phase 4: Validation & Testing
- Automated schema validation
- Manifest inheritance resolver
- Regression testing of orchestrators

---

## Expected Outcomes

### Redundancy Reduction
- **Before:** {overall_redundancy:.1f}% redundancy
- **Target:** <40% redundancy
- **Reduction:** ≥{overall_redundancy - 40:.1f}% improvement

### Maintainability Improvements
- Centralized metadata standards
- Single source of truth for common patterns
- Easier manifest updates (change once, inherit everywhere)

### Token Efficiency
- Reduced manifest file sizes
- Lower token consumption in AI prompts
- Faster manifest parsing

---

## Next Steps

1. ✅ **Complete**: Redundancy quantification (this report)
2. ⏳ **Next**: Design inheritance hierarchy
3. ⏳ **Planned**: Create base manifest and shared templates
4. ⏳ **Planned**: Refactor existing manifests
5. ⏳ **Planned**: Implement validation tooling

---

**Report Generated:** {Path(__file__).name}
**Output Location:** {output_path}
"""
        
        # Write report
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        print(f"\n✓ Report written to: {output_path}")
        
        return overall_redundancy


def main():
    """Main execution"""
    print("="*60)
    print("CORTEX MANIFEST REDUNDANCY ANALYZER")
    print("Week 15 Day 1 - December 22, 2025")
    print("="*60)
    
    analyzer = ManifestRedundancyAnalyzer()
    
    # Load manifests
    loaded = analyzer.load_manifests()
    print(f"\nLoaded {loaded}/{len(TARGET_MANIFESTS)} manifests")
    
    if loaded < 5:
        print("\n⚠️  Too few manifests loaded. Check paths.")
        return
    
    # Generate report
    output_path = Path(__file__).parent.parent / "cortex-brain" / "documents" / "reports" / "manifest-redundancy-audit-2025-12-22.md"
    
    overall_redundancy = analyzer.generate_report(output_path)
    
    # Success indicator
    if overall_redundancy >= 60:
        print(f"\n✓ SUCCESS: {overall_redundancy:.1f}% redundancy quantified (target: ≥60%)")
    else:
        print(f"\n⚠️  WARNING: {overall_redundancy:.1f}% redundancy (expected ≥60%)")
    
    print("\n" + "="*60)
    print("ANALYSIS COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
