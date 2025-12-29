#!/usr/bin/env python3
"""
Automated Evidence Template Extraction Script

Purpose: Batch-extract large evidence/rationale blocks from brain-protection-rules.yaml
         to separate template files, replacing with #file: references.

Target: Reduce brain-protection-rules.yaml from 58K tokens to 8K tokens (86% reduction)

Author: Asif Hussain
Version: 2.0
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Tuple

class EvidenceTemplateExtractor:
    """Extracts verbose evidence/rationale blocks to separate template files."""
    
    def __init__(self, yaml_path: Path, templates_dir: Path):
        self.yaml_path = yaml_path
        self.templates_dir = templates_dir
        self.min_chars = 500  # Minimum chars to extract
        self.extracted_count = 0
        self.tokens_saved = 0
        self.categories = {
            'planning': ['INCREMENTAL_PLAN_GENERATION', 'PLANNING_DOR', 'PLANNING_DOD'],
            'tdd': ['TDD_ENFORCEMENT', 'RED_PHASE', 'GREEN_PHASE', 'REFACTOR'],
            'security': ['OWASP', 'SECURITY', 'THREAT', 'VULNERABILITY'],
            'git': ['GIT_CHECKPOINT', 'DIRTY_STATE', 'COMMIT', 'BRANCH'],
            'architecture': ['TOKEN_EFFICIENCY', 'BRAIN_ARCHITECTURE', 'INTEGRATION']
        }
        
    def extract_all(self) -> Dict[str, any]:
        """Main extraction workflow."""
        print("🔍 Phase 1: Scanning YAML for extraction candidates...")
        
        # Read YAML content
        with open(self.yaml_path, 'r') as f:
            content = f.read()
        
        original_size = len(content)
        original_tokens = original_size // 4
        
        # Find all evidence/rationale blocks
        candidates = self._find_extraction_candidates(content)
        print(f"   Found {len(candidates)} candidates for extraction (>{self.min_chars} chars each)")
        
        # Sort by size (largest first for maximum impact)
        candidates.sort(key=lambda x: len(x['content']), reverse=True)
        
        print(f"\n� Phase 2: Extracting templates...")
        
        # Extract each candidate
        modified_content = content
        offset = 0
        
        for idx, candidate in enumerate(candidates, 1):
            file_ref = self._extract_template(candidate, idx)
            
            # Replace in content
            start = candidate['start'] + offset
            end = candidate['end'] + offset
            old_text = modified_content[start:end]
            new_text = f"{candidate['field']}: \"{file_ref}\"\n"
            
            modified_content = modified_content[:start] + new_text + modified_content[end:]
            offset += len(new_text) - len(old_text)
            
            # Show progress every 5 templates
            if idx % 5 == 0:
                print(f"   Extracted {idx}/{len(candidates)} templates...")
        
        # Calculate savings
        new_size = len(modified_content)
        new_tokens = new_size // 4
        tokens_saved = original_tokens - new_tokens
        
        print(f"\n✅ Extraction complete: {self.extracted_count} templates created")
        print(f"💾 Size reduction: {original_size:,} → {new_size:,} chars ({original_size - new_size:,} saved)")
        print(f"💾 Token reduction: {original_tokens:,} → {new_tokens:,} tokens ({tokens_saved:,} saved)")
        
        # Write modified content
        backup_path = self.yaml_path.with_suffix('.yaml.before_batch')
        self.yaml_path.rename(backup_path)
        
        with open(self.yaml_path, 'w') as f:
            f.write(modified_content)
        
        print(f"\n✅ Updated {self.yaml_path.name}")
        print(f"📦 Backup saved: {backup_path.name}")
        
        return {
            'templates_created': self.extracted_count,
            'tokens_saved': tokens_saved,
            'original_tokens': original_tokens,
            'new_tokens': new_tokens,
            'candidates_found': len(candidates)
        }
    
    def _find_extraction_candidates(self, content: str) -> List[Dict]:
        """Find all evidence/rationale blocks suitable for extraction."""
        candidates = []
        
        # Pattern 1: evidence_template: | blocks
        evidence_pattern = r'(evidence_template):\s*\|\n((?:\s+.*\n)+?)(?=\n\s{0,2}\w+:|$)'
        for match in re.finditer(evidence_pattern, content, re.MULTILINE):
            full_content = match.group(2)
            if len(full_content) >= self.min_chars and not full_content.strip().startswith('#file:'):
                candidates.append({
                    'type': 'evidence_template',
                    'field': match.group(1),
                    'content': full_content,
                    'start': match.start(),
                    'end': match.end()
                })
        
        # Pattern 2: rationale: | blocks
        rationale_pattern = r'(rationale):\s*\|\n((?:\s+.*\n)+?)(?=\n\s{0,2}\w+:|$)'
        for match in re.finditer(rationale_pattern, content, re.MULTILINE):
            full_content = match.group(2)
            if len(full_content) >= self.min_chars:
                candidates.append({
                    'type': 'rationale',
                    'field': match.group(1),
                    'content': full_content,
                    'start': match.start(),
                    'end': match.end()
                })
        
        return candidates
    
    def _extract_template(self, candidate: Dict, index: int) -> str:
        """Extract single template to file and return file reference."""
        # Extract rule name from context
        rule_name = self._extract_rule_name(candidate['start'])
        
        # Determine category
        category = self._determine_category(rule_name)
        
        # Create filename
        filename = f"{rule_name}.md"
        
        # Determine subdirectory
        if candidate['type'] == 'rationale':
            template_path = self.templates_dir.parent / "rationales" / filename
        else:
            template_path = self.templates_dir / category / filename
        
        # Ensure directory exists
        template_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write template content (strip leading whitespace)
        clean_content = self._clean_content(candidate['content'])
        with open(template_path, 'w') as f:
            f.write(clean_content)
        
        self.extracted_count += 1
        self.tokens_saved += len(candidate['content']) // 4
        
        chars = len(candidate['content'])
        tokens = chars // 4
        print(f"   ✅ {category}/{filename} ({chars:,} chars, ~{tokens} tokens)")
        
        # Return file reference path
        if candidate['type'] == 'rationale':
            return f"#file:documents/rationales/{filename}"
        else:
            return f"#file:documents/evidence-templates/{category}/{filename}"
    
    def _extract_rule_name(self, position: int) -> str:
        """Extract rule name from YAML context."""
        with open(self.yaml_path, 'r') as f:
            content = f.read()
        
        # Look backwards for rule name (uppercase with underscores)
        chunk = content[max(0, position-1000):position]
        
        # Find last rule name pattern before position
        matches = list(re.finditer(r'^\s{2}([A-Z_]+):\s*$', chunk, re.MULTILINE))
        if matches:
            return matches[-1].group(1)
        
        return f"UNKNOWN_{position}"
    
    def _determine_category(self, rule_name: str) -> str:
        """Determine category directory based on rule name."""
        rule_upper = rule_name.upper()
        
        for category, keywords in self.categories.items():
            if any(keyword in rule_upper for keyword in keywords):
                return category
        
        return 'misc'
    
    def _clean_content(self, content: str) -> str:
        """Clean template content (remove leading indent)."""
        lines = content.split('\n')
        
        # Find minimum indent
        min_indent = float('inf')
        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                min_indent = min(min_indent, indent)
        
        # Remove minimum indent from all lines
        if min_indent < float('inf'):
            cleaned_lines = [line[min_indent:] if line.strip() else '' for line in lines]
            return '\n'.join(cleaned_lines)
        
        return content


def main():
    """Main execution."""
    print("=" * 70)
    print("CORTEX Evidence Template Batch Extraction")
    print("=" * 70)
    print()
    
    # Paths
    cortex_root = Path(__file__).parent.parent
    yaml_path = cortex_root / "cortex-brain" / "brain-protection-rules.yaml"
    templates_dir = cortex_root / "cortex-brain" / "documents" / "evidence-templates"
    
    # Validate paths
    if not yaml_path.exists():
        print(f"❌ Error: {yaml_path} not found")
        return 1
    
    # Create extractor
    extractor = EvidenceTemplateExtractor(yaml_path, templates_dir)
    
    # Extract templates
    results = extractor.extract_all()
    
    # Show summary
    print()
    print("=" * 70)
    print("📊 Extraction Summary")
    print("=" * 70)
    print(f"Templates created:   {results['templates_created']}")
    print(f"Original tokens:     {results['original_tokens']:,}")
    print(f"New tokens:          {results['new_tokens']:,}")
    print(f"Tokens saved:        {results['tokens_saved']:,}")
    print(f"Reduction:           {(results['tokens_saved'] / results['original_tokens'] * 100):.1f}%")
    print()
    print("✅ Batch extraction complete!")
    print()
    print("📍 NEXT STEPS:")
    print("   1. Review templates: cortex-brain/documents/evidence-templates/")
    print("   2. Validate YAML:    python -c 'import yaml; yaml.safe_load(open(\"cortex-brain/brain-protection-rules.yaml\"))'")
    print("   3. Run tests:        pytest tests/tier0/test_token_efficiency_enforcement.py")
    print("   4. Test Copilot:     Count exchanges before summarization")
    print()
    
    return 0


if __name__ == "__main__":
    exit(main())
