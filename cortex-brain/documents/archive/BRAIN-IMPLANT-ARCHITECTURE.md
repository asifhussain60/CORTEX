# CORTEX Brain Implant Architecture
**Feature:** Export/Import Brain for Knowledge Sharing  
**Version:** 1.0 (Tier 1 - Git Isolation Strategy)  
**Date:** 2025-11-17  
**Author:** Asif Hussain  
**Status:** Architecture Design

---

## 🎯 Overview

**Problem:** CORTEX instances on different machines (or branches) accumulate different learned knowledge. When pulling code updates, git has no understanding of how to merge pattern confidence, namespace boundaries, or contradictory learnings.

**Solution:** "Brain Implant" entry points that allow explicit, controlled knowledge transfer between CORTEX instances using human-readable YAML format.

**Core Principle:** Never lose learned knowledge during git operations.

---

## 📋 Architecture Decision

**Chosen Tier:** **Tier 1 (Git Isolation)**  
**Rationale:**
- ✅ Zero merge conflicts (databases excluded from git)
- ✅ Manual control over knowledge sharing
- ✅ Human review of imported patterns
- ✅ No automatic merge errors
- ✅ Already 80% implemented (databases in .gitignore)

**Alternative Tiers Considered:**
- **Tier 2 (Auto-Merge Hook):** 6 hours dev, risk of incorrect merges
- **Tier 3 (Explicit Sync Command):** 6 hours dev, manual review overhead

---

## 🧠 Brain Implant Components

### Component 1: Export Brain (`export brain`)

**Purpose:** Export learned patterns from local knowledge graph to shareable YAML file

**Format:** Human-readable YAML (same as existing knowledge-graph.yaml)

**What Gets Exported:**
1. **Patterns** (Tier 2):
   - Intent patterns (learned user phrases → detected intent)
   - Validation insights (bugs caught, lessons learned)
   - Workflow templates (proven multi-step processes)
   - File relationships (files that change together)
   - Architectural patterns (design decisions)

2. **Metadata:**
   - Pattern confidence scores (0.0-1.0)
   - Access counts (usage frequency)
   - Last accessed timestamps
   - Namespace boundaries (cortex.* vs workspace.*)
   - Pattern source (machine ID, timestamp)

3. **Exclusions (NOT exported):**
   - Conversation history (Tier 1) - stays private
   - Machine-specific context (Tier 3) - git stats, file paths
   - Decayed patterns (confidence < 0.3)
   - Pinned generic patterns (already in CORTEX core)

**Export Process:**

```yaml
# Command
export brain [--scope=workspace|cortex|all] [--min-confidence=0.5] [--output=path]

# Examples
export brain                              # Export all workspace patterns
export brain --scope=all                  # Export workspace + cortex patterns
export brain --min-confidence=0.7         # Only high-confidence patterns
export brain --output=brain-export.yaml   # Custom output path

# Default output location
cortex-brain/exports/brain-export-{timestamp}.yaml
```

**Export Format (YAML Structure):**

