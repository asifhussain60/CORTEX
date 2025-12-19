#!/usr/bin/env python3
"""
Security Collector Validation Tests

TDD approach: Write comprehensive tests for all security scans to ensure
collectors don't miss vulnerabilities.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from src.dashboard.data.security_collector import SecurityCollector


class TestSQLInjectionScans:
    """Test SQL injection detection comprehensiveness."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_detects_string_concatenation_sql(self, temp_repo):
        """FAILING: Should detect SQL with + operator."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            string query = "SELECT * FROM Users WHERE Id = " + userId;
            SqlCommand cmd = new SqlCommand(query);
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_sql_injection()
        
        assert len(findings) > 0, "Should detect string concatenation SQL injection"
        assert any("concatenation" in f['description'].lower() for f in findings)
    
    def test_detects_string_interpolation_sql(self, temp_repo):
        """FAILING: Should detect $"SELECT..." patterns."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            string query = $"SELECT * FROM Users WHERE Name = '{userName}'";
            var result = db.Execute(query);
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_sql_injection()
        
        assert len(findings) > 0, "Should detect string interpolation SQL injection"
        assert any("interpolation" in f['description'].lower() for f in findings)
    
    def test_detects_string_format_sql(self, temp_repo):
        """FAILING: Should detect String.Format with SQL."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            string query = String.Format("SELECT * FROM {0} WHERE Id = {1}", table, id);
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_sql_injection()
        
        assert len(findings) > 0, "Should detect String.Format SQL injection"


class TestXSSScans:
    """Test XSS detection comprehensiveness."""
    
    @pytest.fixture
    def temp_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_detects_response_write_without_encode(self, temp_repo):
        """FAILING: Current check is too weak - requires both conditions in same file."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            Response.Write(Request.QueryString["name"]);
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_xss()
        
        assert len(findings) > 0, "Should detect Response.Write without HtmlEncode"
    
    def test_detects_innerhtml_assignment(self, temp_repo):
        """FAILING: Not currently checked."""
        js_file = temp_repo / "test.js"
        js_file.write_text('''
            element.innerHTML = userInput;
            document.getElementById('output').innerHTML = data;
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_xss()
        
        assert len(findings) > 0, "Should detect innerHTML assignments"
    
    def test_detects_document_write(self, temp_repo):
        """FAILING: Not currently checked."""
        js_file = temp_repo / "test.js"
        js_file.write_text('''
            document.write(userInput);
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_xss()
        
        assert len(findings) > 0, "Should detect document.write with user input"
    
    def test_detects_jquery_html_method(self, temp_repo):
        """FAILING: Not currently checked."""
        js_file = temp_repo / "test.js"
        js_file.write_text('''
            $('#output').html(userInput);
            $(element).html(data);
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_xss()
        
        assert len(findings) > 0, "Should detect jQuery .html() with user input"
    
    def test_detects_eval_with_user_input(self, temp_repo):
        """FAILING: Not currently checked."""
        js_file = temp_repo / "test.js"
        js_file.write_text('''
            eval(userInput);
            new Function(data)();
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_xss()
        
        assert len(findings) > 0, "Should detect eval/Function with user input"
    
    def test_detects_aspx_without_encoding(self, temp_repo):
        """FAILING: Not currently checked."""
        aspx_file = temp_repo / "test.aspx"
        aspx_file.write_text('''
            <%= Request.QueryString["name"] %>
            <%= userInput %>
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_xss()
        
        assert len(findings) > 0, "Should detect <%= without encoding in ASPX"


class TestHardcodedSecretsScans:
    """Test hardcoded secrets detection."""
    
    @pytest.fixture
    def temp_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_detects_basic_auth_header(self, temp_repo):
        """FAILING: Not currently checked."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            request.Headers.Add("Authorization", "Basic YWRtaW46cGFzc3dvcmQxMjM=");
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_hardcoded_secrets()
        
        assert len(findings) > 0, "Should detect Basic Auth in headers"
    
    def test_detects_jwt_tokens(self, temp_repo):
        """FAILING: Not currently checked."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            string token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0";
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_hardcoded_secrets()
        
        assert len(findings) > 0, "Should detect JWT tokens"
    
    def test_detects_aws_keys(self, temp_repo):
        """FAILING: Not currently checked."""
        config = temp_repo / "app.config"
        config.write_text('''
            <add key="AWSAccessKey" value="AKIAIOSFODNN7EXAMPLE" />
            <add key="AWSSecretKey" value="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" />
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_hardcoded_secrets()
        
        assert len(findings) > 0, "Should detect AWS access keys"
    
    def test_detects_azure_connection_strings(self, temp_repo):
        """FAILING: Not currently checked."""
        config = temp_repo / "web.config"
        config.write_text('''
            <add name="Azure" connectionString="DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=abc123==" />
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_hardcoded_secrets()
        
        assert len(findings) > 0, "Should detect Azure connection strings"
    
    def test_detects_private_keys(self, temp_repo):
        """FAILING: Not currently checked."""
        pem_file = temp_repo / "private.pem"
        pem_file.write_text('''
            -----BEGIN RSA PRIVATE KEY-----
            MIIEpAIBAAKCAQEA...
            -----END RSA PRIVATE KEY-----
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_hardcoded_secrets()
        
        assert len(findings) > 0, "Should detect private keys in PEM files"


class TestInsecureDeserializationScans:
    """Test insecure deserialization detection."""
    
    @pytest.fixture
    def temp_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_detects_binary_formatter(self, temp_repo):
        """Should detect BinaryFormatter usage."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            BinaryFormatter formatter = new BinaryFormatter();
            object obj = formatter.Deserialize(stream);
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_for_vulnerabilities()
        
        insecure_deser = [f for f in findings if 'deserialization' in f['type'].lower()]
        assert len(insecure_deser) > 0, "Should detect BinaryFormatter"
    
    def test_detects_type_name_handling_all(self, temp_repo):
        """FAILING: Not currently checked."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            var settings = new JsonSerializerSettings {
                TypeNameHandling = TypeNameHandling.All
            };
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_for_vulnerabilities()
        
        insecure_deser = [f for f in findings if 'deserialization' in f['type'].lower()]
        assert len(insecure_deser) > 0, "Should detect TypeNameHandling.All"


class TestWeakCryptographyScans:
    """Test weak cryptography detection."""
    
    @pytest.fixture
    def temp_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_detects_md5(self, temp_repo):
        """Should detect MD5 usage."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            MD5 md5 = MD5.Create();
            byte[] hash = md5.ComputeHash(data);
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_for_vulnerabilities()
        
        weak_crypto = [f for f in findings if 'cryptography' in f['type'].lower() or 'MD5' in f.get('description', '')]
        assert len(weak_crypto) > 0, "Should detect MD5 usage"
    
    def test_detects_sha1(self, temp_repo):
        """FAILING: Not comprehensive."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            SHA1 sha = SHA1.Create();
            HashAlgorithm.Create("SHA1");
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_for_vulnerabilities()
        
        weak_crypto = [f for f in findings if 'SHA1' in f.get('description', '')]
        assert len(weak_crypto) > 0, "Should detect SHA1 usage"
    
    def test_detects_des_3des(self, temp_repo):
        """FAILING: Not currently checked."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            DES des = DES.Create();
            TripleDES tdes = TripleDES.Create();
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_for_vulnerabilities()
        
        weak_crypto = [f for f in findings if 'DES' in f.get('description', '') or 'TripleDES' in f.get('description', '')]
        assert len(weak_crypto) > 0, "Should detect DES/3DES usage"
    
    def test_detects_ecb_mode(self, temp_repo):
        """FAILING: Not currently checked."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            aes.Mode = CipherMode.ECB;
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_for_vulnerabilities()
        
        weak_crypto = [f for f in findings if 'ECB' in f.get('description', '')]
        assert len(weak_crypto) > 0, "Should detect ECB mode usage"


class TestInputValidationScans:
    """Test input validation detection."""
    
    @pytest.fixture
    def temp_repo(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    def test_detects_unvalidated_redirects(self, temp_repo):
        """FAILING: Not currently checked."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            Response.Redirect(Request.QueryString["url"]);
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_for_vulnerabilities()
        
        validation_issues = [f for f in findings if 'redirect' in f.get('description', '').lower()]
        assert len(validation_issues) > 0, "Should detect unvalidated redirects"
    
    def test_detects_path_traversal(self, temp_repo):
        """FAILING: Not currently checked."""
        cs_file = temp_repo / "test.cs"
        cs_file.write_text('''
            string path = Path.Combine(basePath, Request.QueryString["file"]);
            File.ReadAllText(path);
        ''')
        
        collector = SecurityCollector(temp_repo)
        findings = collector._scan_for_vulnerabilities()
        
        validation_issues = [f for f in findings if 'path' in f.get('description', '').lower() or 'traversal' in f.get('description', '').lower()]
        assert len(validation_issues) > 0, "Should detect path traversal"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
