"""
Legacy API Specification Generator - CORTEX Lens Capability

Analyzes legacy C# code and generates:
- PM/BA-readable specifications
- OpenAPI 3.0 specifications
- Cross-check test fixtures

Part of CORTEX Lens for comprehensive legacy API reverse engineering.

Author: CORTEX
Version: 3.0.0 (OpenAPI Generation)
Date: December 15, 2025
"""

import re
import sys
import json
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class MethodInfo:
    """Represents a method extracted from legacy code."""
    name: str
    return_type: str
    parameters: List[str]
    line_start: int
    line_end: int
    body: str


@dataclass
class BusinessRule:
    """Represents a business rule extracted from code."""
    rule_id: int
    name: str
    description: str
    condition: str
    action: str
    line_number: int
    layer: str  # Domain, UseCase, Infrastructure


@dataclass
class ValidationRule:
    """Represents a validation rule."""
    field: str
    rule_type: str
    message: str
    line_number: int


@dataclass
class DatabaseOperation:
    """Represents a database operation."""
    operation_type: str  # SELECT, INSERT, UPDATE, DELETE
    table: str
    line_number: int
    purpose: str


@dataclass
class OpenAPIEndpoint:
    """Represents an inferred REST endpoint."""
    path: str
    method: str  # GET, POST, PUT, DELETE
    operation_id: str
    summary: str
    request_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    parameters: List[Dict[str, Any]] = None
    errors: List[Dict[str, Any]] = None


@dataclass
class PropertySchema:
    """Represents a property schema for OpenAPI."""
    name: str
    type: str
    required: bool
    validation: Optional[Dict[str, Any]] = None
    description: str = ""