```yaml
# CORTEX Brain Export
# Generated: 2025-11-17T10:30:00Z
# Source Machine: DESKTOP-PRIMARY-12345
# CORTEX Version: 3.0.1

version: "1.0"
export_date: "2025-11-17T10:30:00Z"
source_machine_id: "DESKTOP-PRIMARY-12345"
cortex_version: "3.0.1"
total_patterns: 54
scope: "workspace"  # or "cortex" or "all"

# Export Statistics
statistics:
  patterns_exported: 54
  confidence_range: [0.50, 0.95]
  namespaces: ["workspace.ksessions", "workspace.authentication"]
  pattern_types: ["validation_insight", "workflow", "intent", "file_relationship"]
  oldest_pattern: "2025-10-15T09:30:00Z"
  newest_pattern: "2025-11-17T10:25:00Z"

# Exported Patterns
patterns:
  
  # Pattern 1: Validation Insight
  filesystem_validation_required:
    pattern_type: "validation_insight"
    confidence: 0.95
    access_count: 12
    last_accessed: "2025-11-17T09:00:00Z"
    created_at: "2025-11-17T08:00:00Z"
    namespaces: ["workspace.ksessions", "cortex.core"]
    source: "DESKTOP-PRIMARY-12345"
    
    # Pattern Content
    issue: "File generation operations report success without verifying actual filesystem changes"
    root_cause: "Missing post-write validation - code execution ≠ file creation success"
    symptom: "Operations return success status, but target folders remain empty"
    solution: "Multi-layer validation after every file write: exists() + size > 0 + count matches expected"
    
    # Evidence
    test_evidence: |
      pytest test_folders_not_empty: FAILED
      Error: "Empty folders found: diagrams, generated"
    
    code_pattern: |
      # Correct pattern
      with open(file, 'w') as f:
          f.write(content)
      
      if not file.exists():
          raise ValueError(f"File not created: {file}")
      if file.stat().st_size == 0:
          raise ValueError(f"Empty file: {file}")
    
    applies_to: ["document_generators", "diagram_generators", "export_operations"]
    
    # Metadata
    metadata:
      impact: "critical"
      reusability: 100
      strategic_value: "extremely_high"
      conversation_reference: "CONVERSATION-CAPTURE-2025-11-17.md"
  
  # Pattern 2: Workflow Template
  authentication_implementation_workflow:
    pattern_type: "workflow"
    confidence: 0.88
    access_count: 8
    last_accessed: "2025-11-16T14:30:00Z"
    created_at: "2025-11-10T10:00:00Z"
    namespaces: ["workspace.ksessions"]
    source: "DESKTOP-PRIMARY-12345"
    
    # Workflow Content
    name: "Authentication Feature Implementation"
    phases:
      - phase: 1
        name: "Planning & Design"
        tasks: ["Define requirements", "Create test scenarios", "Design API contracts"]
        duration_estimate: "2 hours"
      
      - phase: 2
        name: "TDD Implementation"
        tasks: ["Write failing tests (RED)", "Implement feature (GREEN)", "Refactor code"]
        duration_estimate: "4 hours"
      
      - phase: 3
        name: "Integration & Validation"
        tasks: ["Run full test suite", "Verify DoD", "Deploy to staging"]
        duration_estimate: "1 hour"
    
    success_rate: 0.94
    avg_duration_hours: 7.0
    
    # Metadata
    metadata:
      feature_type: "authentication"
      complexity: "medium"
      team_size: 1
  
  # Pattern 3: Intent Pattern
  plan_authentication_intent:
    pattern_type: "intent"
    confidence: 0.82
    access_count: 15
    last_accessed: "2025-11-17T10:00:00Z"
    created_at: "2025-11-05T09:00:00Z"
    namespaces: ["cortex.core"]
    source: "DESKTOP-PRIMARY-12345"
    
    # Intent Content
    detected_intent: "PLAN"
    user_phrases:
      - "plan authentication"
      - "create a plan for login"
      - "help me plan user auth"
      - "design authentication system"
    
    keywords: ["plan", "authentication", "auth", "login", "design"]
    routed_to: "work-planner"
    success_rate: 0.92
    
    # Metadata
    metadata:
      intent_category: "planning"
      agent: "work-planner"
  
  # Pattern 4: File Relationship
  auth_service_files:
    pattern_type: "file_relationship"
    confidence: 0.75
    access_count: 6
    last_accessed: "2025-11-15T16:00:00Z"
    created_at: "2025-11-10T10:30:00Z"
    namespaces: ["workspace.ksessions"]
    source: "DESKTOP-PRIMARY-12345"
    
    # Relationship Content
    file_a: "Services/AuthService.cs"
    file_b: "Controllers/AuthController.cs"
    relationship_type: "co_modification"
    strength: 0.85  # 85% of the time they change together
    co_modification_count: 17
    
    context: "Authentication feature implementation - service + API endpoint"
    
    # Metadata
    metadata:
      pattern: "service + controller"
      layer_a: "business_logic"
      layer_b: "api"

# Export Signature (for verification)
signature:
  sha256: "abc123...def456"  # SHA256 hash of patterns content
  generator: "CORTEX Brain Exporter v1.0"
  schema_version: "1.0"
```

**Export Implementation (Python):**

