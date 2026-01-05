Apply TaskListOrchestrator to ADO Orchestrator v2

Context: TaskListOrchestrator validated via Planning v5.1 pilot 
(94.4% tests passing, 0.09ms recovery). ADO v2 is simpler than 
Planning (4 phases vs 5, fewer dependencies).

Task: Integrate TaskListOrchestrator into ADO v2
1. Create ado_orchestrator_v2_1.py extending ADO v2
2. Map 4 ADO phases to 4-6 tasks
3. Add strategic checkpoints (before API calls)
4. Test recovery from interruptions
5. Benchmark performance

ADO v2 Phases → Tasks:
- Phase 1: Feature analysis → task_analyze_feature
- Phase 2: Story generation → task_generate_stories (CHECKPOINT)
- Phase 3: Task breakdown → task_breakdown_tasks
- Phase 4: JSON export → task_export_json

Benefits:
- Sub-millisecond recovery from any phase
- Automatic resume after interruption
- Simpler than Planning (fewer dependencies)

Reference:
- src/orchestrators/ado/ado_orchestrator_v2.py (base)
- src/orchestrators/planning/planning_orchestrator_v5_1_pilot.py (pattern)
- src/orchestrators/task_list_orchestrator.py (core)

Target: 2-3 days, production-ready ADO v2.1