"""
Tests for Multi-Language Docstring Extraction

Tests C#, TypeScript, and JavaScript docstring extraction

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from src.intelligence.ast_docstring_extractor import (
    AstDocstringExtractor,
    DocstringInfo
)


class TestCSharpDocstringExtraction:
    """Test C# XML documentation comment extraction."""
    
    def test_extract_csharp_class_doc(self):
        """Should extract C# XML doc comments from class."""
        code = '''
/// <summary>
/// Manages user authentication and authorization.
/// Provides secure access control for enterprise applications.
/// </summary>
public class UserService
{
    public void Login() {}
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cs', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            assert len(results) >= 1
            assert results[0].name == 'UserService'
            assert results[0].type == 'class'
            assert 'authentication' in results[0].docstring.lower()
    
    def test_extract_csharp_method_doc(self):
        """Should extract C# method documentation."""
        code = '''
public class PaymentController
{
    /// <summary>
    /// Process payment transaction for customer order.
    /// </summary>
    /// <param name="orderId">Order identifier</param>
    /// <returns>Payment confirmation</returns>
    public PaymentResult ProcessPayment(int orderId)
    {
        return null;
    }
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cs', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            # Should extract class and method
            assert len(results) >= 1
            names = [r.name for r in results]
            assert 'ProcessPayment' in names or 'PaymentController' in names
    
    def test_extract_multiple_csharp_classes(self):
        """Should extract docs from multiple C# classes."""
        code = '''
/// <summary>User authentication service</summary>
public class AuthService {}

/// <summary>Payment processing service</summary>
public class PaymentService {}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cs', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            assert len(results) >= 2
            names = [r.name for r in results]
            assert 'AuthService' in names
            assert 'PaymentService' in names


class TestTypeScriptDocstringExtraction:
    """Test TypeScript/JavaScript JSDoc extraction."""
    
    def test_extract_typescript_class_doc(self):
        """Should extract JSDoc from TypeScript class."""
        code = '''
/**
 * Manages user authentication and authorization.
 * Provides secure access control for enterprise applications.
 */
export class UserService {
    login() {}
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            assert len(results) >= 1
            assert results[0].name == 'UserService'
            assert results[0].type == 'class'
            assert 'authentication' in results[0].docstring.lower()
    
    def test_extract_javascript_function_doc(self):
        """Should extract JSDoc from JavaScript function."""
        code = '''
/**
 * Calculate total price for items in cart.
 * @param {Array} items - List of cart items
 * @returns {number} Total price
 */
function calculateTotal(items) {
    return items.reduce((sum, item) => sum + item.price, 0);
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            assert len(results) >= 1
            assert results[0].name == 'calculateTotal'
            assert results[0].type == 'function'
            assert 'calculate' in results[0].docstring.lower()
    
    def test_extract_typescript_interface_doc(self):
        """Should extract JSDoc from TypeScript interface."""
        code = '''
/**
 * Represents a user in the system.
 * Contains authentication and profile information.
 */
export interface User {
    id: number;
    email: string;
}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ts', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            assert len(results) >= 1
            assert results[0].name == 'User'
            assert 'user' in results[0].docstring.lower()


class TestMultiLanguageConsistency:
    """Test consistent output schema across languages."""
    
    def test_consistent_schema_python_csharp(self):
        """Should return same schema for Python and C#."""
        # Python class
        py_code = '''
class Service:
    """A service class."""
    pass
'''
        # C# class
        cs_code = '''
/// <summary>A service class.</summary>
public class Service {}
'''
        
        extractor = AstDocstringExtractor()
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(py_code)
            f.flush()
            py_results = extractor.extract_from_file(Path(f.name))
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cs', delete=False) as f:
            f.write(cs_code)
            f.flush()
            cs_results = extractor.extract_from_file(Path(f.name))
        
        # Both should have same fields
        assert py_results[0].name == cs_results[0].name
        assert py_results[0].type == cs_results[0].type
        assert hasattr(py_results[0], 'informativeness_score')
        assert hasattr(cs_results[0], 'informativeness_score')
    
    def test_ranking_works_across_languages(self):
        """Should rank docstrings across all languages."""
        extractor = AstDocstringExtractor()
        
        # Create mixed language files
        files = []
        
        # Short Python doc
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write('class A:\n    """Short."""\n    pass')
            f.flush()
            files.append(Path(f.name))
        
        # Long C# doc
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cs', delete=False) as f:
            f.write('/// <summary>Long detailed documentation with many words.</summary>\npublic class B {}')
            f.flush()
            files.append(Path(f.name))
        
        all_results = []
        for file_path in files:
            all_results.extend(extractor.extract_from_file(file_path))
        
        # Should have 2 results
        assert len(all_results) == 2
        
        # Longer doc should rank higher (after ranking)
        ranked = sorted(all_results, key=lambda x: x.informativeness_score, reverse=True)
        assert ranked[0].name == 'B'  # Longer C# doc


class TestMultiLanguageEdgeCases:
    """Test edge cases for multi-language support."""
    
    def test_unsupported_file_type(self):
        """Should return empty list for unsupported file types."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write('Plain text file')
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            assert results == []
    
    def test_malformed_csharp_xml(self):
        """Should handle malformed C# XML gracefully."""
        code = '''
/// <summary>Unclosed tag
public class Service {}
'''
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cs', delete=False) as f:
            f.write(code)
            f.flush()
            
            extractor = AstDocstringExtractor()
            results = extractor.extract_from_file(Path(f.name))
            
            # Should not crash, may return partial or empty
            assert isinstance(results, list)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