```python
# src/tier2/brain_implant.py

class BrainExporter:
    """Export CORTEX knowledge graph to shareable YAML format"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
    
    def export_brain(
        self,
        scope: str = "workspace",
        min_confidence: float = 0.5,
        output_path: Optional[Path] = None
    ) -> Path:
        """
        Export learned patterns to YAML file.
        
        Args:
            scope: "workspace" (default), "cortex", or "all"
            min_confidence: Minimum confidence threshold (default: 0.5)
            output_path: Custom output path (default: auto-generated)
        
        Returns:
            Path to exported YAML file
        """
        # Generate output path if not provided
        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = Path("cortex-brain/exports") / f"brain-export-{timestamp}.yaml"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Query patterns from database
        patterns = self._query_patterns(scope, min_confidence)
        
        # Build export structure
        export_data = {
            "version": "1.0",
            "export_date": datetime.now().isoformat(),
            "source_machine_id": self._get_machine_id(),
            "cortex_version": self._get_cortex_version(),
            "total_patterns": len(patterns),
            "scope": scope,
            "statistics": self._calculate_statistics(patterns),
            "patterns": self._format_patterns(patterns),
            "signature": self._generate_signature(patterns)
        }
        
        # Write YAML file
        with open(output_path, 'w') as f:
            yaml.safe_dump(export_data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"✅ Exported {len(patterns)} patterns to {output_path}")
        
        return output_path
    
    def _query_patterns(self, scope: str, min_confidence: float) -> List[Dict]:
        """Query patterns from knowledge graph database"""
        conn = sqlite3.connect(self.kg.db_path)
        cursor = conn.cursor()
        
        # Build query based on scope
        if scope == "workspace":
            namespace_filter = "AND (namespaces LIKE '%workspace%' OR namespaces IS NULL)"
        elif scope == "cortex":
            namespace_filter = "AND namespaces LIKE '%cortex%'"
        elif scope == "all":
            namespace_filter = ""
        else:
            raise ValueError(f"Invalid scope: {scope}")
        
        query = f"""
            SELECT pattern_id, title, pattern_type, confidence, 
                   created_at, last_accessed, access_count,
                   content, metadata, namespaces, source
            FROM patterns
            WHERE confidence >= ?
              {namespace_filter}
            ORDER BY confidence DESC, access_count DESC
        """
        
        cursor.execute(query, (min_confidence,))
        patterns = []
        
        for row in cursor.fetchall():
            patterns.append({
                "pattern_id": row[0],
                "title": row[1],
                "pattern_type": row[2],
                "confidence": row[3],
                "created_at": row[4],
                "last_accessed": row[5],
                "access_count": row[6],
                "content": json.loads(row[7]) if row[7] else {},
                "metadata": json.loads(row[8]) if row[8] else {},
                "namespaces": json.loads(row[9]) if row[9] else [],
                "source": row[10]
            })
        
        conn.close()
        return patterns
    
    def _calculate_statistics(self, patterns: List[Dict]) -> Dict:
        """Calculate export statistics"""
        if not patterns:
            return {}
        
        all_namespaces = set()
        pattern_types = set()
        
        for p in patterns:
            all_namespaces.update(p.get("namespaces", []))
            pattern_types.add(p.get("pattern_type"))
        
        return {
            "patterns_exported": len(patterns),
            "confidence_range": [
                min(p["confidence"] for p in patterns),
                max(p["confidence"] for p in patterns)
            ],
            "namespaces": sorted(list(all_namespaces)),
            "pattern_types": sorted(list(pattern_types)),
            "oldest_pattern": min(p["created_at"] for p in patterns),
            "newest_pattern": max(p["created_at"] for p in patterns)
        }
    
    def _format_patterns(self, patterns: List[Dict]) -> Dict:
        """Format patterns for YAML export"""
        formatted = {}
        
        for p in patterns:
            pattern_id = p["pattern_id"]
            
            # Build pattern structure
            formatted[pattern_id] = {
                "pattern_type": p["pattern_type"],
                "confidence": p["confidence"],
                "access_count": p["access_count"],
                "last_accessed": p["last_accessed"],
                "created_at": p["created_at"],
                "namespaces": p["namespaces"],
                "source": p["source"],
                **p["content"],  # Pattern-specific content
                "metadata": p["metadata"]
            }
        
        return formatted
    
    def _generate_signature(self, patterns: List[Dict]) -> Dict:
        """Generate SHA256 signature for verification"""
        import hashlib
        
        # Serialize patterns for hashing
        patterns_json = json.dumps(patterns, sort_keys=True)
        sha256_hash = hashlib.sha256(patterns_json.encode()).hexdigest()
        
        return {
            "sha256": sha256_hash,
            "generator": "CORTEX Brain Exporter v1.0",
            "schema_version": "1.0"
        }
    
    def _get_machine_id(self) -> str:
        """Get unique machine identifier"""
        import socket
        import uuid
        
        hostname = socket.gethostname()
        mac_address = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                                for elements in range(0,8*6,8)][::-1])
        return f"{hostname}-{mac_address[:8]}"
    
    def _get_cortex_version(self) -> str:
        """Get CORTEX version from config"""
        # TODO: Load from cortex.config.json
        return "3.0.1"
```

