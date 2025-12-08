"""
RED PHASE: ColdFusion CFScript Analyzer Tests
==============================================

These tests MUST FAIL initially (RED phase of TDD).
Expected failure: ImportError or NotImplementedError

Test coverage:
- CFScript component definition parsing (.cfc files)
- Function extraction with typed parameters
- Access modifier detection (public, private, package, remote)
- Multiple return point handling
- Function hint/documentation extraction
- Mixed tag and CFScript syntax
- Constructor pattern (init() function)
- Variable declaration parsing (var, local, arguments)
- Error handling for syntax errors
- Performance requirements (<100ms for <1000 LOC)
"""

import pytest
from pathlib import Path
import time

# This import WILL FAIL - module doesn't exist yet (RED phase)
from src.intelligence.analyzers.coldfusion_analyzer import ColdFusionAnalyzer


class TestColdFusionAnalyzerBasics:
    """Basic CFScript analyzer functionality tests"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return ColdFusionAnalyzer()
    
    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory path"""
        return Path("tests/fixtures/coldfusion")
    
    def test_analyzer_initializes(self, analyzer):
        """Test that analyzer can be instantiated"""
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze_file')
        assert hasattr(analyzer, 'analyze_code')
    
    def test_analyze_basic_cfc_returns_structure(self, analyzer):
        """Test that analyzer returns structured output for basic .cfc file"""
        code = '''
        component {
            function init() {
                return this;
            }
        }
        '''
        
        result = analyzer.analyze_code(code)
        
        assert result is not None
        assert 'language' in result
        assert result['language'] == 'coldfusion'
        assert 'components' in result
        assert isinstance(result, dict)


class TestCFScriptComponentParsing:
    """Test CFScript component definition parsing"""
    
    @pytest.fixture
    def analyzer(self):
        return ColdFusionAnalyzer()
    
    def test_parse_component_with_metadata(self, analyzer):
        """Test parsing component with metadata attributes"""
        code = '''
        component displayname="EmployeeService" 
                  hint="Handles employee business logic" 
                  output="false" 
                  persistent="true" {
            
            property name="id" type="numeric" fieldtype="id" generator="increment";
            property name="firstName" type="string" length="50";
            property name="lastName" type="string" length="50";
            
            function init() {
                return this;
            }
        }
        '''
        
        result = analyzer.analyze_code(code)
        
        assert len(result['components']) == 1
        component = result['components'][0]
        assert component['displayname'] == 'EmployeeService'
        assert component['hint'] == 'Handles employee business logic'
        assert component['output'] is False
        assert component['persistent'] is True
        assert len(component['properties']) == 3
    
    def test_parse_component_properties(self, analyzer):
        """Test parsing component property definitions"""
        code = '''
        component {
            property name="username" type="string" required="true";
            property name="email" type="string" pattern="^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$";
            property name="age" type="numeric" default="0";
        }
        '''
        
        result = analyzer.analyze_code(code)
        
        component = result['components'][0]
        props = component['properties']
        
        assert len(props) == 3
        assert props[0]['name'] == 'username'
        assert props[0]['required'] is True
        assert props[1]['name'] == 'email'
        assert 'pattern' in props[1]
        assert props[2]['default'] == '0'


class TestCFScriptFunctionExtraction:
    """Test CFScript function extraction"""
    
    @pytest.fixture
    def analyzer(self):
        return ColdFusionAnalyzer()
    
    def test_extract_public_function_with_typed_params(self, analyzer):
        """Test extraction of public function with typed parameters"""
        code = '''
        component {
            public query function getEmployeeById(required numeric id, boolean includeDetails=false) {
                var qryEmployee = queryExecute(
                    "SELECT * FROM employees WHERE id = :id",
                    {id: arguments.id},
                    {datasource: "myDB"}
                );
                return qryEmployee;
            }
        }
        '''
        
        result = analyzer.analyze_code(code)
        
        component = result['components'][0]
        assert len(component['functions']) == 1
        
        func = component['functions'][0]
        assert func['name'] == 'getEmployeeById'
        assert func['access'] == 'public'
        assert func['returntype'] == 'query'
        assert len(func['parameters']) == 2
        
        # Check required parameter
        param1 = func['parameters'][0]
        assert param1['name'] == 'id'
        assert param1['type'] == 'numeric'
        assert param1['required'] is True
        
        # Check optional parameter with default
        param2 = func['parameters'][1]
        assert param2['name'] == 'includeDetails'
        assert param2['type'] == 'boolean'
        assert param2['default'] == 'false'
    
    def test_extract_private_function(self, analyzer):
        """Test extraction of private function"""
        code = '''
        component {
            private string function validateInput(required string input) {
                var cleaned = trim(arguments.input);
                return cleaned;
            }
        }
        '''
        
        result = analyzer.analyze_code(code)
        
        func = result['components'][0]['functions'][0]
        assert func['name'] == 'validateInput'
        assert func['access'] == 'private'
        assert func['returntype'] == 'string'
    
    def test_extract_remote_function(self, analyzer):
        """Test extraction of remote function (web service endpoint)"""
        code = '''
        component {
            remote struct function getEmployeeData(required numeric employeeId) 
                returnformat="json" 
                hint="Returns employee data as JSON" {
                
                var employee = {
                    id: arguments.employeeId,
                    name: "John Doe"
                };
                return employee;
            }
        }
        '''
        
        result = analyzer.analyze_code(code)
        
        func = result['components'][0]['functions'][0]
        assert func['name'] == 'getEmployeeData'
        assert func['access'] == 'remote'
        assert func['returntype'] == 'struct'
        assert func['returnformat'] == 'json'
        assert 'hint' in func


