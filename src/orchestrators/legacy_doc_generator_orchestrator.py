"""
Legacy API Documentation Generator Orchestrator

Reverse-engineers legacy C# code into PM/BA-readable specifications using:
- CORTEX Lens (C# AST analysis)
- Planning System 3.1 (tiered routing)
- Clean Architecture mapping
- Mermaid diagram generation

Phase 10 of CORTEX Evolution v3.9

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass

from src.operations.base_operation_module import (
    BaseOperationModule, OperationResult, OperationStatus
)
from src.intelligence.analyzers.csharp_analyzer import CSharpAnalyzer
from src.operations.modules.analysis.ast_engine import ASTEngine

logger = logging.getLogger(__name__)


@dataclass
class BusinessRule:
    """Extracted business rule."""
    name: str
    description: str
    condition: str
    action: str
    line_start: int
    line_end: int
    layer: str  # Domain/UseCase/Infrastructure


@dataclass
class DataOperation:
    """Database or service operation."""
    operation_type: str  # SELECT/INSERT/UPDATE/DELETE/SERVICE_CALL
    target: str  # Table name or service name
    purpose: str
    line_number: int


@dataclass
class ValidationRule:
    """Input/business validation."""
    field_name: str
    rule_type: str  # REQUIRED/RANGE/FORMAT/BUSINESS
    constraint: str
    error_message: str
    line_number: int


@dataclass
class MethodSpec:
    """Method specification."""
    name: str
    purpose: str
    line_start: int
    line_end: int
    parameters: List[Dict[str, str]]
    return_type: str
    is_public: bool


class LegacyDocGeneratorOrchestrator(BaseOperationModule):
    """
    Orchestrates reverse-engineering of legacy C# code.
    
    Workflow:
    1. Parse C# file with tree-sitter
    2. Extract methods, classes, logic
    3. Identify business rules (if/else/switch)
    4. Map database operations
    5. Extract validation logic
    6. Generate PM/BA specification
    7. Create Mermaid data flow diagram
    8. Build traceability matrix
    9. Map to Clean Architecture layers
    """
    
    def __init__(self):
        super().__init__()
        self.analyzer = CSharpAnalyzer()
        self.ast_engine = None  # Lazy load
        
    def generate_specification(
        self,
        legacy_file: Path,
        output_folder: Path
    ) -> OperationResult:
        """
        Generate complete specification from legacy file.
        
        Args:
            legacy_file: Path to legacy C# file
            output_folder: Where to store generated docs
            
        Returns:
            OperationResult with generated files
        """
        logger.info(f"🎭 Orchestrator engaged: LegacyDocGeneratorOrchestrator")
        logger.info(f"📄 Analyzing: {legacy_file.name}")
        
        try:
            # Phase 1: Read and parse
            code = legacy_file.read_text(encoding='utf-8')
            ast_tree = self.analyzer._parse_code(code)
            
            if not ast_tree:
                return OperationResult(
                    status=OperationStatus.FAILED,
                    message=f"Failed to parse {legacy_file.name}",
                    metadata={}
                )
            
            # Phase 2: Extract components
            logger.info("🎭 Phase transition: PARSE → EXTRACT")
            methods = self._extract_methods(ast_tree, code)
            rules = self._extract_business_rules(ast_tree, code)
            data_ops = self._extract_data_operations(ast_tree, code)
            validations = self._extract_validations(ast_tree, code)
            
            # Phase 3: Generate documentation
            logger.info("🎭 Phase transition: EXTRACT → GENERATE")
            
            output_folder.mkdir(parents=True, exist_ok=True)
            
            # Generate business spec
            spec_file = output_folder / "business-spec.md"
            self._generate_business_spec(
                spec_file, legacy_file, methods, rules, data_ops, validations, code
            )
            
            # Generate data flow diagram
            flow_file = output_folder / "data-flow.mmd"
            self._generate_data_flow(flow_file, methods, data_ops)
            
            # Generate traceability matrix
            matrix_file = output_folder / "traceability-matrix.md"
            self._generate_traceability_matrix(matrix_file, legacy_file, rules, data_ops)
            
            # Generate layer mapping
            layer_file = output_folder / "layer-mapping.md"
            self._generate_layer_mapping(layer_file, methods, rules, data_ops)
            
            logger.info("🎭 Orchestrator completing: ✅ ALL WORK COMPLETE")
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"Generated specification for {legacy_file.name}",
                metadata={
                    'legacy_file': str(legacy_file),
                    'output_folder': str(output_folder),
                    'files_generated': [
                        'business-spec.md',
                        'data-flow.mmd',
                        'traceability-matrix.md',
                        'layer-mapping.md'
                    ],
                    'methods_extracted': len(methods),
                    'business_rules': len(rules),
                    'data_operations': len(data_ops),
                    'validations': len(validations)
                }
            )
            
        except Exception as e:
            logger.error(f"❌ Failed to generate specification: {e}")
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Error: {str(e)}",
                metadata={'error': str(e)}
            )
    
    def _extract_methods(self, ast_tree: Any, code: str) -> List[MethodSpec]:
        """Extract all method specifications."""
        methods = []
        
        # Find method declarations
        query = """
        (method_declaration) @method
        """
        
        # Use tree-sitter query (simplified - actual implementation would use proper queries)
        method_nodes = self.analyzer._find_methods(ast_tree)
        
        for node in method_nodes:
            method_name = self.analyzer._get_method_name(node, code)
            start_line = node.start_point[0] + 1
            end_line = node.end_point[0] + 1
            
            # Extract method details
            method_text = code.split('\n')[start_line-1:end_line]
            is_public = any('public' in line for line in method_text[:3])
            
            methods.append(MethodSpec(
                name=method_name,
                purpose=f"Purpose extracted from {method_name}",  # TODO: Enhance
                line_start=start_line,
                line_end=end_line,
                parameters=[],  # TODO: Extract parameters
                return_type="void",  # TODO: Extract return type
                is_public=is_public
            ))
        
        return methods
    
    def _extract_business_rules(self, ast_tree: Any, code: str) -> List[BusinessRule]:
        """Extract IF/ELSE business logic as rules."""
        rules = []
        lines = code.split('\n')
        
        # Find if statements
        def find_if_statements(node, depth=0):
            if node.type == 'if_statement':
                start_line = node.start_point[0] + 1
                end_line = node.end_point[0] + 1
                
                # Extract condition
                condition_text = lines[start_line-1].strip()
                
                # Determine layer based on context
                layer = self._guess_layer(condition_text)
                
                rules.append(BusinessRule(
                    name=f"Rule at Line {start_line}",
                    description=f"Conditional logic: {condition_text[:50]}...",
                    condition=condition_text,
                    action="Then/Else action",
                    line_start=start_line,
                    line_end=end_line,
                    layer=layer
                ))
            
            for child in node.children:
                find_if_statements(child, depth + 1)
        
        find_if_statements(ast_tree.root_node)
        return rules
    
    def _extract_data_operations(self, ast_tree: Any, code: str) -> List[DataOperation]:
        """Extract database queries and service calls."""
        operations = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Database operations
            if any(keyword in line for keyword in ['SELECT', 'INSERT', 'UPDATE', 'DELETE']):
                operations.append(DataOperation(
                    operation_type=next(k for k in ['SELECT', 'INSERT', 'UPDATE', 'DELETE'] if k in line),
                    target="Database table",  # TODO: Extract table name
                    purpose="Database operation",
                    line_number=i
                ))
            
            # Repository calls
            if 'Repository' in line or '.Get' in line or '.Save' in line:
                operations.append(DataOperation(
                    operation_type="REPOSITORY",
                    target="Data access",
                    purpose="Repository operation",
                    line_number=i
                ))
            
            # Service calls
            if 'Client' in line or 'Service' in line:
                operations.append(DataOperation(
                    operation_type="SERVICE_CALL",
                    target="External service",
                    purpose="Service invocation",
                    line_number=i
                ))
        
        return operations
    
    def _extract_validations(self, ast_tree: Any, code: str) -> List[ValidationRule]:
        """Extract validation rules."""
        validations = []
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # throw statements
            if 'throw' in line and 'Exception' in line:
                validations.append(ValidationRule(
                    field_name="Field",  # TODO: Extract field
                    rule_type="BUSINESS",
                    constraint="Must satisfy condition",
                    error_message=line.strip(),
                    line_number=i
                ))
            
            # IsNullOrEmpty checks
            if 'IsNullOrEmpty' in line or '== null' in line:
                validations.append(ValidationRule(
                    field_name="Field",  # TODO: Extract field
                    rule_type="REQUIRED",
                    constraint="Cannot be null/empty",
                    error_message="Required field",
                    line_number=i
                ))
        
        return validations
    
    def _guess_layer(self, code_snippet: str) -> str:
        """Guess Clean Architecture layer based on code context."""
        snippet_lower = code_snippet.lower()
        
        if any(kw in snippet_lower for kw in ['repository', 'database', 'sql', 'query']):
            return "Infrastructure"
        elif any(kw in snippet_lower for kw in ['validate', 'check', 'ensure']):
            return "Domain"
        else:
            return "UseCase"
    
    def _generate_business_spec(
        self,
        output_file: Path,
        legacy_file: Path,
        methods: List[MethodSpec],
        rules: List[BusinessRule],
        data_ops: List[DataOperation],
        validations: List[ValidationRule],
        code: str
    ):
        """Generate PM/BA-readable business specification."""
        api_name = legacy_file.stem
        
        content = f"""# RA API Specification - {api_name}