---

### Component 2: Import Brain (`import brain`)

**Purpose:** Import patterns from exported YAML into local knowledge graph with conflict detection

**Safety Features:**
1. **Signature Verification:** Validate SHA256 hash before import
2. **Conflict Detection:** Identify existing patterns with same ID
3. **Merge Strategy:** Apply weighted confidence merging (reuse existing algorithm)
4. **Namespace Validation:** Prevent mixing cortex.* and workspace.* patterns
5. **Human Review:** Generate conflict report before applying changes

**Import Process:**

```yaml
# Command
import brain <file> [--strategy=merge|replace|skip] [--dry-run] [--review]

# Examples
import brain brain-export-20251117.yaml             # Import with merge strategy
import brain brain-export.yaml --strategy=replace   # Replace existing patterns
import brain brain-export.yaml --dry-run            # Preview conflicts without changes
import brain brain-export.yaml --review             # Show conflict report, ask approval

# Import Strategies
# - merge: Combine with existing patterns (weighted confidence, namespace union)
# - replace: Overwrite existing patterns completely
# - skip: Keep existing patterns, ignore imports with same ID
```

**Conflict Detection Rules:**

| Scenario | Detection | Merge Strategy | Example |
|----------|-----------|----------------|---------|
| **Identical Patterns** | Same pattern_id, confidence within 5% | Keep higher confidence | Local: 0.85, Import: 0.88 → Keep import (0.88) |
| **Similar Patterns** | Same pattern_id, confidence differs >5% | Weighted merge | Local: 0.85 (10x), Import: 0.75 (5x) → Merged: 0.82 |
| **Contradictory Patterns** | Same feature, opposite conclusions | Flag for review | Local: "use JWT", Import: "use OAuth2" → CONFLICT |
| **Namespace Violation** | Import tries to add cortex.* pattern | Block import | Import: cortex.core pattern → BLOCKED (protected) |
| **New Patterns** | pattern_id not in local graph | Add directly | Import: new_pattern → ADDED |

**Import Implementation (Python):**

