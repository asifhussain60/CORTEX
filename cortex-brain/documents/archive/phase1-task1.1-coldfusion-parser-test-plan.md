# Phase 1 Task 1.1: ColdFusion Parser Development - Test Plan

**Date:** December 8, 2025  
**Phase:** 1 - Multi-Language Code Intelligence Foundation  
**Task:** 1.1 - ColdFusion Parser Development  
**Status:** Ready for RED Phase

---

## TDD Workflow: RED → GREEN → REFACTOR

### RED Phase: Write Failing Tests

**Test Files Created:**
1. `tests/intelligence/parsers/test_coldfusion_parser_red.py` - Tag-based syntax tests (MUST FAIL)
2. `tests/intelligence/analyzers/test_coldfusion_analyzer_red.py` - CFScript syntax tests (MUST FAIL)

**Test Coverage:**
- Parse .cfm files with tag-based syntax (10 samples)
- Parse .cfc files with CFScript syntax (10 samples)
- Extract component metadata (displayname, hint, returntype)
- Extract function definitions (name, access, parameters, returntype)
- Handle ColdFusion 9 vs 2018 syntax variations
- Error handling (malformed files, syntax errors)

**Test Fixtures:**
- Location: `tests/fixtures/coldfusion/`
- Files: 20 real samples from V5.ColdFusion repository
- Mix: Fusebox framework files, API components, business logic

---

## Test File 1: Tag-Based Syntax Parser

**File:** `tests/intelligence/parsers/test_coldfusion_parser_red.py`

**Scenarios:**
1. Parse basic .cfm file with <cfset>, <cfif>, <cfloop>
2. Extract <cfcomponent> definitions
3. Extract <cffunction> with parameters
4. Parse <cfquery> blocks
5. Handle nested tags (cfloop inside cfif)
6. Parse Application.cfm (application scope)
7. Handle fusebox.xml.cfm (XML-style CFM)
8. Error: malformed tag (missing closing tag)
9. Error: unknown tag (graceful degradation)
10. Performance: <100ms for files <1000 LOC

**Expected Results (RED Phase):**
- All 10 tests FAIL with NotImplementedError or ImportError
- No src/intelligence/parsers/coldfusion_parser.py exists yet

---

## Test File 2: CFScript Analyzer

**File:** `tests/intelligence/analyzers/test_coldfusion_analyzer_red.py`

**Scenarios:**
1. Parse component definition with metadata
2. Extract public function with typed parameters
3. Extract private function (access="private")
4. Parse function with multiple return points
5. Extract function hints (documentation)
6. Handle cfscript mixed with tags
7. Parse init() constructor pattern
8. Parse variable declarations (var, local, arguments)
9. Error: syntax error in cfscript
10. Performance: <100ms for files <1000 LOC

**Expected Results (RED Phase):**
- All 10 tests FAIL with NotImplementedError or ImportError
- No src/intelligence/analyzers/coldfusion_analyzer.py exists yet

---

## Sample Test Code (RED Phase)