**API Name:** {api_name}  
**Legacy Location:** `{legacy_file.relative_to(Path('C:/PROJECTS/Platform.Classic'))}`  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Status:** Draft - Generated by CORTEX

---

## 📋 Document Overview

**Purpose:** Define business logic and behavior for {api_name} in plain English for PM/BA validation

**Audience:** Product Managers, Business Analysts, QA, Developers

**Traceability:** All rules reference legacy code line numbers for verification

---

## 🎯 Business Purpose

**What This API Does:**
{self._infer_business_purpose(api_name, code)}

**Example Use Case:**
```
User Story: As a system administrator, I need to {api_name.lower().replace('_', ' ')} so that business operations continue
Scenario: [Concrete example to be filled by PM/BA]
```

---

## 📐 Business Rules

"""
        for i, rule in enumerate(rules, 1):
            content += f"""### Rule {i}: {rule.name}

**Description:** {rule.description}

**Logic:**
- IF {rule.condition}
- THEN [Action to be documented]

**Example:**
```
Input: [To be filled with concrete values]
Expected: [Expected outcome]
```

**Layer Mapping:** {rule.layer}

**Legacy Reference:** Lines {rule.line_start}-{rule.line_end}

---

"""
        
        content += """## 💾 Data Operations

"""
        for op in data_ops:
            content += f"""**{op.operation_type}** - Line {op.line_number}