```python
# src/tier2/brain_implant.py

class BrainImporter:
    """Import patterns from YAML brain export with conflict detection"""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        self.kg = knowledge_graph
    
    def import_brain(
        self,
        import_file: Path,
        strategy: str = "merge",
        dry_run: bool = False,
        review: bool = True
    ) -> Dict[str, Any]:
        """
        Import patterns from exported YAML file.
        
        Args:
            import_file: Path to exported brain YAML
            strategy: "merge" (default), "replace", or "skip"
            dry_run: Preview conflicts without making changes
            review: Generate conflict report and ask for approval
        
        Returns:
            Import results with statistics and conflicts
        """
        # Load and validate import file
        import_data = self._load_and_validate(import_file)
        
        if not import_data:
            raise ValueError("Invalid import file or signature verification failed")
        
        # Detect conflicts
        conflicts = self._detect_conflicts(import_data["patterns"])
        
        # Generate conflict report
        report = self._generate_conflict_report(conflicts, strategy)
        
        if review:
            # Show report and ask for approval
            self._display_conflict_report(report)
            
            if not dry_run:
                approved = input("\n⚠️  Apply these changes? (yes/no): ").strip().lower()
                if approved != "yes":
                    logger.info("Import cancelled by user")
                    return {"status": "cancelled", "report": report}
        
        if dry_run:
            logger.info("DRY RUN: No changes applied")
            return {"status": "dry_run", "report": report}
        
        # Apply import based on strategy
        results = self._apply_import(import_data["patterns"], strategy, conflicts)
        
        return {
            "status": "success",
            "report": report,
            "results": results
        }
    
    def _load_and_validate(self, import_file: Path) -> Optional[Dict]:
        """Load YAML file and verify signature"""
        with open(import_file) as f:
            data = yaml.safe_load(f)
        
        # Verify signature
        patterns = data.get("patterns", {})
        expected_signature = data.get("signature", {}).get("sha256")
        
        # Recalculate signature
        patterns_json = json.dumps(patterns, sort_keys=True)
        actual_signature = hashlib.sha256(patterns_json.encode()).hexdigest()
        
        if expected_signature != actual_signature:
            logger.error(f"❌ Signature verification failed")
            logger.error(f"   Expected: {expected_signature}")
            logger.error(f"   Actual: {actual_signature}")
            return None
        
        logger.info(f"✅ Signature verified")
        return data
    
    def _detect_conflicts(self, import_patterns: Dict) -> Dict[str, List]:
        """Detect conflicts between import and existing patterns"""
        conflicts = {
            "identical": [],      # Same pattern_id, confidence within 5%
            "similar": [],        # Same pattern_id, confidence differs >5%
            "contradictory": [],  # Same feature, opposite conclusions
            "namespace_violations": [],  # Tries to add protected namespace
            "new_patterns": []    # pattern_id not in local graph
        }
        
        for pattern_id, import_pattern in import_patterns.items():
            # Check if pattern exists locally
            local_pattern = self.kg.retrieve_pattern(pattern_id)
            
            if not local_pattern:
                # New pattern
                conflicts["new_patterns"].append({
                    "pattern_id": pattern_id,
                    "import_confidence": import_pattern["confidence"],
                    "import_namespaces": import_pattern.get("namespaces", [])
                })
                continue
            
            # Check for namespace violations
            import_namespaces = import_pattern.get("namespaces", [])
            if any(ns.startswith("cortex.") for ns in import_namespaces):
                conflicts["namespace_violations"].append({
                    "pattern_id": pattern_id,
                    "import_namespaces": import_namespaces,
                    "reason": "Protected cortex.* namespace"
                })
                continue
            
            # Compare confidence
            confidence_diff = abs(import_pattern["confidence"] - local_pattern.confidence)
            
            if confidence_diff <= 0.05:
                # Identical (within 5%)
                conflicts["identical"].append({
                    "pattern_id": pattern_id,
                    "local_confidence": local_pattern.confidence,
                    "import_confidence": import_pattern["confidence"],
                    "difference": confidence_diff
                })
            else:
                # Similar (differs >5%)
                conflicts["similar"].append({
                    "pattern_id": pattern_id,
                    "local_confidence": local_pattern.confidence,
                    "local_access_count": local_pattern.access_count,
                    "import_confidence": import_pattern["confidence"],
                    "import_access_count": import_pattern.get("access_count", 0),
                    "difference": confidence_diff
                })
        
        return conflicts
    
    def _generate_conflict_report(self, conflicts: Dict, strategy: str) -> Dict:
        """Generate human-readable conflict report"""
        report = {
            "total_patterns": sum(len(v) for v in conflicts.values()),
            "new_patterns": len(conflicts["new_patterns"]),
            "identical_patterns": len(conflicts["identical"]),
            "similar_patterns": len(conflicts["similar"]),
            "contradictory_patterns": len(conflicts["contradictory"]),
            "namespace_violations": len(conflicts["namespace_violations"]),
            "strategy": strategy,
            "actions": []
        }
        
        # Determine actions based on strategy
        for pattern_id in conflicts["new_patterns"]:
            report["actions"].append({
                "pattern_id": pattern_id["pattern_id"],
                "action": "ADD",
                "confidence": pattern_id["import_confidence"]
            })
        
        for pattern in conflicts["identical"]:
            if strategy == "merge":
                action = "KEEP_HIGHER" if pattern["import_confidence"] > pattern["local_confidence"] else "KEEP_LOCAL"
            elif strategy == "replace":
                action = "REPLACE"
            else:  # skip
                action = "SKIP"
            
            report["actions"].append({
                "pattern_id": pattern["pattern_id"],
                "action": action,
                "local": pattern["local_confidence"],
                "import": pattern["import_confidence"]
            })
        
        for pattern in conflicts["similar"]:
            if strategy == "merge":
                # Calculate weighted merge confidence
                total_count = pattern["local_access_count"] + pattern["import_access_count"]
                if total_count > 0:
                    merged_confidence = (
                        pattern["local_confidence"] * pattern["local_access_count"] +
                        pattern["import_confidence"] * pattern["import_access_count"]
                    ) / total_count
                else:
                    merged_confidence = max(pattern["local_confidence"], pattern["import_confidence"])
                
                report["actions"].append({
                    "pattern_id": pattern["pattern_id"],
                    "action": "MERGE",
                    "local": pattern["local_confidence"],
                    "import": pattern["import_confidence"],
                    "merged": merged_confidence
                })
            elif strategy == "replace":
                report["actions"].append({
                    "pattern_id": pattern["pattern_id"],
                    "action": "REPLACE",
                    "local": pattern["local_confidence"],
                    "import": pattern["import_confidence"]
                })
            else:  # skip
                report["actions"].append({
                    "pattern_id": pattern["pattern_id"],
                    "action": "SKIP",
                    "local": pattern["local_confidence"]
                })
        
        for pattern in conflicts["namespace_violations"]:
            report["actions"].append({
                "pattern_id": pattern["pattern_id"],
                "action": "BLOCKED",
                "reason": pattern["reason"],
                "namespaces": pattern["import_namespaces"]
            })
        
        return report
    
    def _display_conflict_report(self, report: Dict):
        """Display conflict report to user"""
        print("\n" + "="*60)
        print("🧠 CORTEX Brain Import Conflict Report")
        print("="*60 + "\n")
        
        print(f"📊 Summary:")
        print(f"   Total patterns: {report['total_patterns']}")
        print(f"   New patterns: {report['new_patterns']}")
        print(f"   Identical patterns: {report['identical_patterns']}")
        print(f"   Similar patterns: {report['similar_patterns']}")
        print(f"   Namespace violations: {report['namespace_violations']}")
        print(f"   Strategy: {report['strategy'].upper()}\n")
        
        print(f"📋 Planned Actions:\n")
        
        for action in report["actions"]:
            pattern_id = action["pattern_id"]
            action_type = action["action"]
            
            if action_type == "ADD":
                print(f"   ✅ ADD: {pattern_id} (confidence: {action['confidence']:.2f})")
            
            elif action_type == "KEEP_HIGHER":
                print(f"   ⚖️  KEEP_HIGHER: {pattern_id} (import: {action['import']:.2f} > local: {action['local']:.2f})")
            
            elif action_type == "KEEP_LOCAL":
                print(f"   ⚖️  KEEP_LOCAL: {pattern_id} (local: {action['local']:.2f} ≥ import: {action['import']:.2f})")
            
            elif action_type == "MERGE":
                print(f"   🔀 MERGE: {pattern_id}")
                print(f"      Local: {action['local']:.2f} + Import: {action['import']:.2f} → Merged: {action['merged']:.2f}")
            
            elif action_type == "REPLACE":
                print(f"   ♻️  REPLACE: {pattern_id} (local: {action['local']:.2f} → import: {action['import']:.2f})")
            
            elif action_type == "SKIP":
                print(f"   ⏭️  SKIP: {pattern_id} (keeping local: {action['local']:.2f})")
            
            elif action_type == "BLOCKED":
                print(f"   🚫 BLOCKED: {pattern_id}")
                print(f"      Reason: {action['reason']}")
                print(f"      Namespaces: {', '.join(action['namespaces'])}")
        
        print("\n" + "="*60)
    
    def _apply_import(self, import_patterns: Dict, strategy: str, conflicts: Dict) -> Dict:
        """Apply import changes to knowledge graph"""
        results = {
            "added": 0,
            "merged": 0,
            "replaced": 0,
            "skipped": 0,
            "blocked": 0
        }
        
        # Block namespace violations first
        blocked_patterns = {p["pattern_id"] for p in conflicts["namespace_violations"]}
        
        for pattern_id, import_pattern in import_patterns.items():
            if pattern_id in blocked_patterns:
                results["blocked"] += 1
                continue
            
            # Check if pattern exists locally
            local_pattern = self.kg.retrieve_pattern(pattern_id)
            
            if not local_pattern:
                # Add new pattern
                self.kg.store_pattern(self._convert_to_pattern(import_pattern))
                results["added"] += 1
                continue
            
            # Conflict resolution based on strategy
            if strategy == "merge":
                # Use existing merge algorithm from pattern_cleanup.py
                self._merge_pattern(local_pattern, import_pattern)
                results["merged"] += 1
            
            elif strategy == "replace":
                # Replace local pattern with import
                self.kg.delete_pattern(pattern_id)
                self.kg.store_pattern(self._convert_to_pattern(import_pattern))
                results["replaced"] += 1
            
            elif strategy == "skip":
                # Keep local, ignore import
                results["skipped"] += 1
        
        logger.info(f"✅ Import complete:")
        logger.info(f"   Added: {results['added']}")
        logger.info(f"   Merged: {results['merged']}")
        logger.info(f"   Replaced: {results['replaced']}")
        logger.info(f"   Skipped: {results['skipped']}")
        logger.info(f"   Blocked: {results['blocked']}")
        
        return results
    
    def _merge_pattern(self, local_pattern, import_pattern):
        """Merge import pattern with local pattern (reuse existing algorithm)"""
        # Calculate weighted confidence
        local_count = local_pattern.access_count
        import_count = import_pattern.get("access_count", 0)
        total_count = local_count + import_count
        
        if total_count > 0:
            merged_confidence = (
                local_pattern.confidence * local_count +
                import_pattern["confidence"] * import_count
            ) / total_count
        else:
            merged_confidence = max(local_pattern.confidence, import_pattern["confidence"])
        
        # Merge namespaces (union)
        local_namespaces = set(local_pattern.namespaces or [])
        import_namespaces = set(import_pattern.get("namespaces", []))
        merged_namespaces = list(local_namespaces | import_namespaces)
        
        # Update local pattern
        local_pattern.confidence = merged_confidence
        local_pattern.namespaces = merged_namespaces
        local_pattern.access_count = total_count
        local_pattern.last_accessed = max(
            local_pattern.last_accessed,
            import_pattern.get("last_accessed", local_pattern.last_accessed)
        )
        
        # Save merged pattern
        self.kg.update_pattern(local_pattern)
    
    def _convert_to_pattern(self, import_pattern: Dict):
        """Convert import YAML structure to Pattern object"""
        # TODO: Convert to proper Pattern object
        # This is a placeholder - actual implementation depends on Pattern class structure
        pass
```