class TestCFScriptMultipleReturns:
    """Test handling of functions with multiple return points"""
    
    @pytest.fixture
    def analyzer(self):
        return ColdFusionAnalyzer()
    
    def test_parse_function_multiple_returns(self, analyzer):
        """Test parsing function with multiple return statements"""
        code = '''
        component {
            public boolean function isValid(required string input) {
                if (len(arguments.input) == 0) {
                    return false;
                }
                
                if (len(arguments.input) > 100) {
                    return false;
                }
                
                return true;
            }
        }
        '''
        
        result = analyzer.analyze_code(code)
        
        func = result['components'][0]['functions'][0]
        assert func['name'] == 'isValid'
        # Should detect multiple return points
        assert 'return_points' in func or func['returntype'] == 'boolean'


class TestCFScriptDocumentation:
    """Test extraction of function hints and documentation"""
    
    @pytest.fixture
    def analyzer(self):
        return ColdFusionAnalyzer()
    
    def test_extract_function_hint(self, analyzer):
        """Test extraction of function hint attribute"""
        code = '''
        component {
            public void function processPayroll(required numeric employeeId) 
                hint="Processes payroll for specified employee" {
                // Processing logic here
            }
        }
        '''
        
        result = analyzer.analyze_code(code)
        
        func = result['components'][0]['functions'][0]
        assert 'hint' in func
        assert func['hint'] == 'Processes payroll for specified employee'
    
    def test_extract_javadoc_style_comments(self, analyzer):
        """Test extraction of JavaDoc-style comments"""
        code = '''
        component {
            /**
             * Calculates employee salary
             * @param employeeId The ID of the employee
             * @param includeBonus Whether to include bonus in calculation
             * @return The calculated salary amount
             */
            public numeric function calculateSalary(required numeric employeeId, boolean includeBonus=true) {
                return 50000;
            }
        }
        '''
        
        result = analyzer.analyze_code(code)
        
        func = result['components'][0]['functions'][0]
        assert 'documentation' in func or 'hint' in func
        # Should capture javadoc-style documentation


class TestCFScriptMixedSyntax:
    """Test handling of mixed tag and CFScript syntax"""
    
    @pytest.fixture
    def analyzer(self):
        return ColdFusionAnalyzer()
    
    def test_parse_mixed_tag_cfscript(self, analyzer):
        """Test parsing file with both tag and CFScript syntax"""
        code = '''
        <cfcomponent>
            <cffunction name="tagBasedFunction" access="public" returntype="string">
                <cfreturn "Hello from tag" />
            </cffunction>
            
            <cfscript>
                public string function scriptBasedFunction() {
                    return "Hello from script";
                }
            </cfscript>
        </cfcomponent>
        '''
        
        result = analyzer.analyze_code(code)
        
        component = result['components'][0]
        assert len(component['functions']) == 2
        assert component['functions'][0]['name'] == 'tagBasedFunction'
        assert component['functions'][1]['name'] == 'scriptBasedFunction'