```python
import pytest
from pathlib import Path

# This import WILL FAIL - module doesn't exist yet (RED phase)
from src.intelligence.parsers.coldfusion_parser import ColdFusionParser

class TestColdFusionParserTagSyntax:
    """Tag-based ColdFusion syntax parser tests"""
    
    @pytest.fixture
    def parser(self):
        return ColdFusionParser()
    
    @pytest.fixture
    def sample_cfm_file(self):
        return Path("tests/fixtures/coldfusion/Application.cfm")
    
    def test_parse_cfm_file_returns_structure(self, parser, sample_cfm_file):
        """Test that parser returns structured output for .cfm file"""
        result = parser.parse_file(sample_cfm_file)
        
        assert result is not None
        assert 'language' in result
        assert result['language'] == 'coldfusion'
        assert 'file_path' in result
        assert 'components' in result or 'functions' in result
    
    def test_extract_cfcomponent_metadata(self, parser):
        """Test extraction of <cfcomponent> metadata"""
        code = '''
        <cfcomponent displayname="Employee" hint="Manages employee data" output="false">
            <cffunction name="init" access="public" returntype="Employee">
                <cfreturn this />
            </cffunction>
        </cfcomponent>
        '''
        
        result = parser.parse_code(code)
        
        assert len(result['components']) == 1
        component = result['components'][0]
        assert component['name'] == 'Employee'
        assert component['hint'] == 'Manages employee data'
        assert component['output'] == False
        assert len(component['functions']) == 1
    
    def test_extract_cffunction_parameters(self, parser):
        """Test extraction of <cffunction> parameters"""
        code = '''
        <cffunction name="getEmployeeByID" access="public" returntype="query">
            <cfargument name="employeeID" type="numeric" required="true" />
            <cfargument name="includeDetails" type="boolean" required="false" default="false" />
            
            <cfquery name="qryEmployee" datasource="myDB">
                SELECT * FROM employees WHERE id = <cfqueryparam value="#arguments.employeeID#" />
            </cfquery>
            
            <cfreturn qryEmployee />
        </cffunction>
        '''
        
        result = parser.parse_code(code)
        
        func = result['functions'][0]
        assert func['name'] == 'getEmployeeByID'
        assert func['access'] == 'public'
        assert func['returntype'] == 'query'
        assert len(func['parameters']) == 2
        assert func['parameters'][0]['name'] == 'employeeID'
        assert func['parameters'][0]['type'] == 'numeric'
        assert func['parameters'][0]['required'] == True
    
    def test_performance_large_file(self, parser):
        """Test parser performance on large file (fusebox40.transformer.cfmx.cfm - 44.9 KB)"""
        large_file = Path("tests/fixtures/coldfusion/fusebox40.transformer.cfmx.cfm")
        
        import time
        start = time.time()
        result = parser.parse_file(large_file)
        duration = time.time() - start
        
        assert result is not None
        assert duration < 0.1  # <100ms requirement
    
    # Additional 6 tests for nested tags, Application.cfm, XML-style, errors, etc.
```

---

## GREEN Phase: Minimal Implementation

**Files to Create:**
1. `src/intelligence/parsers/coldfusion_parser.py` - Main parser
2. `src/intelligence/analyzers/coldfusion_analyzer.py` - Analyzer wrapper
3. Update `src/intelligence/parsers/parser_registry.py` - Register ColdFusion parser

**Implementation Strategy:**
- Start with regex-based tokenizer for tag extraction
- Use BeautifulSoup-like approach for XML parsing
- Handle CFScript blocks separately (JavaScript-like syntax)
- Minimal viable implementation to pass tests

---

## REFACTOR Phase: Optimization

**Improvements:**
- Extract tokenizer to separate class
- Add caching for parsed AST structures
- Improve error messages
- Add logging for debugging
- Optimize regex patterns for performance
- Add support for ColdFusion 2018 syntax features

---

## Git Checkpoints

**Commit Strategy:**
1. RED Phase: `git commit -m "RED: ColdFusion parser tests (20 failing tests)"`
2. GREEN Phase: `git commit -m "GREEN: ColdFusion parser minimal implementation (all tests pass)"`
3. REFACTOR Phase: `git commit -m "REFACTOR: ColdFusion parser optimization (performance + clarity)"`

---

## Success Criteria

**RED Phase Complete:**
- ✅ 20 test cases written and failing
- ✅ Test fixtures in place (20 ColdFusion files)
- ✅ Git checkpoint: RED phase commit

**GREEN Phase Complete:**
- ✅ All 20 tests passing
- ✅ ColdFusion parser handles .cfm and .cfc files
- ✅ Extracts components, functions, parameters correctly
- ✅ Performance: <100ms for files <1000 LOC
- ✅ Git checkpoint: GREEN phase commit

**REFACTOR Phase Complete:**
- ✅ Code is clean, readable, maintainable
- ✅ No duplication or code smells
- ✅ Tests still passing after refactor
- ✅ Performance optimized (caching, efficient regex)
- ✅ Git checkpoint: REFACTOR phase commit

---

## Next Steps After Task 1.1

1. Task 1.2: Enhanced AST Docstring Extractor (Multi-Language)
2. Task 1.3: Business Domain Inference Engine
3. Phase 2: Executive Summary Intelligence
4. Phase 3: Onboarding Automation

---

**Test Plan Status:** ✅ READY  
**Test Environment:** ✅ SET UP (20 sample files extracted)  
**Git Checkpoint:** ⏳ Ready for RED phase commit  
**Estimated Duration:** 12 hours (4h RED + 6h GREEN + 2h REFACTOR)