---

## 🔒 Safety & Validation

### Brain Protection Integration (Rule #22)

**Brain Protector must validate all import operations:**

```python
# Before import
brain_protector.validate_change(
    intent="Import brain patterns from external source",
    description=f"Importing {len(patterns)} patterns from {import_file}",
    affected_files=["cortex-brain/tier2/knowledge-graph.db"],
    scope="cortex" if any("cortex." in ns for p in patterns for ns in p["namespaces"]) else "application"
)

# Protection Checks:
# ✅ Namespace isolation enforced (no cortex.* imports without approval)
# ✅ Signature verification required
# ✅ Conflict report generated
# ✅ Human review required (--review flag)
```

### Import Validation Layers

| Layer | Check | Action if Failed |
|-------|-------|------------------|
| **Layer 1: File Exists** | import_file.exists() | Abort: "Import file not found" |
| **Layer 2: Valid YAML** | yaml.safe_load() succeeds | Abort: "Invalid YAML format" |
| **Layer 3: Schema Validation** | Required fields present | Abort: "Missing required fields" |
| **Layer 4: Signature Verification** | SHA256 hash matches | Abort: "Signature verification failed" |
| **Layer 5: Namespace Protection** | No cortex.* imports | Block: "Namespace violation detected" |
| **Layer 6: Conflict Detection** | Generate conflict report | Continue: "Review conflicts before import" |
| **Layer 7: Human Review** | User approval required | Abort: "Import cancelled by user" |