class LegacySpecGenerator:
    """Generates specifications from legacy C# code - CORTEX Lens Capability."""
    
    def __init__(self, legacy_file: Path, output_dir: Path):
        self.legacy_file = legacy_file
        self.output_dir = output_dir
        
        # Try different encodings
        for encoding in ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']:
            try:
                self.content = legacy_file.read_text(encoding=encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise ValueError(f"Could not decode file with any known encoding: {legacy_file}")
        
        self.lines = self.content.split('\n')
        
        # Extracted components
        self.class_name = ""
        self.namespace = ""
        self.methods: List[MethodInfo] = []
        self.business_rules: List[BusinessRule] = []
        self.validations: List[ValidationRule] = []
        self.db_operations: List[DatabaseOperation] = []
        self.dependencies: List[str] = []
        self.openapi_endpoints: List[OpenAPIEndpoint] = []
        self.narrator_enabled = True  # Enable narrator agent by default
        self.openapi_enabled = True  # Enable OpenAPI generation by default
        
    def analyze(self):
        """Perform complete AST-like analysis of legacy code."""
        print(f"🔍 Analyzing {self.legacy_file.name}...")
        
        self._extract_metadata()
        self._extract_dependencies()
        self._extract_methods()
        self._extract_business_rules()
        self._extract_validations()
        self._extract_database_operations()
        
        # CORTEX Lens: OpenAPI extraction
        if self.openapi_enabled:
            self._extract_openapi_endpoints()
        
        print(f"✅ Analysis complete:")
        print(f"   - Methods: {len(self.methods)}")
        print(f"   - Business Rules: {len(self.business_rules)}")
        print(f"   - Validations: {len(self.validations)}")
        print(f"   - DB Operations: {len(self.db_operations)}")
        if self.openapi_enabled:
            print(f"   - OpenAPI Endpoints: {len(self.openapi_endpoints)}")
    
    def _extract_metadata(self):
        """Extract class name and namespace."""
        # Extract namespace
        ns_match = re.search(r'namespace\s+(\S+)', self.content)
        if ns_match:
            self.namespace = ns_match.group(1)
        
        # Extract class name (handle partial classes)
        class_match = re.search(r'public\s+(?:partial\s+)?class\s+(\w+)', self.content)
        if class_match:
            self.class_name = class_match.group(1)
    
    def _extract_dependencies(self):
        """Extract using statements and external dependencies."""
        using_pattern = r'using\s+([^;]+);'
        matches = re.finditer(using_pattern, self.content)
        
        for match in matches:
            dep = match.group(1).strip()
            if dep not in ['System', 'System.Linq']:  # Filter common ones
                self.dependencies.append(dep)
    
    def _extract_methods(self):
        """Extract all methods with their bodies."""
        # Pattern for method signatures
        method_pattern = r'(public|private|protected|internal)\s+(?:override\s+)?(?:async\s+)?(\w+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)'
        
        matches = re.finditer(method_pattern, self.content, re.MULTILINE)
        
        for match in matches:
            visibility = match.group(1)
            return_type = match.group(2)
            method_name = match.group(3)
            params = match.group(4)
            
            # Find line number
            line_num = self.content[:match.start()].count('\n') + 1
            
            # Extract method body (simplified - find matching braces)
            body_start = self.content.find('{', match.end())
            if body_start != -1:
                brace_count = 1
                body_end = body_start + 1
                while brace_count > 0 and body_end < len(self.content):
                    if self.content[body_end] == '{':
                        brace_count += 1
                    elif self.content[body_end] == '}':
                        brace_count -= 1
                    body_end += 1
                
                body = self.content[body_start:body_end]
                line_end = self.content[:body_end].count('\n') + 1
                
                self.methods.append(MethodInfo(
                    name=method_name,
                    return_type=return_type,
                    parameters=params.split(',') if params else [],
                    line_start=line_num,
                    line_end=line_end,
                    body=body
                ))
    
    def _extract_business_rules(self):
        """Extract business rules from if statements and logic."""
        rule_id = 1
        
        # Pattern for if statements
        if_pattern = r'if\s*\(([^)]+)\)'
        matches = re.finditer(if_pattern, self.content, re.MULTILINE)
        
        for match in matches:
            condition = match.group(1).strip()
            line_num = self.content[:match.start()].count('\n') + 1
            
            # Try to extract what happens after the condition
            block_start = self.content.find('{', match.end())
            if block_start == -1:
                # Single-line if
                block_start = match.end()
                block_end = self.content.find(';', block_start) + 1
            else:
                # Multi-line if - find matching brace
                brace_count = 1
                block_end = block_start + 1
                while brace_count > 0 and block_end < len(self.content):
                    if self.content[block_end] == '{':
                        brace_count += 1
                    elif self.content[block_end] == '}':
                        brace_count -= 1
                    block_end += 1
            
            action = self.content[block_start:block_end].strip()
            
            # Determine layer based on what the action does
            layer = self._classify_layer(action)
            
            # Generate rule name from condition
            rule_name = self._generate_rule_name(condition)
            
            self.business_rules.append(BusinessRule(
                rule_id=rule_id,
                name=rule_name,
                description=f"When {condition}, perform specific action",
                condition=condition,
                action=action[:100],  # Truncate for summary
                line_number=line_num,
                layer=layer
            ))
            rule_id += 1
    
    def _classify_layer(self, code: str) -> str:
        """Classify code into Clean Architecture layer."""
        code_lower = code.lower()
        
        if any(keyword in code_lower for keyword in ['new ', 'resolvelink', 'save', 'update', 'delete']):
            if any(db in code_lower for db in ['repository', 'context', 'database']):
                return 'Infrastructure'
        
        if 'throw' in code_lower or 'validate' in code_lower:
            return 'Domain'
        
        return 'UseCase'
    
    def _generate_rule_name(self, condition: str) -> str:
        """Generate a readable rule name from a condition."""
        # Preserve operators for semantic meaning
        name = condition.replace('==', '_equals_').replace('!=', '_not_equals_')
        name = name.replace('<=', '_less_equal_').replace('>=', '_greater_equal_')
        name = name.replace('<', '_less_').replace('>', '_greater_')
        name = name.replace('&&', '_and_').replace('||', '_or_')
        
        # Remove other special chars but keep underscores and alphanumeric
        name = re.sub(r'[^\w]', '_', name)
        
        # Remove consecutive underscores
        name = re.sub(r'_+', '_', name).strip('_')
        
        # Intelligently truncate at word boundaries
        if len(name) > 60:
            # Find last underscore before position 60
            truncate_pos = name[:60].rfind('_')
            if truncate_pos > 30:  # Only truncate if we preserve enough context
                name = name[:truncate_pos]
            else:
                name = name[:60]
        
        return name if name else "Rule"
    
    def _extract_validations(self):
        """Extract validation rules."""
        # Pattern for throw statements
        throw_pattern = r'throw\s+new\s+(\w+)\s*\(\s*"([^"]+)"\s*\)'
        matches = re.finditer(throw_pattern, self.content, re.MULTILINE)
        
        for match in matches:
            exception_type = match.group(1)
            message = match.group(2)
            line_num = self.content[:match.start()].count('\n') + 1
            
            # Try to find what field this validates - look backwards more carefully
            preceding = self.content[max(0, match.start()-300):match.start()]
            
            # Try multiple patterns to extract field name
            field = "Unknown"
            
            # Pattern 1: field == null or field == 0
            field_match = re.search(r'([A-Z]\w+)\s*[=<>!]+\s*(?:null|0)', preceding)
            if field_match:
                field = field_match.group(1)
            else:
                # Pattern 2: String.IsNullOrWhiteSpace(FieldName)
                field_match = re.search(r'IsNullOrWhiteSpace\s*\(\s*(\w+)\s*\)', preceding)
                if field_match:
                    field = field_match.group(1)
                else:
                    # Pattern 3: field < or field > comparisons
                    field_match = re.search(r'([A-Z]\w+)\s*[<>]', preceding)
                    if field_match:
                        field = field_match.group(1)
                    else:
                        # Pattern 4: Look for any capitalized word before 'if'
                        field_match = re.search(r'if\s*\(([A-Z]\w+)', preceding)
                        if field_match:
                            field = field_match.group(1)
            
            self.validations.append(ValidationRule(
                field=field,
                rule_type=exception_type,
                message=message,
                line_number=line_num
            ))
    
    def _extract_database_operations(self):
        """Extract database operations."""
        # Pattern for ResolveLink (common in legacy code)
        resolve_pattern = r'ResolveLink\s*\(\s*typeof\((\w+)\)'
        matches = re.finditer(resolve_pattern, self.content, re.MULTILINE)
        
        for match in matches:
            table = match.group(1)
            line_num = self.content[:match.start()].count('\n') + 1
            
            self.db_operations.append(DatabaseOperation(
                operation_type='SELECT',
                table=table,
                line_number=line_num,
                purpose=f'Retrieve {table} entity'
            ))
        
        # Pattern for property assignments (potential updates)
        update_pattern = r'(\w+)\.(\w+)\s*=\s*([^;]+);'
        matches = re.finditer(update_pattern, self.content, re.MULTILINE)
        
        for match in matches:
            entity = match.group(1)
            property_name = match.group(2)
            value = match.group(3).strip()
            line_num = self.content[:match.start()].count('\n') + 1
            
            # Only count if it looks like a database entity (starts with uppercase)
            if entity[0].isupper() and entity not in ['String', 'Int', 'Bool']:
                self.db_operations.append(DatabaseOperation(
                    operation_type='UPDATE',
                    table=entity,
                    line_number=line_num,
                    purpose=f'Update {property_name} to {value[:30]}'
                ))
    
    def _extract_openapi_endpoints(self):
        """
        CORTEX Lens: Extract OpenAPI endpoint specifications from legacy code.
        Infers REST endpoints, request/response schemas, and validations.
        """
        # Infer endpoint from class name
        endpoint_path = self._infer_endpoint_path()
        http_method = self._infer_http_method()
        
        # Build request schema from method parameters
        request_schema = self._build_request_schema()
        
        # Build response schema from return type and DB operations
        response_schema = self._build_response_schema()
        
        # Build parameters (path/query)
        parameters = self._build_parameters()
        
        # Build error responses from validations
        error_responses = self._build_error_responses()
        
        endpoint = OpenAPIEndpoint(
            path=endpoint_path,
            method=http_method,
            operation_id=self.class_name,
            summary=self._generate_business_purpose(),
            request_schema=request_schema,
            response_schema=response_schema,
            parameters=parameters if parameters else [],
            errors=error_responses if error_responses else []
        )
        
        self.openapi_endpoints.append(endpoint)
    
    def _infer_endpoint_path(self) -> str:
        """Infer REST API path from class name."""
        # Remove common prefixes
        name = self.class_name
        for prefix in ['X', 'Updater_', 'Service_']:
            if name.startswith(prefix):
                name = name[len(prefix):]
        
        # Convert PascalCase to kebab-case
        path = re.sub('([a-z0-9])([A-Z])', r'\1-\2', name).lower()
        
        return f"/api/ra/{path}"
    
    def _infer_http_method(self) -> str:
        """Infer HTTP method from class/method names."""
        name_lower = self.class_name.lower()
        
        if 'create' in name_lower or 'generate' in name_lower or 'add' in name_lower:
            return 'POST'
        elif 'update' in name_lower or 'modify' in name_lower:
            return 'PUT'
        elif 'delete' in name_lower or 'remove' in name_lower:
            return 'DELETE'
        elif 'get' in name_lower or 'find' in name_lower or 'search' in name_lower:
            return 'GET'
        else:
            # Check DB operations
            if self.db_operations:
                if any('INSERT' in op.operation_type or 'CREATE' in op.operation_type for op in self.db_operations):
                    return 'POST'
                elif any('UPDATE' in op.operation_type for op in self.db_operations):
                    return 'PUT'
                elif any('DELETE' in op.operation_type for op in self.db_operations):
                    return 'DELETE'
            return 'POST'  # Default for operations
    
    def _build_request_schema(self) -> Optional[Dict[str, Any]]:
        """Build OpenAPI request schema from method parameters and validations."""
        # Find primary method
        primary_method = next((m for m in self.methods if m.name in ['Execute', 'Run', 'Process']), None)
        
        if not primary_method or not primary_method.parameters:
            return None
        
        properties = {}
        required = []
        
        # Extract properties from validations
        for validation in self.validations:
            prop_name = validation.field if validation.field != 'Unknown' else f'field{len(properties)}'
            
            properties[prop_name] = {
                'type': 'string',  # Default type
                'description': validation.message if validation.message else f'Validated field: {prop_name}'
            }
            
            # Add validation constraints
            if 'null' in validation.rule_type.lower() or 'empty' in validation.rule_type.lower():
                required.append(prop_name)
                properties[prop_name]['minLength'] = 1
        
        # If no validations, infer from business rules
        if not properties:
            for rule in self.business_rules[:5]:
                # Extract field names from conditions
                field_matches = re.findall(r'(\w+)\s*[<>=!]+', rule.condition)
                for field in field_matches:
                    if field not in ['true', 'false', 'null'] and field[0].isupper():
                        prop_name = field[0].lower() + field[1:]
                        if prop_name not in properties:
                            properties[prop_name] = {
                                'type': self._infer_type_from_condition(rule.condition, field),
                                'description': f'Business rule: {rule.description[:50]}'
                            }
        
        if not properties:
            return None
        
        return {
            'type': 'object',
            'properties': properties,
            'required': required if required else []
        }
    
    def _infer_type_from_condition(self, condition: str, field: str) -> str:
        """Infer OpenAPI type from condition pattern."""
        condition_lower = condition.lower()
        
        if 'amount' in field.lower() or 'balance' in field.lower() or '<=' in condition or '>=' in condition:
            return 'number'
        elif 'date' in field.lower() or 'time' in field.lower():
            return 'string'  # Will add format: date-time
        elif 'count' in field.lower() or 'id' in field.lower():
            return 'integer'
        elif '==' in condition and ('true' in condition_lower or 'false' in condition_lower):
            return 'boolean'
        else:
            return 'string'
    
    def _build_response_schema(self) -> Optional[Dict[str, Any]]:
        """Build OpenAPI response schema from return type and DB operations."""
        primary_method = next((m for m in self.methods if m.name in ['Execute', 'Run', 'Process']), None)
        
        if not primary_method:
            return None
        
        # If void return, infer from DB operations
        if primary_method.return_type == 'void':
            if not self.db_operations:
                return {
                    'type': 'object',
                    'properties': {
                        'success': {'type': 'boolean'},
                        'message': {'type': 'string'}
                    }
                }
            else:
                # Infer from DB operations
                entities = list(set(op.table for op in self.db_operations if op.operation_type == 'SELECT'))
                if entities:
                    return {
                        'type': 'object',
                        'properties': {
                            'data': {
                                'type': 'array' if len(entities) > 1 else 'object',
                                'description': f'Retrieved {", ".join(entities)} entities'
                            }
                        }
                    }
        
        return {
            'type': 'object',
            'properties': {
                'result': {
                    'type': 'string',
                    'description': f'Result of {self.class_name} operation'
                }
            }
        }
    
    def _build_parameters(self) -> Optional[List[Dict[str, Any]]]:
        """Build OpenAPI path/query parameters."""
        parameters = []
        
        # Check if any validations reference ID fields
        for validation in self.validations:
            if 'id' in validation.field.lower() and validation.field != 'Unknown':
                parameters.append({
                    'name': validation.field,
                    'in': 'path',
                    'required': True,
                    'schema': {'type': 'string'},
                    'description': f'Unique identifier for {validation.field}'
                })
        
        return parameters if parameters else None
    
    def _build_error_responses(self) -> Optional[List[Dict[str, Any]]]:
        """Build error response schemas from validations."""
        if not self.validations:
            return None
        
        errors = []
        for validation in self.validations:
            errors.append({
                'status': 400,
                'description': validation.message if validation.message else 'Validation error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'},
                        'field': {'type': 'string', 'example': validation.field},
                        'code': {'type': 'string', 'example': validation.rule_type}
                    }
                }
            })
        
        return errors
    
    def _generate_openapi_dict(self) -> Dict[str, Any]:
        """
        CORTEX Lens: Generate OpenAPI 3.0 specification as Python dict.
        Internal method used by both YAML and JSON generators.
        """
        openapi_spec = {
            'openapi': '3.0.3',
            'info': {
                'title': f'{self.class_name} API',
                'description': f'Reverse-engineered API specification from legacy {self.class_name}',
                'version': '1.0.0',
                'contact': {
                    'name': 'CORTEX Lens',
                    'url': 'https://github.com/asifhussain60/CORTEX'
                },
                'x-legacy-source': {
                    'file': str(self.legacy_file),
                    'class': self.class_name,
                    'namespace': self.namespace,
                    'generated': datetime.now().isoformat()
                }
            },
            'servers': [
                {
                    'url': 'https://api.example.com/v1',
                    'description': 'Production server (placeholder)'
                }
            ],
            'paths': {},
            'components': {
                'schemas': {},
                'responses': {
                    'ValidationError': {
                        'description': 'Validation error response',
                        'content': {
                            'application/json': {
                                'schema': {
                                    'type': 'object',
                                    'properties': {
                                        'error': {'type': 'string'},
                                        'field': {'type': 'string'},
                                        'code': {'type': 'string'}
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
        
        # Add endpoints
        for endpoint in self.openapi_endpoints:
            if endpoint.path not in openapi_spec['paths']:
                openapi_spec['paths'][endpoint.path] = {}
            
            operation = {
                'operationId': endpoint.operation_id,
                'summary': endpoint.summary,
                'tags': ['RA Operations'],
                'responses': {
                    '200': {
                        'description': 'Successful operation',
                        'content': {
                            'application/json': {
                                'schema': endpoint.response_schema
                            }
                        }
                    }
                }
            }
            
            # Add request body if present
            if endpoint.request_schema:
                operation['requestBody'] = {
                    'required': True,
                    'content': {
                        'application/json': {
                            'schema': endpoint.request_schema
                        }
                    }
                }
            
            # Add parameters if present
            if endpoint.parameters:
                operation['parameters'] = endpoint.parameters
            
            # Add error responses
            if endpoint.errors:
                for error in endpoint.errors:
                    operation['responses'][str(error['status'])] = {
                        'description': error['description'],
                        'content': {
                            'application/json': {
                                'schema': error['schema']
                            }
                        }
                    }
            
            openapi_spec['paths'][endpoint.path][endpoint.method.lower()] = operation
        
        return openapi_spec
    
    def generate_openapi_spec(self) -> str:
        """
        CORTEX Lens: Generate OpenAPI 3.0 specification in YAML format.
        Returns formatted YAML string ready for file output.
        """
        spec_dict = self._generate_openapi_dict()
        
        # Convert to YAML with custom formatting
        yaml_output = yaml.dump(
            spec_dict,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
            indent=2,
            width=120
        )
        
        # Add header comment
        header = f"""# OpenAPI 3.0 Specification
# API: {self.class_name}
# Generated by: CORTEX Lens v3.0
# Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX
# Source: {self.legacy_file.name}
# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
#
# This specification was reverse-engineered from legacy code.
# Review and adjust server URLs, security schemes, and examples before production use.

"""
        
        return header + yaml_output
    
    def generate_openapi_json(self) -> str:
        """
        CORTEX Lens: Generate OpenAPI 3.0 specification in JSON format.
        Returns formatted JSON string ready for file output.
        """
        spec_dict = self._generate_openapi_dict()
        
        # Convert to JSON with formatting
        json_output = json.dumps(spec_dict, indent=2, ensure_ascii=False)
        
        return json_output
    
    def generate_cross_check_fixtures(self) -> Dict[str, Any]:
        """
        CORTEX Lens: Generate test fixtures for cross-checking legacy vs modern implementation.
        Returns test cases with inputs and expected validation behavior.
        """
        fixtures = {
            'api': self.class_name,
            'generated': datetime.now().isoformat(),
            'test_cases': []
        }
        
        # Generate test cases from validations
        for i, validation in enumerate(self.validations, 1):
            fixtures['test_cases'].append({
                'id': f'validation_{i}',
                'description': f'Test {validation.rule_type} validation',
                'input': {
                    validation.field: None if 'null' in validation.rule_type.lower() else ''
                },
                'expected_error': {
                    'field': validation.field,
                    'type': validation.rule_type,
                    'message': validation.message
                },
                'legacy_line': validation.line_number
            })
        
        # Generate test cases from business rules
        for i, rule in enumerate(self.business_rules[:5], 1):
            # Extract test value from condition
            test_value = self._extract_test_value_from_condition(rule.condition)
            
            fixtures['test_cases'].append({
                'id': f'business_rule_{i}',
                'description': rule.description,
                'input': test_value,
                'expected_behavior': rule.action[:100],
                'legacy_line': rule.line_number
            })
        
        return fixtures
    
    def _extract_test_value_from_condition(self, condition: str) -> Dict[str, Any]:
        """Extract test input values from business rule conditions."""
        test_input = {}
        
        # Extract field and value from condition
        match = re.search(r'(\w+)\s*([<>=!]+)\s*([^&|]+)', condition)
        if match:
            field = match.group(1)
            operator = match.group(2)
            value = match.group(3).strip()
            
            # Convert value to appropriate type
            if value.replace('.', '').replace('-', '').isdigit():
                test_value = float(value) if '.' in value else int(value)
            elif value.lower() in ['true', 'false']:
                test_value = value.lower() == 'true'
            elif value == 'null':
                test_value = None
            else:
                test_value = value.strip('"\'')
            
            test_input[field] = test_value
        
        return test_input
    
    def generate_business_spec(self) -> str:
        """Generate business specification document."""
        spec = f"""# RA API Specification - {self.class_name}

**Generated by:** CORTEX Lens v3.0  
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

**API Name:** {self.class_name}  
**Operation:** {self.class_name}  
**Legacy Location:** `{self.legacy_file.relative_to(self.legacy_file.parents[3])}`  
**Version:** 1.0  
**Status:** Draft  
**Generated:** {datetime.now().strftime('%Y-%m-%d')}

---

## 📊 Executive Summary

{self._generate_executive_summary()}

---

## 📋 Document Overview

**Purpose:** Define business logic and behavior for {self.class_name} in plain English for PM/BA validation

**Audience:** Product Managers, Business Analysts, QA, Developers

**Traceability:** All rules reference legacy code line numbers for verification

**Analysis Method:** CORTEX Lens AST Analysis

---

## 🎯 Business Purpose

**What This API Does:**
{self._generate_business_purpose()}

**Namespace:** `{self.namespace}`

**Dependencies:**
"""
        for dep in self.dependencies:
            spec += f"- {dep}\n"
        
        spec += f"""
---

## 📊 Visual Overview

### Embedded Diagrams (Inline Preview)

**Control Flow:**
```mermaid
{self._generate_flowchart()}
```

**Sequence Flow:**
```mermaid
{self._generate_sequence_diagram()}
```

### Diagram Files (For External Tools)

Visual diagrams are also available as separate `.mmd` files in the `diagrams/` folder for use with Mermaid renderers, draw.io, or other visualization tools.

**Available Files:**
- [Control Flow Diagram](diagrams/flowchart.mmd) - Business logic flow and decision points
- [Sequence Diagram](diagrams/sequence.mmd) - Component interactions and message flow
{self._get_dependency_diagram_link()}

**Rendering Options:**
- **VS Code:** Install [Mermaid Preview](https://marketplace.visualstudio.com/items?itemName=bierner.markdown-mermaid) extension
- **Online:** Copy diagram content to [mermaid.live](https://mermaid.live)
- **CLI:** Use `mmdc` command-line tool to generate PNG/SVG

---

## 👥 User Stories

{self._generate_detailed_user_stories()}

---

## ✅ Preconditions

**Required State Before Operation:**
"""
        
        # Analyze method Execute() or main method for preconditions
        main_method = next((m for m in self.methods if m.name in ['Execute', 'Run', 'Process']), None)
        if main_method:
            spec += f"""
1. **Input Parameters Validated**
   - Example: All required properties populated
   - Validation: Method starts at Line {main_method.line_start}

2. **Transaction Context Available**
   - Example: Inherits from HETransaction base class
   - Validation: Framework provides transaction scope

**Legacy Reference:** Lines {main_method.line_start}-{main_method.line_end}
"""
        
        spec += """
---

## 📐 Business Rules

"""
        
        for rule in self.business_rules:
            spec += f"""### Rule {rule.rule_id}: {rule.name}

**Description:** {rule.description}

**Logic:**
- IF `{rule.condition}`
- THEN Perform action
- ELSE Continue processing

**Example:**
```
Condition: {rule.condition}
Action: {rule.action[:80]}...
```

**Layer Mapping:** {rule.layer}

**Legacy Reference:** Line {rule.line_number}

---

"""
        
        spec += """## 🔄 Data Flow

**Sequence Diagram:** See [diagrams/sequence.mmd](diagrams/sequence.mmd) for complete interaction flow.

**Key Paths:**
1. Happy path: All validations pass, entities processed successfully
2. Error paths: See Error Scenarios below

---

## 💾 Data Operations

### Database Operations

**Tables Accessed:**
"""
        
        tables = set(op.table for op in self.db_operations)
        for table in tables:
            ops = [op for op in self.db_operations if op.table == table]
            spec += f"\n- `{table}` ("
            op_types = set(op.operation_type for op in ops)
            spec += ', '.join(op_types) + ")\n"
        
        spec += "\n**Operations:**\n\n"
        
        for i, op in enumerate(self.db_operations[:10], 1):  # Limit to first 10
            spec += f"""{i}. **{op.operation_type} {op.table}:**
   - Purpose: {op.purpose}
   - Legacy Reference: Line {op.line_number}

"""
        
        spec += """
---

## ⚠️ Error Scenarios

"""
        
        for i, val in enumerate(self.validations, 1):
            spec += f"""### Error {i}: {val.rule_type}

**Trigger:** {val.field} validation failure

**Error Message:** "{val.message}"

**User Action:** Verify {val.field} is provided and valid

**Example:**
```
Input: {val.field} = null
Result: {val.rule_type}
Message: "{val.message}"
```

**Legacy Reference:** Line {val.line_number}

---

"""
        
        spec += f"""
## 📊 Layer Mapping

| Legacy Code Location | Business Rule | Modern Layer | Rationale |
|---------------------|---------------|--------------|-----------|
"""
        
        for rule in self.business_rules[:10]:  # Limit to first 10
            spec += f"| Line {rule.line_number} | {rule.name[:30]} | {rule.layer} | {self._get_layer_rationale(rule.layer)} |\n"
        
        spec += """
**Design Notes:**
- Domain layer contains business validation logic
- Infrastructure handles all database access
- UseCase orchestrates the workflow

---

## ✅ PM/BA Review Checklist

**Completeness Check:**
- [ ] All business rules documented with examples
- [ ] All error scenarios explained
- [ ] Data flow diagram accurate
- [ ] No technical jargon without explanation

**Accuracy Check:**
- [ ] Examples use realistic data
- [ ] Error messages match user expectations
- [ ] Business rules match current behavior

**Approval:**
- PM Name: _____________________
- BA Name: _____________________
- Date: _____________________
- Status: ☐ Approved ☐ Needs Revision ☐ Rejected

---

## 📝 Analysis Metadata

**Generated By:** CORTEX Legacy Specification Generator v1.0  
**Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Source File:** `{self.legacy_file.name}`  
**Total Lines Analyzed:** {len(self.lines)}  
**Methods Extracted:** {len(self.methods)}  
**Business Rules Identified:** {len(self.business_rules)}  
**Validation Rules Found:** {len(self.validations)}  
**Database Operations:** {len(self.db_operations)}

---

**Document Status:** Draft - Awaiting PM/BA Review  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}
"""
        
        return spec
    
    def _generate_business_purpose(self) -> str:
        """Generate business purpose from class name."""
        # Convert PascalCase to readable text
        words = re.findall('[A-Z][^A-Z]*', self.class_name)
        if not words:
            return f"{self.class_name} operation for RA funding management"
        
        if words[0] in ['X', 'Updater']:
            words = words[1:]  # Remove prefix
        
        if not words:
            return f"{self.class_name} operation for RA funding management"
        
        return f"{' '.join(words)} operation for RA funding management"
    
    def _get_layer_rationale(self, layer: str) -> str:
        """Get rationale for layer assignment."""
        rationales = {
            'Domain': 'Business logic, no dependencies',
            'UseCase': 'Orchestration logic',
            'Infrastructure': 'Database/external access'
        }
        return rationales.get(layer, 'To be determined')
    
    def generate_traceability_matrix(self) -> str:
        """Generate traceability matrix."""
        matrix = f"""# Traceability Matrix - {self.class_name}

**Generated by:** CORTEX Lens v3.0  
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

**Purpose:** Map legacy code to business specification to modern architecture

**Generated:** {datetime.now().strftime('%Y-%m-%d')}

---

| Legacy Code | Line | Business Rule | Spec Section | Modern Layer | Project |
|-------------|------|---------------|--------------|--------------|---------|
"""
        
        for rule in self.business_rules:
            spec_section = f"§ {rule.rule_id}"
            project = f"HealthEquity.RA.{rule.layer}"
            matrix += f"| {self.legacy_file.name} | {rule.line_number} | {rule.name[:40]} | {spec_section} | {rule.layer} | {project} |\n"
        
        matrix += f"""
---

**Coverage Statistics:**
- Total Legacy Lines: {len(self.lines)}
- Mapped Lines: {len(self.business_rules)}
- Coverage: {(len(self.business_rules) / max(len(self.lines), 1) * 100):.1f}%

**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}
"""
        
        return matrix
    
    def _generate_executive_summary(self) -> str:
        """Generate executive summary for quick API understanding."""
        # Find primary method
        primary_method = next((m for m in self.methods if m.name in ['Execute', 'Run', 'Process']), None)
        if not primary_method and self.methods:
            primary_method = self.methods[0]
        
        # Extract API purpose
        purpose = self._generate_business_purpose()
        
        # Count key elements
        validation_count = len(self.validations)
        rule_count = len(self.business_rules)
        db_op_count = len(self.db_operations)
        
        # Generate user stories
        user_stories = self._extract_user_stories()
        
        summary = f"""**API Purpose:** {purpose}

**User Stories:**
{user_stories}

**Primary Interface:**"""
        
        if primary_method:
            params = ', '.join(primary_method.parameters) if primary_method.parameters else 'None'
            summary += f"""
- **Method:** `{primary_method.name}({params})`
- **Returns:** `{primary_method.return_type}`
- **Entry Point:** Line {primary_method.line_start}"""
        else:
            summary += " Not detected (class-level API)"
        
        summary += f"""

**Business Logic Complexity:**
- {rule_count} business rules extracted
- {validation_count} validation checks
- {db_op_count} database operations
- {len(self.dependencies)} external dependencies

**Key Capabilities:**"""
        
        # Identify key capabilities from business rules
        capabilities = []
        for rule in self.business_rules[:3]:  # Top 3 rules
            cap = rule.description.replace('When ', '').replace(', perform specific action', '')
            capabilities.append(f"- {cap}")
        
        if capabilities:
            summary += '\n' + '\n'.join(capabilities)
        else:
            summary += "\n- Processing logic (details in Business Rules section)"
        
        summary += f"""

**Modernization Readiness:**
- Layer Classification: {len(set(r.layer for r in self.business_rules))} distinct layers detected
- Traceability: {len(self.business_rules)} mappings to modern architecture
- Validation Coverage: {'High' if validation_count > 5 else 'Medium' if validation_count > 0 else 'Low'}
"""
        
        return summary
    
    def _extract_user_stories(self) -> str:
        """Extract user stories in 'As a..., I want to..., So that...' format."""
        # Identify actor from class name and context
        actor = self._identify_actor()
        
        # Parse action from class/method names
        action = self._parse_action()
        
        # Infer business value from rules and DB operations
        value = self._infer_business_value()
        
        # Format as user story
        story = f"""
**Primary Story:**
> As a **{actor}**, I want to **{action}**, so that **{value}**.
"""
        
        # Add secondary stories from business rules
        secondary_stories = self._generate_secondary_stories()
        if secondary_stories:
            story += f"\n**Supporting Stories:**\n{secondary_stories}"
        
        return story
    
    def _identify_actor(self) -> str:
        """Identify the primary actor/persona from code patterns."""
        class_lower = self.class_name.lower()
        
        # Pattern matching for common actors
        if 'updater' in class_lower or 'batch' in class_lower:
            return "System Administrator"
        elif 'employer' in class_lower:
            return "Employer"
        elif 'account' in class_lower or 'member' in class_lower:
            return "Account Holder"
        elif 'invoice' in class_lower or 'funding' in class_lower:
            return "Finance Team Member"
        elif 'report' in class_lower:
            return "Business Analyst"
        elif 'admin' in class_lower:
            return "System Administrator"
        else:
            return "System User"
    
    def _parse_action(self) -> str:
        """Parse the action from class/method names."""
        # Extract action from class name
        action_words = re.findall('[A-Z][^A-Z]*', self.class_name)
        
        # Remove prefixes
        prefixes = ['X', 'Updater', 'Service', 'Manager', 'Handler']
        action_words = [w for w in action_words if w not in prefixes]
        
        if not action_words:
            return "execute the operation"
        
        # Convert to verb phrase
        action_map = {
            'Create': 'create',
            'Generate': 'generate',
            'Update': 'update',
            'Delete': 'delete',
            'Process': 'process',
            'Validate': 'validate',
            'Calculate': 'calculate',
            'Send': 'send',
            'Receive': 'receive',
            'Close': 'close',
            'Open': 'open'
        }
        
        first_word = action_words[0]
        verb = action_map.get(first_word, first_word.lower())
        
        # Build action phrase
        remaining = ' '.join(action_words[1:]).lower() if len(action_words) > 1 else "records"
        
        return f"{verb} {remaining}"
    
    def _infer_business_value(self) -> str:
        """Infer business value from rules and operations."""
        # Check for funding/invoice patterns
        if 'funding' in self.class_name.lower() or 'invoice' in self.class_name.lower():
            return "ensure accurate and timely reimbursement processing"
        
        # Check for batch/updater patterns
        if 'batch' in self.class_name.lower() or 'updater' in self.class_name.lower():
            return "maintain data consistency and automate routine operations"
        
        # Check database operations
        if self.db_operations:
            if any('INSERT' in op.operation_type or 'UPDATE' in op.operation_type for op in self.db_operations):
                return "maintain accurate system records"
            elif any('SELECT' in op.operation_type for op in self.db_operations):
                return "retrieve necessary information for decision making"
        
        # Check validations
        if len(self.validations) > 3:
            return "ensure data quality and prevent errors"
        
        # Default value
        return "support business operations efficiently"
    
    def _generate_secondary_stories(self) -> str:
        """Generate secondary user stories from business rules."""
        stories = []
        
        # Extract unique rule themes
        themes = set()
        for rule in self.business_rules[:5]:  # Top 5 rules
            # Extract theme from condition
            condition = rule.condition.lower()
            
            if 'null' in condition or 'empty' in condition:
                themes.add("validation")
            elif 'date' in condition or 'time' in condition:
                themes.add("temporal_control")
            elif 'amount' in condition or 'balance' in condition:
                themes.add("financial_control")
            elif 'status' in condition or 'state' in condition:
                themes.add("state_management")
        
        # Map themes to stories
        theme_stories = {
            'validation': "> As a **Data Quality Manager**, I want to **validate all inputs**, so that **system integrity is maintained**.",
            'temporal_control': "> As a **Operations Manager**, I want to **control timing of operations**, so that **processes execute at the right time**.",
            'financial_control': "> As a **Finance Controller**, I want to **validate financial amounts**, so that **transactions are accurate**.",
            'state_management': "> As a **System Administrator**, I want to **manage entity states**, so that **workflows progress correctly**."
        }
        
        for theme in themes:
            if theme in theme_stories:
                stories.append(theme_stories[theme])
        
        return '\n'.join(stories) if stories else ""
    
    def _generate_detailed_user_stories(self) -> str:
        """Generate detailed user stories section with acceptance criteria."""
        actor = self._identify_actor()
        action = self._parse_action()
        value = self._infer_business_value()
        
        stories = f"""### Primary User Story

**Story:**
> As a **{actor}**,  
> I want to **{action}**,  
> So that **{value}**.

**Acceptance Criteria:**
"""
        
        # Generate acceptance criteria from validations
        criteria_num = 1
        if self.validations:
            stories += f"\n**Validation Requirements:**\n"
            for val in self.validations[:3]:
                stories += f"{criteria_num}. Given {val.field} is provided, when validation runs, then {val.rule_type} must be checked (Line {val.line_number})\n"
                criteria_num += 1
        
        # Generate acceptance criteria from business rules
        if self.business_rules:
            stories += f"\n**Business Logic Requirements:**\n"
            for rule in self.business_rules[:3]:
                condition_clean = rule.condition.replace('`', '').strip()
                stories += f"{criteria_num}. Given {condition_clean}, when processing occurs, then system must apply {rule.name} logic (Line {rule.line_number})\n"
                criteria_num += 1
        
        # Generate acceptance criteria from DB operations
        if self.db_operations:
            stories += f"\n**Data Persistence Requirements:**\n"
            for db_op in self.db_operations[:2]:
                stories += f"{criteria_num}. Given successful processing, when {db_op.purpose}, then {db_op.operation_type} must execute on {db_op.table} (Line {db_op.line_number})\n"
                criteria_num += 1
        
        # Add supporting stories
        secondary = self._generate_secondary_stories()
        if secondary:
            stories += f"\n---\n\n### Supporting User Stories\n\n{secondary}\n"
        
        # Add traceability note
        stories += f"""
---

**Traceability Note:** All acceptance criteria reference specific line numbers in the legacy code for verification and modernization planning.
"""
        
        return stories
    
    def _sanitize_mermaid_text(self, text: str, max_length: int = 30) -> str:
        """Sanitize text for Mermaid diagrams to avoid parse errors."""
        # Preserve operators before sanitization
        text = text.replace('<=', ' LTE ').replace('>=', ' GTE ')
        text = text.replace('<', ' LT ').replace('>', ' GT ')
        text = text.replace('==', ' EQ ').replace('!=', ' NE ')
        
        # Remove special characters that break Mermaid (but keep underscores)
        sanitized = re.sub(r'[{}\[\]()"\':]', '', text)
        # Replace problematic punctuation
        sanitized = sanitized.replace('...', '')
        sanitized = sanitized.replace('?', '')
        # Truncate and ensure complete words
        if len(sanitized) > max_length:
            # Try to find last space or underscore to break at word boundary
            last_break = max(sanitized[:max_length].rfind(' '), sanitized[:max_length].rfind('_'))
            if last_break > 10:  # Only truncate if we preserve enough context
                sanitized = sanitized[:last_break]
            else:
                sanitized = sanitized[:max_length]
        # Remove trailing punctuation (but keep underscores)
        sanitized = sanitized.rstrip('.,;: ')
        return sanitized if sanitized else "Operation"
    
    def _generate_flowchart(self) -> str:
        """Generate Mermaid flowchart from business rules."""
        # Skip if no meaningful rules
        if len(self.business_rules) < 2 and len(self.validations) == 0:
            return "*Flowchart omitted: Insufficient business logic for meaningful visualization*"
        
        flowchart = "flowchart TD\n"
        flowchart += "    Start([API Invoked]) --> Validate\n"
        
        # Add validation checks
        if self.validations:
            flowchart += "    Validate{Input Valid?}\n"
            flowchart += "    Validate -->|No| Error1[Throw Validation Error]\n"
            flowchart += "    Validate -->|Yes| Process\n"
        else:
            flowchart += "    Validate[Validate Inputs] --> Process\n"
        
        # Add business rules as decision nodes
        prev_node = "Process"
        for i, rule in enumerate(self.business_rules[:3], 1):  # Limit to 3 for clarity
            node_id = f"Rule{i}"
            decision_id = f"Check{i}"
            
            # Sanitize condition text
            condition = self._sanitize_mermaid_text(rule.condition, 25)
            rule_label = self._sanitize_mermaid_text(rule.name, 20)
            
            flowchart += f"    {prev_node} --> {decision_id}{{Condition: {condition}}}\n"
            flowchart += f"    {decision_id} -->|Yes| {node_id}[{rule_label}]\n"
            flowchart += f"    {decision_id} -->|No| Next{i}[Continue]\n"
            
            prev_node = f"Next{i}"
        
        # Add database operations
        if self.db_operations:
            flowchart += f"    {prev_node} --> DB[Database Operations]\n"
            flowchart += "    DB --> Complete\n"
        else:
            flowchart += f"    {prev_node} --> Complete\n"
        
        flowchart += "    Complete([Operation Complete])\n"
        if self.validations:
            flowchart += "    Error1 --> End([End])\n"
        flowchart += "    Complete --> End([End])\n"
        
        return flowchart
    
    def _generate_sequence_diagram(self) -> str:
        """Generate Mermaid sequence diagram."""
        # Skip if no meaningful operations
        if len(self.methods) == 0:
            return "*Sequence diagram omitted: No methods detected*"
        
        seq = "sequenceDiagram\n"
        seq += "    participant Client\n"
        
        # Sanitize class name
        class_name_safe = self._sanitize_mermaid_text(self.class_name, 40)
        seq += f"    participant {class_name_safe}\n"
        
        # Add database if operations exist
        if self.db_operations:
            seq += "    participant Database\n"
        
        seq += f"\n    Client->>+{class_name_safe}: Execute\n"
        
        # Add validation
        if self.validations:
            seq += f"    {class_name_safe}->>{class_name_safe}: Validate Inputs\n"
        
        # Add business rules as processing steps (sanitized)
        for rule in self.business_rules[:2]:  # Limit to 2 for clarity
            rule_label = self._sanitize_mermaid_text(rule.name, 30)
            seq += f"    {class_name_safe}->>{class_name_safe}: {rule_label}\n"
        
        # Add DB operations
        for db_op in self.db_operations[:2]:
            table_safe = self._sanitize_mermaid_text(db_op.table, 20)
            seq += f"    {class_name_safe}->>+Database: {db_op.operation_type} {table_safe}\n"
            seq += f"    Database-->>-{class_name_safe}: Result\n"
        
        seq += f"    {class_name_safe}-->>-Client: Success\n"
        
        return seq
    
    def _generate_diagram_files(self):
        """Generate separate .mmd files in diagrams/ folder."""
        diagrams_dir = self.output_dir / 'diagrams'
        diagrams_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate flowchart.mmd
        flowchart_content = self._generate_flowchart()
        if not flowchart_content.startswith('*Flowchart omitted'):
            flowchart_path = diagrams_dir / 'flowchart.mmd'
            flowchart_path.write_text(flowchart_content, encoding='utf-8')
            print(f"   📊 flowchart.mmd ({len(flowchart_content)} chars)")
        
        # Generate sequence.mmd
        sequence_content = self._generate_sequence_diagram()
        if not sequence_content.startswith('*Sequence diagram omitted'):
            sequence_path = diagrams_dir / 'sequence.mmd'
            sequence_path.write_text(sequence_content, encoding='utf-8')
            print(f"   📊 sequence.mmd ({len(sequence_content)} chars)")
        
        # Generate dependency.mmd (conditional)
        dependency_content = self._generate_dependency_diagram_content()
        if dependency_content:
            dependency_path = diagrams_dir / 'dependency.mmd'
            dependency_path.write_text(dependency_content, encoding='utf-8')
            print(f"   📊 dependency.mmd ({len(dependency_content)} chars)")
    
    def _get_dependency_diagram_link(self) -> str:
        """Get markdown link for dependency diagram if it exists."""
        meaningful_deps = [d for d in self.dependencies 
                          if not d.startswith('System') and '.' in d]
        
        if len(meaningful_deps) >= 2:
            return "- [Dependency Diagram](diagrams/dependency.mmd) - Class relationships and external dependencies"
        return ""
    
    def _generate_dependency_diagram_content(self) -> Optional[str]:
        """Generate class/dependency diagram content for separate file."""
        # Only generate if we have meaningful dependencies
        meaningful_deps = [d for d in self.dependencies 
                          if not d.startswith('System') and '.' in d]
        
        if len(meaningful_deps) < 2:
            return None
        
        class_name_safe = self._sanitize_mermaid_text(self.class_name, 40)
        diagram = "classDiagram\n"
        diagram += f"    class {class_name_safe} {{\n"
        
        # Add primary method if exists
        primary = next((m for m in self.methods if m.name in ['Execute', 'Run', 'Process']), None)
        if primary:
            method_safe = self._sanitize_mermaid_text(primary.name, 30)
            diagram += f"        +{method_safe}\n"
        
        diagram += "    }\n"
        
        # Add dependencies (sanitized)
        for dep in meaningful_deps[:4]:  # Limit to 4
            dep_class = self._sanitize_mermaid_text(dep.split('.')[-1], 30)
            diagram += f"    class {dep_class}\n"
            diagram += f"    {class_name_safe} --> {dep_class}\n"
        
        return diagram
    
    def _generate_dependency_diagram(self) -> str:
        """Legacy method - returns empty string as diagrams now in separate files."""
        return ""
    
    def _narrator_pass(self, spec: str) -> str:
        """
        Narrator agent: Enhance technical text for better readability.
        Makes content more verbose and presentable to teams.
        """
        # Pattern replacements for better readability
        enhancements = [
            # Make IF/THEN statements more readable
            (r'IF `([^`]+)`', r'**When** `\1` occurs'),
            (r'THEN Perform action', r'**Then** the system performs the following action'),
            (r'ELSE Continue processing', r'**Otherwise** processing continues normally'),
            
            # Enhance validation language
            (r'Input Parameters Validated', 'All input parameters are validated for correctness and completeness'),
            (r'Transaction Context Available', 'Transaction context is established and available for the operation'),
            
            # Make purpose statements more professional
            (r'operation for RA funding management', 'operation designed to manage Reimbursement Account (RA) funding processes'),
            
            # Enhance error messages
            (r'Throw Validation Error', 'The system raises a validation error and halts processing'),
            
            # Make business rule titles more descriptive
            (r'Rule (\d+):', r'Business Rule \1:'),
        ]
        
        enhanced_spec = spec
        for pattern, replacement in enhancements:
            enhanced_spec = re.sub(pattern, replacement, enhanced_spec)
        
        # Add contextual improvements to business rules
        enhanced_spec = self._enhance_business_rules_context(enhanced_spec)
        
        return enhanced_spec
    
    def _enhance_business_rules_context(self, spec: str) -> str:
        """Add context and verbosity to business rule descriptions."""
        lines = spec.split('\n')
        enhanced_lines = []
        
        for i, line in enumerate(lines):
            enhanced_lines.append(line)
            
            # Add context after business rule headers
            if line.startswith('### Business Rule') and i + 2 < len(lines):
                # Check if next line is the description
                if lines[i + 2].startswith('**Description:**'):
                    # Add explanatory note
                    enhanced_lines.append('')
                    enhanced_lines.append('*This rule governs the behavior of the system when specific conditions are met during execution.*')
        
        return '\n'.join(enhanced_lines)
    
    def generate_all(self):
        """Generate all specification documents."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\n📝 Generating specifications in {self.output_dir}...")
        
        # Generate business spec
        business_spec = self.generate_business_spec()
        
        # Apply narrator agent to improve readability
        if self.narrator_enabled:
            print(f"   🎭 Narrator agent enhancing readability...")
            business_spec = self._narrator_pass(business_spec)
        
        # Save business spec
        spec_path = self.output_dir / 'business-spec.md'
        spec_path.write_text(business_spec, encoding='utf-8')
        print(f"   ✅ business-spec.md ({len(business_spec)} chars)")
        
        # Generate separate diagram files
        self._generate_diagram_files()
        
        # Validate Mermaid diagrams in separate files
        print(f"   🔍 Validating Mermaid diagrams...")
        validation_result = self._validate_diagram_files()
        
        if not validation_result['is_valid']:
            print(f"   ⚠️  Mermaid validation found {len(validation_result['errors'])} errors")
            for error in validation_result['errors'][:3]:  # Show first 3 errors
                print(f"      - Line {error['line_number']}: {error['message']}")
            if len(validation_result['errors']) > 3:
                print(f"      ... and {len(validation_result['errors']) - 3} more errors")
        else:
            print(f"   ✅ All Mermaid diagrams validated successfully")
        
        # Generate traceability matrix
        matrix = self.generate_traceability_matrix()
        (self.output_dir / 'traceability-matrix.md').write_text(matrix, encoding='utf-8')
        print(f"   ✅ traceability-matrix.md ({len(matrix)} chars)")
        
        # Generate OpenAPI specification
        if self.openapi_enabled and self.openapi_endpoints:
            print(f"   🔧 Generating OpenAPI specification...")
            openapi_spec = self.generate_openapi_spec()
            (self.output_dir / 'openapi.yaml').write_text(openapi_spec, encoding='utf-8')
            print(f"   ✅ openapi.yaml ({len(openapi_spec)} chars)")
            
            # Generate OpenAPI JSON version
            openapi_json = self.generate_openapi_json()
            (self.output_dir / 'openapi.json').write_text(openapi_json, encoding='utf-8')
            print(f"   ✅ openapi.json ({len(openapi_json)} chars)")
        
        # PRE-PUBLISH LINT CHECK
        print(f"\n🔬 Running pre-publish lint checks...")
        lint_result = self._run_lint_checks()
        
        if lint_result['passed']:
            print(f"   ✅ All lint checks passed ({lint_result['checks_run']} checks)")
        else:
            print(f"   ⚠️  Lint checks found {len(lint_result['failures'])} issues:")
            for failure in lint_result['failures']:
                print(f"      - {failure}")
        
        print(f"\n🎉 Specification generation complete!")
        print(f"   Output: {self.output_dir}")
        
        # Return combined validation and lint results
        return {
            **validation_result,
            'lint_result': lint_result
        }
    
    def _validate_diagram_files(self) -> dict:
        """
        Validate Mermaid diagrams in separate .mmd files.
        
        Returns:
            {
                'is_valid': bool,
                'errors': List[dict],
                'warnings': List[str],
                'diagrams_found': int
            }
        """
        try:
            diagrams_dir = self.output_dir / 'diagrams'
            if not diagrams_dir.exists():
                return {
                    'is_valid': True,
                    'errors': [],
                    'warnings': ['No diagrams directory found'],
                    'diagrams_found': 0
                }
            
            # Import validator
            import importlib.util
            validator_path = Path(__file__).parent.parent / 'validators' / 'mermaid_diagram_validator.py'
            
            if not validator_path.exists():
                return {
                    'is_valid': True,
                    'errors': [],
                    'warnings': ['Validator file not found'],
                    'diagrams_found': 0
                }
            
            spec = importlib.util.spec_from_file_location("mermaid_validator", validator_path)
            validator_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(validator_module)
            
            # Validate each .mmd file
            all_errors = []
            all_warnings = []
            diagrams_count = 0
            
            for mmd_file in diagrams_dir.glob('*.mmd'):
                # Create a temporary markdown wrapper for validator
                temp_content = f"```mermaid\n{mmd_file.read_text(encoding='utf-8')}\n```"
                temp_md = diagrams_dir / f"_temp_{mmd_file.stem}.md"
                temp_md.write_text(temp_content, encoding='utf-8')
                
                try:
                    result = validator_module.validate_spec_file(temp_md)
                    diagrams_count += result.diagrams_found
                    
                    for err in result.errors:
                        all_errors.append({
                            'file': mmd_file.name,
                            'diagram_type': err.diagram_type,
                            'line_number': err.line_number,
                            'error_type': err.error_type,
                            'message': err.message,
                            'context': err.context
                        })
                    
                    all_warnings.extend([f"{mmd_file.name}: {w}" for w in result.warnings])
                finally:
                    # Clean up temp file
                    if temp_md.exists():
                        temp_md.unlink()
            
            return {
                'is_valid': len(all_errors) == 0,
                'errors': all_errors,
                'warnings': all_warnings,
                'diagrams_found': diagrams_count
            }
        except Exception as e:
            print(f"   ⚠️  Mermaid validation error: {str(e)}")
            return {
                'is_valid': True,
                'errors': [],
                'warnings': [f'Validation failed: {str(e)}'],
                'diagrams_found': 0
            }
    
    def _run_lint_checks(self) -> dict:
        """
        Run comprehensive pre-publish lint checks on all generated files.
        
        Returns:
            {
                'passed': bool,
                'checks_run': int,
                'failures': List[str]
            }
        """
        failures = []
        checks_run = 0
        
        try:
            # Check 1: Verify all expected files exist
            checks_run += 1
            expected_files = ['business-spec.md', 'traceability-matrix.md']
            if self.openapi_enabled:
                expected_files.extend(['openapi.yaml', 'openapi.json'])
            
            for filename in expected_files:
                if not (self.output_dir / filename).exists():
                    failures.append(f"Missing required file: {filename}")
            
            # Check 2: Verify diagrams folder exists and has content
            checks_run += 1
            diagrams_dir = self.output_dir / 'diagrams'
            if not diagrams_dir.exists():
                failures.append("diagrams/ folder not created")
            elif len(list(diagrams_dir.glob('*.mmd'))) == 0:
                failures.append("diagrams/ folder is empty")
            
            # Check 3: Validate each .mmd file has valid Mermaid syntax
            if diagrams_dir.exists():
                for mmd_file in diagrams_dir.glob('*.mmd'):
                    checks_run += 1
                    content = mmd_file.read_text(encoding='utf-8')
                    
                    # Check for diagram type declaration
                    valid_types = ['flowchart', 'sequenceDiagram', 'classDiagram', 'graph']
                    if not any(diagram_type in content for diagram_type in valid_types):
                        failures.append(f"{mmd_file.name}: No valid diagram type found")
                    
                    # Check for markdown code fences (should NOT be present)
                    if '```' in content:
                        failures.append(f"{mmd_file.name}: Contains markdown code fences (should be raw Mermaid only)")
                    
                    # Check file is not empty
                    if len(content.strip()) == 0:
                        failures.append(f"{mmd_file.name}: File is empty")
                    
                    # Check for common syntax errors
                    if content.count('(') != content.count(')'):
                        failures.append(f"{mmd_file.name}: Unmatched parentheses")
                    if content.count('[') != content.count(']'):
                        failures.append(f"{mmd_file.name}: Unmatched square brackets")
                    if content.count('{') != content.count('}'):
                        failures.append(f"{mmd_file.name}: Unmatched curly braces")
            
            # Check 4: Validate business-spec.md references diagram files correctly
            checks_run += 1
            spec_path = self.output_dir / 'business-spec.md'
            if spec_path.exists():
                spec_content = spec_path.read_text(encoding='utf-8')
                
                # Check for diagram links
                if 'diagrams/flowchart.mmd' not in spec_content and 'diagrams/sequence.mmd' not in spec_content:
                    failures.append("business-spec.md: Missing diagram file references")
                
                # Check that diagrams are NOT embedded (no ```mermaid blocks followed by diagram content)
                import re
                mermaid_blocks = re.findall(r'```\s*mermaid\s*\n', spec_content, re.IGNORECASE)
                if mermaid_blocks:
                    failures.append("business-spec.md: Contains embedded Mermaid diagrams (should use links to .mmd files)")
            
            # Check 5: Validate OpenAPI files if enabled
            if self.openapi_enabled:
                checks_run += 1
                yaml_path = self.output_dir / 'openapi.yaml'
                json_path = self.output_dir / 'openapi.json'
                
                if yaml_path.exists():
                    yaml_content = yaml_path.read_text(encoding='utf-8')
                    if 'openapi: 3.' not in yaml_content:
                        failures.append("openapi.yaml: Missing OpenAPI version declaration")
                
                if json_path.exists():
                    json_content = json_path.read_text(encoding='utf-8')
                    if '"openapi":' not in json_content:
                        failures.append("openapi.json: Missing OpenAPI version declaration")
            
            # Check 6: Verify traceability matrix has content
            checks_run += 1
            matrix_path = self.output_dir / 'traceability-matrix.md'
            if matrix_path.exists():
                matrix_content = matrix_path.read_text(encoding='utf-8')
                if len(matrix_content.strip()) < 100:
                    failures.append("traceability-matrix.md: File appears to be empty or incomplete")
            
            return {
                'passed': len(failures) == 0,
                'checks_run': checks_run,
                'failures': failures
            }
            
        except Exception as e:
            return {
                'passed': False,
                'checks_run': checks_run,
                'failures': [f"Lint check error: {str(e)}"]
            }
    
    def _validate_mermaid_diagrams(self, md_file_path: Path) -> dict:
        """
        Validate Mermaid diagrams in generated markdown file.
        
        Returns:
            {
                'is_valid': bool,
                'errors': List[dict],
                'warnings': List[str],
                'diagrams_found': int
            }
        """
        try:
            # Import validator from same package
            import importlib.util
            validator_path = Path(__file__).parent.parent / 'validators' / 'mermaid_diagram_validator.py'
            
            if not validator_path.exists():
                return {
                    'is_valid': True,
                    'errors': [],
                    'warnings': ['Validator file not found'],
                    'diagrams_found': 0
                }
            
            spec = importlib.util.spec_from_file_location("mermaid_validator", validator_path)
            validator_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(validator_module)
            
            result = validator_module.validate_spec_file(md_file_path)
            
            return {
                'is_valid': result.is_valid,
                'errors': [
                    {
                        'diagram_type': err.diagram_type,
                        'line_number': err.line_number,
                        'error_type': err.error_type,
                        'message': err.message,
                        'context': err.context
                    }
                    for err in result.errors
                ],
                'warnings': result.warnings,
                'diagrams_found': result.diagrams_found
            }
        except Exception as e:
            print(f"   ⚠️  Mermaid validation error: {str(e)}")
            return {
                'is_valid': True,
                'errors': [],
                'warnings': [f'Validation failed: {str(e)}'],
                'diagrams_found': 0
            }


def main():
    """Example usage."""
    import sys
    
    if len(sys.argv) < 3:
        print("Usage: python legacy_spec_generator.py <legacy_file> <output_dir>")
        sys.exit(1)
    
    legacy_file = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    
    if not legacy_file.exists():
        print(f"❌ Error: File not found: {legacy_file}")
        sys.exit(1)
    
    generator = LegacySpecGenerator(legacy_file, output_dir)
    generator.analyze()
    generator.generate_all()


if __name__ == '__main__':
    main()
