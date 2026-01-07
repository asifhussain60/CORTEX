# Feature: TDD Test Harness for Planning
**F004** | 🔥 HIGH | Phase 3

## Purpose
15-test suite validating all planning workflows with RED→GREEN→REFACTOR enforcement.

## Coverage
- Epic parent detection from user requests
- Folder structure validation (5-subfolder standard)
- Orphan plan detection and cleanup
- Regression prevention for plan flooding

## Status
13/15 passing, 2 fixes pending

## Location
`tests/test_planning_folder_structure.py`

## Dependencies
F001 (Planning), F003 (Toolkit)