---

## 📂 File Structure

```
cortex-brain/
├── tier2/
│   └── knowledge-graph.db          # Local knowledge graph (SQLite)
│
├── exports/                         # Exported brain files (NEW)
│   ├── brain-export-20251117_103000.yaml
│   ├── brain-export-20251116_150000.yaml
│   └── README.md                    # Export format documentation
│
├── imports/                         # Import staging area (NEW)
│   ├── pending/                     # Awaiting review
│   │   └── brain-import-from-laptop.yaml
│   ├── applied/                     # Successfully imported
│   │   └── brain-import-20251117.yaml
│   └── rejected/                    # Blocked by validation
│       └── brain-import-invalid.yaml
│
└── knowledge-graph.yaml             # Human-readable reference (existing)
```

---

## 🎯 Usage Examples

### Scenario 1: Share Knowledge Between Desktop & Laptop

**Desktop (primary development machine):**
```bash
# Export workspace patterns
cortex export brain --scope=workspace --min-confidence=0.7

# Output: cortex-brain/exports/brain-export-20251117_103000.yaml
```

**Git commit (if sharing via git):**
```bash
git add cortex-brain/exports/brain-export-20251117_103000.yaml
git commit -m "chore: Export learned patterns for knowledge sharing"
git push origin feature/authentication
```