- Target: {op.target}
- Purpose: {op.purpose}

"""
        
        content += """## ⚠️ Validation Rules

"""
        for val in validations:
            content += f"""**{val.rule_type}** - Line {val.line_number}
- Field: {val.field_name}
- Constraint: {val.constraint}
- Error: {val.error_message}

"""
        
        content += f"""## ✅ PM/BA Review Checklist

**Completeness Check:**
- [ ] All business rules documented with examples ({len(rules)} rules found)
- [ ] All error scenarios explained ({len(validations)} validations found)
- [ ] All validation rules specified
- [ ] Data flow diagram accurate ({len(data_ops)} operations found)
- [ ] No technical jargon without explanation

**Approval:**
- PM Name: _____________________
- BA Name: _____________________
- Date: _____________________

---

**Document Status:** Draft - Requires PM/BA Review  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}  
**Generated by:** CORTEX Legacy Documentation Generator v1.0
"""
        
        output_file.write_text(content, encoding='utf-8')
        logger.info(f"✅ Generated: {output_file.name}")
    
    def _generate_data_flow(self, output_file: Path, methods: List[MethodSpec], data_ops: List[DataOperation]):
        """Generate Mermaid sequence diagram."""
        content = """```mermaid
sequenceDiagram
    participant Client
    participant Transaction
    participant Repository
    participant Database
    
    Client->>Transaction: Execute()
    Transaction->>Transaction: Validate inputs
    
"""
        
        for op in data_ops[:5]:  # Limit to first 5 operations
            if op.operation_type in ['SELECT', 'REPOSITORY']:
                content += f"""    Transaction->>Repository: {op.purpose}
    Repository->>Database: {op.operation_type}
    Database-->>Repository: Results
    Repository-->>Transaction: Data
    
"""
        
        content += """    Transaction-->>Client: Success/Error
```

