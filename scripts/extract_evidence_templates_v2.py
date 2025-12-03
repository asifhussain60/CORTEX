#!/usr/bin/env python3
"""
CORTEX Evidence Template Extractor - Version 2.0 (YAML-Aware)

This script extracts verbose evidence_template and rationale blocks from
brain-protection-rules.yaml into separate .md files, replacing them with
file references to reduce token consumption.

Key improvements over v1:
- Uses PyYAML for proper parsing (no regex replacement)
- Preserves YAML structure and indentation
- Correctly extracts rule_id from YAML data structure
- Properly categorizes rules into subdirectories

Author: CORTEX Team
Version: 2.0.0
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class EvidenceTemplateExtractorV2:
    """
    Extract verbose templates from YAML using proper YAML parsing.
    """
    
    def __init__(self, 
                 yaml_path: str = "cortex-brain/brain-protection-rules.yaml",
                 templates_dir: str = "cortex-brain/documents/evidence-templates",
                 rationales_dir: str = "cortex-brain/documents/rationales"):
        self.yaml_path = Path(yaml_path)
        self.templates_dir = Path(templates_dir)
        self.rationales_dir = Path(rationales_dir)
        
        # Token estimation (4 chars per token)
        self.chars_per_token = 4
        
        # Extraction threshold (500 chars minimum)
        self.min_chars = 500
        
        # Category mapping for rules
        self.category_map = {
            'INCREMENTAL_PLAN_GENERATION': 'planning',
            'TDD_ENFORCEMENT': 'tdd',
            'RED_PHASE_VALIDATION': 'tdd',
            'GREEN_PHASE_VALIDATION': 'tdd',
            'GIT_CHECKPOINT_ENFORCEMENT': 'git',
            'PREVENT_DIRTY_STATE_WORK': 'git',
            'GIT_ISOLATION_ENFORCEMENT': 'git',
            'BRAIN_ARCHITECTURE_INTEGRITY': 'architecture',
            'DISTRIBUTED_DATABASE_ARCHITECTURE': 'architecture',
            'SECURITY_INJECTION': 'security',
            'SECURITY_AUTHENTICATION': 'security',
            'THREAT_MODELING_ENFORCEMENT': 'security',
        }
    
    def extract_all(self) -> Dict:
        """
        Main extraction workflow using PyYAML.
        
        Returns:
            Dict with extraction statistics
        """
        print("=" * 70)
        print("CORTEX Evidence Template Batch Extraction (v2.0)")
        print("=" * 70)
        print()
        
        # Create backup
        backup_path = f"{self.yaml_path}.before_batch_v2"
        print(f"📦 Creating backup: {backup_path}")
        with open(self.yaml_path, 'r') as f:
            original_content = f.read()
        with open(backup_path, 'w') as f:
            f.write(original_content)
        
        original_size = len(original_content)
        original_tokens = original_size // self.chars_per_token
        
        # Parse YAML
        print(f"📂 Parsing YAML: {self.yaml_path}")
        with open(self.yaml_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Extract templates
        print()
        print("🔍 Phase 1: Scanning for extraction candidates...")
        candidates = self._find_candidates(data)
        print(f"   Found {len(candidates)} candidates for extraction (>{self.min_chars} chars each)")
        
        if not candidates:
            print()
            print("✅ No templates to extract")
            return {'extracted': 0}
        
        print()
        print("📝 Phase 2: Extracting templates to files...")
        
        extracted_count = 0
        chars_saved = 0
        
        for i, candidate in enumerate(candidates, 1):
            rule_id = candidate['rule_id']
            field_type = candidate['field_type']  # 'evidence_template' or 'rationale'
            content = candidate['content']
            layer = candidate['layer']
            
            # Determine category and output directory
            category = self.category_map.get(rule_id, 'misc')
            if field_type == 'evidence_template':
                output_dir = self.templates_dir / category
            else:
                output_dir = self.rationales_dir
            
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create filename
            filename = f"{rule_id}.md"
            output_path = output_dir / filename
            
            # Write template file
            with open(output_path, 'w') as f:
                f.write(content)
            
            # Calculate tokens
            tokens = len(content) // self.chars_per_token
            chars_saved += len(content)
            
            # Create file reference
            if field_type == 'evidence_template':
                relative_path = f"documents/evidence-templates/{category}/{filename}"
            else:
                relative_path = f"documents/rationales/{filename}"
            
            file_ref = f"#file:{relative_path}"
            
            # Update YAML data structure
            rule = candidate['rule_obj']
            rule[field_type] = file_ref
            
            print(f"   ✅ {category}/{filename} ({len(content):,} chars, ~{tokens:,} tokens)")
            
            extracted_count += 1
            
            if extracted_count % 5 == 0:
                print(f"   Extracted {extracted_count}/{len(candidates)} templates...")
        
        print()
        print(f"✅ Extraction complete: {extracted_count} templates created")
        
        # Write modified YAML back
        print()
        print("💾 Writing updated YAML...")
        with open(self.yaml_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False, width=1000)
        
        # Calculate final size
        with open(self.yaml_path, 'r') as f:
            new_content = f.read()
        
        new_size = len(new_content)
        new_tokens = new_size // self.chars_per_token
        tokens_saved = original_tokens - new_tokens
        reduction_pct = (chars_saved / original_size) * 100
        
        print(f"💾 Size reduction: {original_size:,} → {new_size:,} chars ({chars_saved:,} saved)")
        print(f"💾 Token reduction: {original_tokens:,} → {new_tokens:,} tokens ({tokens_saved:,} saved)")
        print()
        print(f"✅ Updated {self.yaml_path}")
        print(f"📦 Backup saved: {backup_path}")
        
        print()
        print("=" * 70)
        print("📊 Extraction Summary")
        print("=" * 70)
        print(f"Templates created:   {extracted_count}")
        print(f"Original tokens:     {original_tokens:,}")
        print(f"New tokens:          {new_tokens:,}")
        print(f"Tokens saved:        {tokens_saved:,}")
        print(f"Reduction:           {reduction_pct:.1f}%")
        print()
        print("✅ Batch extraction complete!")
        
        return {
            'extracted': extracted_count,
            'original_tokens': original_tokens,
            'new_tokens': new_tokens,
            'tokens_saved': tokens_saved,
            'reduction_pct': reduction_pct
        }
    
    def _find_candidates(self, data: Dict) -> List[Dict]:
        """
        Find evidence_template and rationale blocks that should be extracted.
        
        Args:
            data: Parsed YAML data structure
            
        Returns:
            List of candidate dictionaries with extraction info
        """
        candidates = []
        
        # Navigate to protection_layers
        layers = data.get('protection_layers', [])
        
        for layer in layers:
            layer_id = layer.get('layer_id', 'unknown')
            rules = layer.get('rules', [])
            
            for rule in rules:
                rule_id = rule.get('rule_id', 'UNKNOWN')
                
                # Check evidence_template
                evidence = rule.get('evidence_template', '')
                if isinstance(evidence, str) and len(evidence) > self.min_chars:
                    candidates.append({
                        'rule_id': rule_id,
                        'layer': layer_id,
                        'field_type': 'evidence_template',
                        'content': evidence,
                        'rule_obj': rule
                    })
                
                # Check rationale
                rationale = rule.get('rationale', '')
                if isinstance(rationale, str) and len(rationale) > self.min_chars:
                    candidates.append({
                        'rule_id': rule_id,
                        'layer': layer_id,
                        'field_type': 'rationale',
                        'content': rationale,
                        'rule_obj': rule
                    })
        
        return candidates


def main():
    """Main entry point."""
    extractor = EvidenceTemplateExtractorV2()
    stats = extractor.extract_all()
    
    # Exit with error if no extractions (for testing)
    if stats.get('extracted', 0) == 0:
        exit(1)


if __name__ == '__main__':
    main()