**Laptop (secondary machine):**
```bash
# Pull code updates
git pull origin feature/authentication

# Import brain patterns
cortex import brain cortex-brain/exports/brain-export-20251117_103000.yaml --review

# Review conflict report
# Approve import
```

---

### Scenario 2: Team Knowledge Sharing

**Developer A (learns authentication patterns):**
```bash
# Export high-confidence patterns only
cortex export brain --scope=workspace --min-confidence=0.8 --output=auth-patterns.yaml
```

**Developer B (imports team knowledge):**
```bash
# Import with merge strategy (combine with existing)
cortex import brain auth-patterns.yaml --strategy=merge --review

# Conflict Report:
# ✅ 12 new patterns added
# 🔀 3 patterns merged (weighted confidence)
# ⏭️  2 patterns skipped (local higher confidence)
```

---

### Scenario 3: Dry-Run Preview

```bash
# Preview import without making changes
cortex import brain brain-export.yaml --dry-run

# Output:
# 📊 Summary:
#    Total patterns: 54
#    New patterns: 42
#    Similar patterns: 12
#    Namespace violations: 0
#
# DRY RUN: No changes applied
```

---

## 🚀 Implementation Roadmap

### Phase 1: Export Brain (2 hours)
- [ ] Create `BrainExporter` class
- [ ] Implement `export_brain()` method
- [ ] Query patterns from SQLite
- [ ] Format to YAML structure
- [ ] Generate SHA256 signature
- [ ] Write export file
- [ ] Add export command to CLI

### Phase 2: Import Brain (3 hours)
- [ ] Create `BrainImporter` class
- [ ] Implement signature verification
- [ ] Implement conflict detection
- [ ] Generate conflict report
- [ ] Implement merge strategies (merge/replace/skip)
- [ ] Apply import with transaction safety
- [ ] Add import command to CLI

### Phase 3: Integration & Testing (1 hour)
- [ ] Integrate with Brain Protector (Rule #22)
- [ ] Add namespace protection validation
- [ ] Create import/export directories
- [ ] Write integration tests
- [ ] Test multi-machine workflow
- [ ] Document usage examples

### Phase 4: Documentation (30 min)
- [ ] Update user documentation
- [ ] Add export/import examples
- [ ] Document conflict resolution strategies
- [ ] Create troubleshooting guide

**Total Estimated Time:** 6.5 hours

---

## 🔮 Future Enhancements (CORTEX 4.0)

These are **NOT** part of current implementation (Tier 1), but documented for future reference:

### Cloud-Based Brain Sync
- Store brain in cloud database (AWS RDS, Azure SQL)
- Real-time sync between machines
- Conflict resolution at database level
- Git merge becomes irrelevant

### Federated Learning
- Aggregate gradients instead of raw patterns
- Privacy-preserving knowledge sharing
- No raw pattern transfer (only learned weights)
- Suitable for teams with privacy constraints

### Event-Sourced Brain
- Store pattern changes as event stream
- Replay events to rebuild state
- Easier conflict resolution (merge events, not state)
- Complete audit trail of all learning

**Decision:** Defer these until CORTEX 4.0 architecture is defined based on actual team collaboration needs.

---

## 📚 References

**Design Documents:**
- Conversation: CORTEX git merge strategy discussion (2025-11-17)
- Existing merge algorithm: `src/tier2/pattern_cleanup.py` lines 482-530
- CORTEX brain structure: `cortex-brain/knowledge-graph.yaml`

**Related Components:**
- Knowledge Graph: `src/tier2/knowledge_graph.py`
- Pattern Cleanup: `src/tier2/pattern_cleanup.py`
- Brain Protector: `src/tier0/brain_protector.py`

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Status:** Architecture Design - Ready for Implementation  
**Version:** 1.0 (Tier 1 - Git Isolation Strategy)
