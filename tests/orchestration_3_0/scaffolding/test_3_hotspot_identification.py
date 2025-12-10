"""
Test 3: Hotspot Identification
Verifies high-complexity files identified as hotspots.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.orchestration_3_0.orchestrators.scaffolding.code_analyzer import CodeAnalyzer


@pytest.fixture
def complex_codebase_fixture():
    """Create temporary codebase with high-complexity file."""
    temp_dir = tempfile.mkdtemp()
    
    # High complexity file (many control flow statements)
    complex_file = Path(temp_dir) / "complex.py"
    complex_content = '''
def complex_function(x, y, z):
    result = 0
    
    if x > 0:
        result += x
        if y > 0:
            result += y
            if z > 0:
                result += z
    
    for i in range(10):
        if i % 2 == 0:
            result += i
        else:
            result -= i
    
    while result < 100:
        if result % 3 == 0:
            result += 1
        elif result % 5 == 0:
            result += 2
        else:
            result += 3
    
    try:
        if result > 50:
            result = result / 2
        else:
            result = result * 2
    except Exception as e:
        result = 0
    
    return result
'''
    complex_file.write_text(complex_content)
    
    # Simple file (low complexity)
    simple_file = Path(temp_dir) / "simple.py"
    simple_file.write_text('''
def simple_function(x):
    return x + 1
''')
    
    yield temp_dir
    
    shutil.rmtree(temp_dir)


def test_hotspot_identification_complexity(complex_codebase_fixture):
    """Verify high-complexity files identified as hotspots."""
    analyzer = CodeAnalyzer(repo_path=complex_codebase_fixture)
    report = analyzer.analyze()
    
    # Should identify hotspot
    assert len(report.hotspots) > 0
    
    # Check hotspot properties
    hotspot = report.hotspots[0]
    assert hotspot.complexity > 10  # Many control flow statements
    assert hotspot.file.endswith(".py")
    assert hotspot.confidence > 0.5


def test_hotspot_identification_no_hotspots():
    """Verify low-complexity codebase has no hotspots."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create only simple files
        for i in range(3):
            simple_file = Path(temp_dir) / f"simple_{i}.py"
            simple_file.write_text(f'''
def function_{i}(x):
    return x + {i}
''')
        
        analyzer = CodeAnalyzer(repo_path=temp_dir)
        report = analyzer.analyze()
        
        # Should have no hotspots (low complexity)
        assert len(report.hotspots) == 0
