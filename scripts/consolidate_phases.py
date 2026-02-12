#!/usr/bin/env python3
"""Update index.yaml with consolidated phases."""

import yaml
from pathlib import Path
from datetime import datetime

def main():
    index_path = Path("cortex-registry/_cortex-master/index.yaml")
    
    # Load existing index
    with open(index_path) as f:
        data = yaml.safe_load(f)
    
    phases = data['active_phases']
    
    # Find phases to supersede
    supersede_map = {
        'phase-70': 'phase-76',
        'phase-48': 'phase-76',
        'phase-51-alt': 'phase-76',
        'phase-75': 'phase-77',
        'phase-65': 'phase-77',
        'phase-52': 'phase-78',
        'phase-66': 'phase-78',
    }
    
    # Update existing phases
    for phase in phases:
        phase_id = phase['id']
        if phase_id in supersede_map:
            new_id = supersede_map[phase_id]
            phase['status'] = 'superseded'
            phase['superseded_by'] = new_id
            phase['superseded_date'] = '2026-02-10'
            # Reduce priority since superseded
            if phase.get('priority') == 'P0':
                phase['priority'] = 'P1'
    
    # Add new consolidated phases
    new_phases = [
        {
            'id': 'phase-76',
            'name': 'Production Foundation Trilogy',
            'file': 'phases/active/phase-76-production-foundation-trilogy.yaml',
            'created': '2026-02-10',
            'status': 'next_activation',
            'priority': 'P0',
            'execution_order': 1,
            'roi_score': 0.97,
            'estimated_duration': '4-6 weeks',
            'test_target': 320,
            'coverage_target': 90,
            'tests_passing': 0,
            'stages_complete': '0/4',
            'critical_path': True,
            'production_blocker': True,
            'description': '🔴 NEXT ACTIVATION (P0 - CRITICAL): Consolidated production foundation (phase-70 + phase-48 + phase-51-alt). S1: Implementation ↔ Specification Alignment (2 weeks, 120 tests) — Delete 620 stub tests, implement 2 domain orchestrators, wiring.yaml 100% accuracy. S2: Registry Isolation & Multi-Tenant (1 week, 80 tests) — GitBackedRegistry with tenant isolation. S3: Secrets Management & Audit Hardening (1 week, 70 tests) — SecretsManager with encryption. S4: Integration & Validation (1 week, 50 tests) — Production deployment checklist. Strategic: 21+ weeks → 4-6 weeks through consolidation. Risk: 1.5/10 (LOW).',
            'depends_on': [],
            'blocks': ['phase-77', 'phase-78', 'Production deployment'],
        },
        {
            'id': 'phase-77',
            'name': 'Intelligence & Learning Core',
            'file': 'phases/active/phase-77-intelligence-learning-core.yaml',
            'created': '2026-02-10',
            'status': 'planned',
            'priority': 'P0',
            'execution_order': 2,
            'roi_score': 0.94,
            'estimated_duration': '2-3 weeks',
            'test_target': 240,
            'coverage_target': 90,
            'tests_passing': 12,
            'stages_complete': '1/4',
            'critical_path': True,
            'production_blocker': True,
            'description': '🟠 PLANNED (P0 - CRITICAL): Consolidated intelligence & learning (phase-75 + phase-65). S1: LENS Intelligence Remediation (1 week, 80 tests) — Complete 9/9 LENS stages, 155 tests passing. S2: Knowledge Persistence Service (1 week, 60 tests) — YAML generation for company/domains/. S3: Universal Learning Loop (1 week, 60 tests) — OBSERVE→ANALYZE→SYNTHESIZE→APPLY. S4: Integration & Enforcement (3 days, 40 tests) — 8th enforcement agent. Strategic: Self-improving CORTEX with cross-session learning. Risk: 1.8/10 (LOW).',
            'depends_on': ['phase-76'],
            'blocks': ['phase-78'],
        },
        {
            'id': 'phase-78',
            'name': 'Enterprise Orchestrator Maturity',
            'file': 'phases/active/phase-78-enterprise-orchestrator-maturity.yaml',
            'created': '2026-02-10',
            'status': 'planned',
            'priority': 'P1',
            'execution_order': 3,
            'roi_score': 0.89,
            'estimated_duration': '2-3 weeks',
            'test_target': 200,
            'coverage_target': 90,
            'tests_passing': 35,
            'stages_complete': '1/3',
            'critical_path': False,
            'production_blocker': False,
            'description': '🟡 PLANNED (P1 - STRATEGIC): Consolidated enterprise readiness (phase-52 + phase-66). S1: Enterprise Orchestrator Suite (1 week, 80 tests) — 165 tests passing, all orchestrators production-ready. S2: Knowledge Graph Lite & Domain Inference (1 week, 70 tests) — Pattern detection, cross-repository intelligence. S3: Integration & Documentation (1 week, 50 tests) — Orchestrator-graph integration. Strategic: Enterprise-scale orchestration with intelligent pattern detection. Risk: 2.0/10 (LOW).',
            'depends_on': ['phase-76', 'phase-77'],
            'blocks': [],
        },
    ]
    
    # Insert new phases at the beginning
    data['active_phases'] = new_phases + phases
    
    # Update metadata
    data['last_updated'] = datetime.now().isoformat() + 'Z'
    data['revision'] = 'Phase Consolidation 2026-02-10: 8 P0 phases → 3 mega-phases (phase-76, phase-77, phase-78) | Production readiness path: 12 weeks'
    
    # Write updated index
    with open(index_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("✅ Index.yaml updated successfully")
    print(f"   - 3 new consolidated phases added")
    print(f"   - 7 phases marked as superseded")
    print(f"   - Revision updated: {data['revision']}")

if __name__ == '__main__':
    main()
