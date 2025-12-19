"""
Test 1: AST Parsing Accuracy
Verifies AST correctly parses Flask monolith structure.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from src.orchestration_3_0.orchestrators.scaffolding.code_analyzer import CodeAnalyzer


@pytest.fixture
def flask_monolith_fixture():
    """Create temporary Flask monolith structure."""
    temp_dir = tempfile.mkdtemp()
    
    # Create app.py (God object - large file)
    app_file = Path(temp_dir) / "app.py"
    app_content = '''
from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/users')
def get_users():
    # Simulate large file
    pass

@app.route('/payments')
def process_payment():
    # Simulate large file
    pass

class UserService:
    def create_user(self):
        pass

class PaymentService:
    def process(self):
        pass

# Simulate 500+ lines
''' + '\n# Line\n' * 500
    
    app_file.write_text(app_content)
    
    # Create models.py
    models_file = Path(temp_dir) / "models.py"
    models_file.write_text('''
class User:
    def __init__(self, name):
        self.name = name

class Payment:
    def __init__(self, amount):
        self.amount = amount
''')
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


def test_ast_parsing_flask_monolith(flask_monolith_fixture):
    """Verify AST correctly parses Flask monolith structure."""
    analyzer = CodeAnalyzer(repo_path=flask_monolith_fixture)
    report = analyzer.analyze()
    
    # Assertions
    assert report.language == "python"
    assert report.framework == "Flask"
    assert report.modules >= 2  # app.py + models.py
    assert report.classes >= 4  # UserService, PaymentService, User, Payment
    assert report.functions >= 2  # get_users, process_payment
    
    # Should detect God object (app.py has >500 lines)
    assert len(report.anti_patterns) > 0
    god_objects = [ap for ap in report.anti_patterns if ap.type == "god_object"]
    assert len(god_objects) > 0
    assert god_objects[0].lines > 500
    assert god_objects[0].confidence > 0.5


def test_ast_parsing_empty_repository():
    """Verify analyzer handles empty repository gracefully."""
    with tempfile.TemporaryDirectory() as temp_dir:
        analyzer = CodeAnalyzer(repo_path=temp_dir)
        report = analyzer.analyze()
        
        assert report.language == "unknown"
        assert report.modules == 0
        assert report.classes == 0
        assert report.functions == 0
        assert len(report.anti_patterns) == 0


def test_ast_parsing_with_exclusions():
    """Verify exclusion patterns work correctly."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Create files in excluded directories
        vendor_dir = Path(temp_dir) / "vendor"
        vendor_dir.mkdir()
        (vendor_dir / "excluded.py").write_text("# Should be excluded")
        
        # Create files in included directories
        src_dir = Path(temp_dir) / "src"
        src_dir.mkdir()
        (src_dir / "included.py").write_text("def hello(): pass")
        
        analyzer = CodeAnalyzer(repo_path=temp_dir, exclusions=['vendor/*'])
        report = analyzer.analyze()
        
        # Should only analyze src/included.py
        assert report.modules == 1
