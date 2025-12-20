"""
RED PHASE: ColdFusion Tag-Based Parser Tests
============================================

These tests MUST FAIL initially (RED phase of TDD).
Expected failure: ImportError or NotImplementedError

Test coverage:
- Basic .cfm file parsing with tag-based syntax
- Component extraction from <cfcomponent> tags
- Function extraction from <cffunction> tags
- Parameter extraction from <cfargument> tags
- Nested tag handling (cfloop, cfif, cfswitch)
- Application.cfm parsing (application scope)
- Fusebox framework XML-style CFM parsing
- Error handling (malformed tags, syntax errors)
- Performance requirements (<100ms for <1000 LOC)
"""

import pytest
from pathlib import Path
import time

# This import WILL FAIL - module doesn't exist yet (RED phase)
from src.intelligence.parsers.coldfusion_parser import ColdFusionParser


class TestColdFusionParserBasics:
    """Basic ColdFusion tag-based syntax parser tests"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return ColdFusionParser()
    
    @pytest.fixture
    def fixtures_dir(self):
        """Get fixtures directory path"""
        return Path("tests/fixtures/coldfusion")
    
    def test_parser_initializes(self, parser):
        """Test that parser can be instantiated"""
        assert parser is not None
        assert hasattr(parser, 'parse_file')
        assert hasattr(parser, 'parse_code')
    
    def test_parse_basic_cfm_returns_structure(self, parser):
        """Test that parser returns structured output for basic .cfm file"""
        code = '''
        <cfset userName = "John Doe">
        <cfif userName NEQ "">
            <cfoutput>#userName#</cfoutput>
        </cfif>
        '''
        
        result = parser.parse_code(code)
        
        assert result is not None
        assert 'language' in result
        assert result['language'] == 'coldfusion'
        assert 'tags' in result or 'statements' in result
        assert isinstance(result, dict)


class TestColdFusionComponentExtraction:
    """Test extraction of ColdFusion components"""
    
    @pytest.fixture
    def parser(self):
        return ColdFusionParser()
    
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
        
        assert 'components' in result
        assert len(result['components']) == 1
        component = result['components'][0]
        assert component['name'] == 'Employee'
        assert component['hint'] == 'Manages employee data'
        assert component['output'] is False
        assert 'functions' in component
        assert len(component['functions']) == 1
    
    def test_extract_nested_components(self, parser):
        """Test extraction of nested component definitions"""
        code = '''
        <cfcomponent>
            <cfproperty name="id" type="numeric" />
            <cfproperty name="name" type="string" />
            
            <cffunction name="getId" access="public" returntype="numeric">
                <cfreturn variables.id />
            </cffunction>
        </cfcomponent>
        '''
        
        result = parser.parse_code(code)
        
        assert len(result['components']) == 1
        component = result['components'][0]
        assert 'properties' in component
        assert len(component['properties']) == 2
        assert component['properties'][0]['name'] == 'id'
        assert component['properties'][0]['type'] == 'numeric'


class TestColdFusionFunctionExtraction:
    """Test extraction of ColdFusion functions"""
    
    @pytest.fixture
    def parser(self):
        return ColdFusionParser()
    
    def test_extract_cffunction_basic(self, parser):
        """Test extraction of basic <cffunction>"""
        code = '''
        <cffunction name="sayHello" access="public" returntype="string">
            <cfreturn "Hello World" />
        </cffunction>
        '''
        
        result = parser.parse_code(code)
        
        assert 'functions' in result
        assert len(result['functions']) == 1
        func = result['functions'][0]
        assert func['name'] == 'sayHello'
        assert func['access'] == 'public'
        assert func['returntype'] == 'string'
    
    def test_extract_cffunction_parameters(self, parser):
        """Test extraction of <cffunction> with multiple parameters"""
        code = '''
        <cffunction name="getEmployeeByID" access="public" returntype="query">
            <cfargument name="employeeID" type="numeric" required="true" />
            <cfargument name="includeDetails" type="boolean" required="false" default="false" />
            <cfargument name="departmentCode" type="string" required="false" default="" />
            
            <cfquery name="qryEmployee" datasource="myDB">
                SELECT * FROM employees 
                WHERE id = <cfqueryparam value="#arguments.employeeID#" cfsqltype="cf_sql_integer" />
            </cfquery>
            
            <cfreturn qryEmployee />
        </cffunction>
        '''
        
        result = parser.parse_code(code)
        
        func = result['functions'][0]
        assert func['name'] == 'getEmployeeByID'
        assert len(func['parameters']) == 3
        
        # Check first parameter
        param1 = func['parameters'][0]
        assert param1['name'] == 'employeeID'
        assert param1['type'] == 'numeric'
        assert param1['required'] is True
        
        # Check optional parameter with default
        param2 = func['parameters'][1]
        assert param2['name'] == 'includeDetails'
        assert param2['required'] is False
        assert param2['default'] == 'false'
    
    def test_extract_multiple_functions(self, parser):
        """Test extraction of multiple functions from same file"""
        code = '''
        <cffunction name="function1" access="public" returntype="void">
        </cffunction>
        
        <cffunction name="function2" access="private" returntype="string">
            <cfargument name="input" type="string" required="true" />
        </cffunction>
        
        <cffunction name="function3" access="package" returntype="numeric">
        </cffunction>
        '''
        
        result = parser.parse_code(code)
        
        assert len(result['functions']) == 3
        assert result['functions'][0]['name'] == 'function1'
        assert result['functions'][1]['name'] == 'function2'
        assert result['functions'][1]['access'] == 'private'
        assert result['functions'][2]['name'] == 'function3'
        assert result['functions'][2]['access'] == 'package'


class TestColdFusionNestedTags:
    """Test handling of nested ColdFusion tags"""
    
    @pytest.fixture
    def parser(self):
        return ColdFusionParser()
    
    def test_parse_nested_cfloop_cfif(self, parser):
        """Test parsing nested cfloop and cfif tags"""
        code = '''
        <cfloop from="1" to="10" index="i">
            <cfif i MOD 2 EQ 0>
                <cfoutput>Even: #i#</cfoutput>
            <cfelse>
                <cfoutput>Odd: #i#</cfoutput>
            </cfif>
        </cfloop>
        '''
        
        result = parser.parse_code(code)
        
        assert result is not None
        # Should successfully parse nested structures
        assert 'tags' in result or 'statements' in result
    
    def test_parse_cfswitch_nested(self, parser):
        """Test parsing cfswitch with nested cfcase tags"""
        code = '''
        <cfswitch expression="#variables.action#">
            <cfcase value="create">
                <cfset result = createRecord() />
            </cfcase>
            <cfcase value="update">
                <cfset result = updateRecord() />
            </cfcase>
            <cfdefaultcase>
                <cfset result = "unknown action" />
            </cfdefaultcase>
        </cfswitch>
        '''
        
        result = parser.parse_code(code)
        
        assert result is not None
        assert 'tags' in result or 'statements' in result


class TestColdFusionSpecialFiles:
    """Test parsing special ColdFusion file types"""
    
    @pytest.fixture
    def parser(self):
        return ColdFusionParser()
    
    @pytest.fixture
    def fixtures_dir(self):
        return Path("tests/fixtures/coldfusion")
    
    def test_parse_application_cfm(self, parser, fixtures_dir):
        """Test parsing Application.cfm (application scope initialization)"""
        app_file = fixtures_dir / "Application.cfm"
        
        # Application.cfm should exist in fixtures
        assert app_file.exists(), f"Expected {app_file} to exist"
        
        result = parser.parse_file(app_file)
        
        assert result is not None
        assert result['language'] == 'coldfusion'
        assert 'file_path' in result
    
    def test_parse_fusebox_xml_cfm(self, parser, fixtures_dir):
        """Test parsing fusebox XML-style CFM files"""
        # Fusebox uses XML-like syntax in CFM files
        fusebox_files = list(fixtures_dir.glob("fusebox*.cfm"))
        
        # At least one fusebox file should exist
        assert len(fusebox_files) > 0, "Expected fusebox CFM files in fixtures"
        
        result = parser.parse_file(fusebox_files[0])
        
        assert result is not None
        assert result['language'] == 'coldfusion'


class TestColdFusionErrorHandling:
    """Test error handling and edge cases"""
    
    @pytest.fixture
    def parser(self):
        return ColdFusionParser()
    
    def test_malformed_tag_missing_closing(self, parser):
        """Test handling of malformed tag (missing closing tag)"""
        code = '''
        <cffunction name="broken" access="public">
            <cfset var x = 1>
        <!--- Missing </cffunction> --->
        '''
        
        # Should either raise specific exception or return error in result
        try:
            result = parser.parse_code(code)
            assert 'errors' in result or 'warnings' in result
        except Exception as e:
            # Expected to raise parsing exception
            assert "malformed" in str(e).lower() or "closing tag" in str(e).lower()
    
    def test_unknown_tag_graceful_degradation(self, parser):
        """Test graceful handling of unknown/custom tags"""
        code = '''
        <cffunction name="test" access="public">
            <cf_customtag attribute="value" />
            <cfreturn true />
        </cffunction>
        '''
        
        # Should parse successfully, treating unknown tags as generic
        result = parser.parse_code(code)
        
        assert result is not None
        assert len(result['functions']) == 1
    
    def test_empty_file(self, parser):
        """Test parsing empty file"""
        code = ''
        
        result = parser.parse_code(code)
        
        assert result is not None
        assert result['language'] == 'coldfusion'
        assert len(result.get('functions', [])) == 0
        assert len(result.get('components', [])) == 0


class TestColdFusionPerformance:
    """Test parser performance requirements"""
    
    @pytest.fixture
    def parser(self):
        return ColdFusionParser()
    
    @pytest.fixture
    def fixtures_dir(self):
        return Path("tests/fixtures/coldfusion")
    
    def test_performance_large_file(self, parser, fixtures_dir):
        """Test parser performance on large file (<100ms for <1000 LOC)"""
        # fusebox40.transformer.cfmx.cfm is 44.9 KB - good test case
        large_file = fixtures_dir / "fusebox40.transformer.cfmx.cfm"
        
        assert large_file.exists(), f"Expected {large_file} to exist"
        
        start = time.time()
        result = parser.parse_file(large_file)
        duration = time.time() - start
        
        assert result is not None
        assert duration < 0.1, f"Parser took {duration:.3f}s, expected <0.1s"
    
    def test_performance_multiple_components(self, parser, fixtures_dir):
        """Test parser performance on file with multiple components"""
        # adjustment_api.cfc is 79.4 KB - largest test fixture
        large_cfc = fixtures_dir / "adjustment_api.cfc"
        
        if large_cfc.exists():
            start = time.time()
            result = parser.parse_file(large_cfc)
            duration = time.time() - start
            
            assert result is not None
            assert duration < 0.15, f"Parser took {duration:.3f}s, expected <0.15s for large CFC"