**Key Paths:**
1. Happy path: Valid execution
2. Error path: Validation failure
3. Error path: Data not found

**Generated by:** CORTEX Legacy Documentation Generator v1.0
"""
        
        output_file.write_text(content, encoding='utf-8')
        logger.info(f"✅ Generated: {output_file.name}")
    
    def _generate_traceability_matrix(
        self,
        output_file: Path,
        legacy_file: Path,
        rules: List[BusinessRule],
        data_ops: List[DataOperation]
    ):
        """Generate traceability matrix."""
        content = f"""# Traceability Matrix - {legacy_file.stem}

| Legacy Code | Line | Business Rule | Spec Section | Modern Layer |
|-------------|------|---------------|--------------|--------------|
"""
        
        for i, rule in enumerate(rules, 1):
            content += f"| {legacy_file.name} | {rule.line_start}-{rule.line_end} | {rule.name} | § {i} | {rule.layer} |\n"
        
        content += f"""
**Coverage:**
- Total rules mapped: {len(rules)}
- Total data operations: {len(data_ops)}

**Generated by:** CORTEX Legacy Documentation Generator v1.0
"""
        
        output_file.write_text(content, encoding='utf-8')
        logger.info(f"✅ Generated: {output_file.name}")
    
    def _generate_layer_mapping(
        self,
        output_file: Path,
        methods: List[MethodSpec],
        rules: List[BusinessRule],
        data_ops: List[DataOperation]
    ):
        """Generate Clean Architecture layer mapping."""
        content = """# Clean Architecture Layer Mapping

## Proposed Modern Structure

### Domain Layer (HealthEquity.RA.DomainCore)
- Business entities
- Business rules
- Validation logic

**Dependencies:** NONE

### UseCase Layer (HealthEquity.RA.UseCase)
- Orchestration logic
- Transaction coordination

**Dependencies:** Domain only

### Infrastructure Layer (HealthEquity.RA.Data.Repositories)
- Database access
- External service calls

**Dependencies:** Domain (entities), EF Core

### Presentation Layer (HealthEquity.RA.Api.Host)
- API controllers
- DTOs
- Request/Response models

**Dependencies:** Domain + UseCase (code), Infrastructure (DI only)

---

## Legacy → Modern Mapping

| Legacy Component | Modern Layer | Rationale |
|------------------|--------------|-----------|
"""
        
        for rule in rules:
            content += f"| Business rule (Line {rule.line_start}) | {rule.layer} | {rule.description[:50]}... |\n"
        
        content += """
**Generated by:** CORTEX Legacy Documentation Generator v1.0
"""
        
        output_file.write_text(content, encoding='utf-8')
        logger.info(f"✅ Generated: {output_file.name}")
    
    def _infer_business_purpose(self, api_name: str, code: str) -> str:
        """Infer business purpose from name and code."""
        name_lower = api_name.lower()
        
        if 'create' in name_lower:
            return f"Creates {api_name.replace('Create', '').replace('_', ' ')}"
        elif 'update' in name_lower:
            return f"Updates {api_name.replace('Update', '').replace('_', ' ')}"
        elif 'generate' in name_lower:
            return f"Generates {api_name.replace('Generate', '').replace('_', ' ')}"
        elif 'delete' in name_lower:
            return f"Deletes {api_name.replace('Delete', '').replace('_', ' ')}"
        else:
            return f"Manages {api_name.replace('_', ' ')}"


# Export
__all__ = ['LegacyDocGeneratorOrchestrator']