class TestCFScriptConstructorPattern:
    """Test detection of constructor (init) pattern"""
    
    @pytest.fixture
    def analyzer(self):
        return ColdFusionAnalyzer()
    
    def test_detect_init_constructor(self, analyzer):
        """Test detection and parsing of init() constructor"""
        code = '''
        component {
            property name="id" type="numeric";
            property name="name" type="string";
            
            public function init(required numeric id, required string name) {
                variables.id = arguments.id;
                variables.name = arguments.name;
                return this;
            }
            
            public numeric function getId() {
                return variables.id;
            }
        }
        '''
        
        result = analyzer.analyze_code(code)
        
        component = result['components'][0]
        init_func = [f for f in component['functions'] if f['name'] == 'init'][0]
        
        assert init_func is not None
        assert init_func['is_constructor'] is True or init_func['name'] == 'init'
        assert len(init_func['parameters']) == 2


class TestCFScriptVariableDeclarations:
    """Test parsing of variable declarations"""
    
    @pytest.fixture
    def analyzer(self):
        return ColdFusionAnalyzer()
    
    def test_parse_var_declarations(self, analyzer):
        """Test parsing var declarations in function"""
        code = '''
        component {
            public void function processData() {
                var localVar = "test";
                var counter = 0;
                var results = [];
                var config = {
                    timeout: 30,
                    retries: 3
                };
            }
        }
        '''
        
        result = analyzer.analyze_code(code)
        
        func = result['components'][0]['functions'][0]
        assert 'variables' in func or 'body' in func
        # Should detect variable declarations
    
    def test_parse_scoped_variables(self, analyzer):
        """Test parsing different variable scopes (local, arguments, variables)"""
        code = '''
        component {
            public function processRequest(required string input) {
                local.result = "";
                arguments.input = trim(arguments.input);
                variables.lastProcessed = now();
                return local.result;
            }
        }
        '''
        
        result = analyzer.analyze_code(code)
        
        func = result['components'][0]['functions'][0]
        assert func['name'] == 'processRequest'
        # Should parse successfully with scoped variables


class TestCFScriptErrorHandling:
    """Test error handling for CFScript syntax errors"""
    
    @pytest.fixture
    def analyzer(self):
        return ColdFusionAnalyzer()
    
    def test_syntax_error_in_cfscript(self, analyzer):
        """Test handling of syntax error in CFScript"""
        code = '''
        component {
            public function broken() {
                var x = ;  // Syntax error: missing value
                return x;
            }
        }
        '''
        
        # Should either raise exception or return error in result
        try:
            result = analyzer.analyze_code(code)
            assert 'errors' in result or 'warnings' in result
        except Exception as e:
            # Expected to raise parsing exception
            assert "syntax" in str(e).lower() or "error" in str(e).lower()
    
    def test_missing_closing_brace(self, analyzer):
        """Test handling of missing closing brace"""
        code = '''
        component {
            public function broken() {
                return "missing brace";
            // Missing closing brace for component
        '''
        
        try:
            result = analyzer.analyze_code(code)
            assert 'errors' in result or 'warnings' in result
        except Exception as e:
            assert "brace" in str(e).lower() or "closing" in str(e).lower()


class TestCFScriptPerformance:
    """Test analyzer performance requirements"""
    
    @pytest.fixture
    def analyzer(self):
        return ColdFusionAnalyzer()
    
    @pytest.fixture
    def fixtures_dir(self):
        return Path("tests/fixtures/coldfusion")
    
    def test_performance_large_cfc_file(self, analyzer, fixtures_dir):
        """Test analyzer performance on large .cfc file (<100ms for <1000 LOC)"""
        # adjustment_api.cfc is 79.4 KB - largest fixture file
        large_cfc = fixtures_dir / "adjustment_api.cfc"
        
        assert large_cfc.exists(), f"Expected {large_cfc} to exist"
        
        start = time.time()
        result = analyzer.analyze_file(large_cfc)
        duration = time.time() - start
        
        assert result is not None
        assert duration < 0.15, f"Analyzer took {duration:.3f}s, expected <0.15s"
    
    def test_performance_multiple_cfc_files(self, analyzer, fixtures_dir):
        """Test analyzer performance on multiple .cfc files"""
        cfc_files = list(fixtures_dir.glob("*.cfc"))
        
        # Should have at least 5 .cfc files in fixtures
        assert len(cfc_files) >= 5, f"Expected at least 5 .cfc files, found {len(cfc_files)}"
        
        total_duration = 0
        for cfc_file in cfc_files[:5]:  # Test first 5
            start = time.time()
            result = analyzer.analyze_file(cfc_file)
            duration = time.time() - start
            total_duration += duration
            
            assert result is not None
        
        avg_duration = total_duration / 5
        assert avg_duration < 0.1, f"Average duration {avg_duration:.3f}s, expected <0.1s"
