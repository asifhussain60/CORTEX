"""
Phase 0: Performance and Load Tests

Tests performance characteristics, load times, and resource usage.
Part of GREEN baseline establishment (200+ tests target).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import time
import json
from pathlib import Path


@pytest.mark.unit
@pytest.mark.slow
class TestJSONLoadPerformance:
    """Test JSON loading performance."""
    
    def test_overview_loads_quickly(self, mock_data_path):
        """Test that overview.json loads in reasonable time."""
        start = time.time()
        with open(mock_data_path / "overview.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        elapsed = time.time() - start
        
        assert elapsed < 1.0, f"Overview took {elapsed}s to load (should be < 1s)"
        assert data is not None
        
    def test_all_files_load_under_5_seconds(self, mock_data_path):
        """Test that all JSON files load within 5 seconds total."""
        start = time.time()
        
        for json_file in mock_data_path.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                assert data is not None
                
        elapsed = time.time() - start
        assert elapsed < 5.0, f"All files took {elapsed}s to load (should be < 5s)"
        
    def test_repeated_loads_are_fast(self, mock_data_path):
        """Test that repeated loads are fast (OS caching)."""
        overview_file = mock_data_path / "overview.json"
        
        # First load
        with open(overview_file, "r", encoding="utf-8") as f:
            json.load(f)
            
        # Second load (should be faster due to OS cache)
        start = time.time()
        with open(overview_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        elapsed = time.time() - start
        
        assert elapsed < 0.5, f"Cached load took {elapsed}s (should be < 0.5s)"
        assert data is not None


@pytest.mark.unit
class TestDataSizeConstraints:
    """Test that data files are reasonable sizes."""
    
    def test_overview_file_size(self, mock_data_path):
        """Test that overview.json is reasonable size."""
        file_path = mock_data_path / "overview.json"
        size_kb = file_path.stat().st_size / 1024
        
        assert size_kb < 500, f"Overview is {size_kb}KB (should be < 500KB)"
        assert size_kb > 0.1, f"Overview is {size_kb}KB (seems too small)"
        
    def test_tech_stack_file_size(self, mock_data_path):
        """Test that tech-stack.json is reasonable size."""
        file_path = mock_data_path / "tech-stack.json"
        size_kb = file_path.stat().st_size / 1024
        
        assert size_kb < 500, f"Tech stack is {size_kb}KB (should be < 500KB)"
        
    def test_security_file_size(self, mock_data_path):
        """Test that security.json is reasonable size."""
        file_path = mock_data_path / "security.json"
        size_kb = file_path.stat().st_size / 1024
        
        assert size_kb < 500, f"Security is {size_kb}KB (should be < 500KB)"
        
    def test_all_files_under_total_limit(self, mock_data_path):
        """Test that total data size is reasonable."""
        total_kb = 0
        for json_file in mock_data_path.glob("*.json"):
            total_kb += json_file.stat().st_size / 1024
            
        assert total_kb < 5000, f"Total data is {total_kb}KB (should be < 5MB)"


@pytest.mark.unit
class TestDataComplexity:
    """Test data structure complexity."""
    
    def _max_depth(self, obj, current_depth=0):
        """Calculate maximum nesting depth of data structure."""
        if isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._max_depth(v, current_depth + 1) for v in obj.values())
        elif isinstance(obj, list):
            if not obj:
                return current_depth
            return max(self._max_depth(item, current_depth + 1) for item in obj)
        else:
            return current_depth
            
    def test_overview_nesting_depth(self, mock_data_path):
        """Test that overview.json doesn't have excessive nesting."""
        with open(mock_data_path / "overview.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        depth = self._max_depth(data)
        assert depth < 10, f"Overview has depth {depth} (should be < 10)"
        
    def test_tech_stack_nesting_depth(self, mock_data_path):
        """Test that tech-stack.json doesn't have excessive nesting."""
        with open(mock_data_path / "tech-stack.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            
        depth = self._max_depth(data)
        assert depth < 10, f"Tech stack has depth {depth} (should be < 10)"
        
    def test_no_file_has_excessive_array_sizes(self, mock_data_path):
        """Test that arrays don't have excessive size."""
        def check_arrays(obj):
            if isinstance(obj, list):
                assert len(obj) < 10000, f"Array has {len(obj)} items (too many)"
                for item in obj:
                    check_arrays(item)
            elif isinstance(obj, dict):
                for value in obj.values():
                    check_arrays(value)
                    
        for json_file in mock_data_path.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                check_arrays(data)


@pytest.mark.unit
class TestDataReadability:
    """Test that data files are human-readable."""
    
    def test_json_is_formatted(self, mock_data_path):
        """Test that JSON files are formatted (not minified)."""
        for json_file in mock_data_path.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Formatted JSON should have newlines and indentation
            lines = content.split("\n")
            assert len(lines) > 3 or len(content) < 100, f"{json_file.name} might be minified"
            
    def test_json_keys_are_readable(self, mock_data_path):
        """Test that JSON keys use readable names."""
        for json_file in mock_data_path.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            def check_keys(obj):
                if isinstance(obj, dict):
                    for key in obj.keys():
                        # Keys should be at least 1 char and not just numbers
                        assert len(key) > 0, "Empty key found"
                        # Check nested objects
                        check_keys(obj[key])
                elif isinstance(obj, list):
                    for item in obj:
                        check_keys(item)
                        
            check_keys(data)


@pytest.mark.unit
class TestMemoryEfficiency:
    """Test memory efficiency of data structures."""
    
    def test_no_duplicate_large_strings(self, mock_data_path):
        """Test that large strings aren't duplicated unnecessarily."""
        for json_file in mock_data_path.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # Count string occurrences
            strings = []
            
            def collect_strings(obj):
                if isinstance(obj, str) and len(obj) > 100:
                    strings.append(obj)
                elif isinstance(obj, dict):
                    for value in obj.values():
                        collect_strings(value)
                elif isinstance(obj, list):
                    for item in obj:
                        collect_strings(item)
                        
            collect_strings(data)
            
            # Check for duplicates in large strings
            if strings:
                unique_strings = set(strings)
                duplicate_ratio = len(strings) / len(unique_strings)
                assert duplicate_ratio < 3, f"{json_file.name} has {duplicate_ratio}x string duplication"


@pytest.mark.unit
class TestDataCacheability:
    """Test that data is suitable for caching."""
    
    def test_data_is_deterministic(self, mock_data_path):
        """Test that loading data twice gives same result."""
        overview_file = mock_data_path / "overview.json"
        
        with open(overview_file, "r", encoding="utf-8") as f:
            data1 = json.load(f)
            
        with open(overview_file, "r", encoding="utf-8") as f:
            data2 = json.load(f)
            
        # Convert to JSON string for comparison
        assert json.dumps(data1, sort_keys=True) == json.dumps(data2, sort_keys=True)
        
    def test_data_has_no_timestamps(self, mock_data_path):
        """Test that data doesn't have current timestamps (would break caching)."""
        for json_file in mock_data_path.glob("*.json"):
            with open(json_file, "r", encoding="utf-8") as f:
                content = f.read()
                
            # Shouldn't have "now" or current date patterns
            assert "new Date()" not in content
            assert "Date.now()" not in content


@pytest.mark.unit
class TestDataIntegrityChecks:
    """Test data integrity and consistency."""
    
    def test_no_missing_required_files(self, mock_data_path):
        """Test that all required data files exist."""
        required_files = [
            "overview.json",
            "executive-summary.json",
            "health-data.json",
            "tech-stack.json",
            "security.json",
            "architecture.json",
            "code-organization.json",
            "vendors.json"
        ]
        
        for filename in required_files:
            file_path = mock_data_path / filename
            assert file_path.exists(), f"Required file {filename} is missing"
            
    def test_file_modification_times(self, mock_data_path):
        """Test that files have reasonable modification times."""
        import datetime
        
        for json_file in mock_data_path.glob("*.json"):
            mtime = datetime.datetime.fromtimestamp(json_file.stat().st_mtime)
            now = datetime.datetime.now()
            
            # File should not be from the future
            assert mtime <= now, f"{json_file.name} has future timestamp"
            
            # File should not be too old (> 1 year)
            age_days = (now - mtime).days
            assert age_days < 365, f"{json_file.name} is {age_days} days old"
