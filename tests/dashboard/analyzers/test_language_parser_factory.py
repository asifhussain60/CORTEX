"""
Comprehensive unit tests for LanguageParserFactory.
"""

import pytest
from pathlib import Path
from src.dashboard.analyzers import (
    LanguageParserFactory,
    get_factory,
    supports_file,
    detect_language,
    analyze_file,
    CSharpAnalyzer,
    TypeScriptAnalyzer,
    ColdFusionAnalyzer,
    SQLAnalyzer
)


@pytest.fixture
def factory():
    """Create factory instance."""
    return LanguageParserFactory()


@pytest.fixture
def sample_files():
    """Paths to all sample files."""
    fixtures_dir = Path(__file__).parent / 'fixtures'
    return {
        'csharp': fixtures_dir / 'sample.cs',
        'typescript': fixtures_dir / 'sample.ts',
        'coldfusion': fixtures_dir / 'sample.cfc',
        'sql': fixtures_dir / 'sample.sql'
    }


def test_factory_singleton():
    """Test factory singleton pattern."""
    factory1 = get_factory()
    factory2 = get_factory()
    
    assert factory1 is factory2


def test_factory_initialization(factory):
    """Test factory initializes with all analyzers."""
    assert len(factory._analyzers) == 4
    assert 'csharp' in factory._analyzers
    assert 'typescript' in factory._analyzers
    assert 'coldfusion' in factory._analyzers
    assert 'sql' in factory._analyzers


def test_get_analyzer_by_language(factory):
    """Test getting analyzer by language name."""
    csharp_analyzer = factory.get_analyzer('csharp')
    assert isinstance(csharp_analyzer, CSharpAnalyzer)
    
    typescript_analyzer = factory.get_analyzer('typescript')
    assert isinstance(typescript_analyzer, TypeScriptAnalyzer)
    
    coldfusion_analyzer = factory.get_analyzer('coldfusion')
    assert isinstance(coldfusion_analyzer, ColdFusionAnalyzer)
    
    sql_analyzer = factory.get_analyzer('sql')
    assert isinstance(sql_analyzer, SQLAnalyzer)


def test_get_analyzer_invalid_language(factory):
    """Test getting analyzer for invalid language."""
    analyzer = factory.get_analyzer('invalid')
    assert analyzer is None


def test_supports_file_csharp(factory):
    """Test file support detection for C#."""
    assert factory.supports_file(Path('test.cs'))
    assert factory.supports_file(Path('Test.CS'))
    assert factory.supports_file(Path('path/to/file.cs'))


def test_supports_file_typescript(factory):
    """Test file support detection for TypeScript."""
    assert factory.supports_file(Path('test.ts'))
    assert factory.supports_file(Path('Test.TS'))
    assert factory.supports_file(Path('path/to/file.ts'))


def test_supports_file_coldfusion(factory):
    """Test file support detection for ColdFusion."""
    assert factory.supports_file(Path('test.cfc'))
    assert factory.supports_file(Path('test.cfm'))
    assert factory.supports_file(Path('Test.CFC'))


def test_supports_file_sql(factory):
    """Test file support detection for SQL."""
    assert factory.supports_file(Path('test.sql'))
    assert factory.supports_file(Path('Test.SQL'))
    assert factory.supports_file(Path('path/to/schema.sql'))


def test_supports_file_unsupported(factory):
    """Test unsupported file extensions."""
    assert not factory.supports_file(Path('test.txt'))
    assert not factory.supports_file(Path('test.py'))
    assert not factory.supports_file(Path('test.java'))
    assert not factory.supports_file(Path('test.rb'))


def test_detect_language_by_extension(factory):
    """Test language detection by file extension."""
    assert factory.detect_language(Path('test.cs')) == 'csharp'
    assert factory.detect_language(Path('test.ts')) == 'typescript'
    assert factory.detect_language(Path('test.cfc')) == 'coldfusion'
    assert factory.detect_language(Path('test.cfm')) == 'coldfusion'
    assert factory.detect_language(Path('test.sql')) == 'sql'


def test_detect_language_unsupported(factory):
    """Test language detection for unsupported files."""
    assert factory.detect_language(Path('test.txt')) is None
    assert factory.detect_language(Path('test.py')) is None


def test_analyze_file_csharp(factory, sample_files):
    """Test analyzing C# file through factory."""
    result = factory.analyze_file(sample_files['csharp'])
    
    assert result is not None
    assert result.language == 'csharp'
    assert len(result.classes) >= 2
    assert len(result.methods) >= 5


def test_analyze_file_typescript(factory, sample_files):
    """Test analyzing TypeScript file through factory."""
    result = factory.analyze_file(sample_files['typescript'])
    
    assert result is not None
    assert result.language == 'typescript'
    assert len(result.classes) >= 2
    assert len(result.methods) >= 3


def test_analyze_file_coldfusion(factory, sample_files):
    """Test analyzing ColdFusion file through factory."""
    result = factory.analyze_file(sample_files['coldfusion'])
    
    assert result is not None
    assert result.language == 'coldfusion'
    assert len(result.classes) >= 1
    assert len(result.methods) >= 6


def test_analyze_file_sql(factory, sample_files):
    """Test analyzing SQL file through factory."""
    result = factory.analyze_file(sample_files['sql'])
    
    assert result is not None
    assert result.language == 'sql'
    assert len(result.classes) >= 3  # Tables
    assert len(result.methods) >= 4  # Procedures + Functions


def test_analyze_file_unsupported(factory, tmp_path):
    """Test analyzing unsupported file."""
    unsupported_file = tmp_path / 'test.txt'
    unsupported_file.write_text('Hello World')
    
    result = factory.analyze_file(unsupported_file)
    assert result is None


def test_analyze_file_nonexistent(factory):
    """Test analyzing nonexistent file."""
    result = factory.analyze_file(Path('nonexistent.cs'))
    
    # Should return result with errors
    assert result is not None
    assert len(result.errors) > 0


def test_get_supported_extensions(factory):
    """Test getting list of supported extensions."""
    extensions = factory.get_supported_extensions()
    
    assert '.cs' in extensions
    assert '.ts' in extensions
    assert '.cfc' in extensions
    assert '.cfm' in extensions
    assert '.sql' in extensions


def test_get_supported_languages(factory):
    """Test getting list of supported languages."""
    languages = factory.get_supported_languages()
    
    assert 'csharp' in languages
    assert 'typescript' in languages
    assert 'coldfusion' in languages
    assert 'sql' in languages
    assert len(languages) == 4


def test_convenience_function_supports_file():
    """Test convenience function supports_file."""
    assert supports_file(Path('test.cs'))
    assert supports_file(Path('test.ts'))
    assert not supports_file(Path('test.txt'))


def test_convenience_function_detect_language():
    """Test convenience function detect_language."""
    assert detect_language(Path('test.cs')) == 'csharp'
    assert detect_language(Path('test.ts')) == 'typescript'
    assert detect_language(Path('test.txt')) is None


def test_convenience_function_analyze_file(sample_files):
    """Test convenience function analyze_file."""
    result = analyze_file(sample_files['csharp'])
    
    assert result is not None
    assert result.language == 'csharp'
    assert len(result.classes) >= 2


def test_batch_analysis(factory, sample_files):
    """Test analyzing multiple files in batch."""
    results = []
    
    for file_path in sample_files.values():
        result = factory.analyze_file(file_path)
        if result:
            results.append(result)
    
    assert len(results) == 4
    
    # Check each language was analyzed
    languages = {r.language for r in results}
    assert languages == {'csharp', 'typescript', 'coldfusion', 'sql'}


def test_factory_registration_order(factory):
    """Test analyzer registration maintains order."""
    languages = list(factory._analyzers.keys())
    
    # Should match registration order in factory
    assert languages.index('csharp') < languages.index('typescript')
    assert languages.index('typescript') < languages.index('coldfusion')
    assert languages.index('coldfusion') < languages.index('sql')


def test_case_insensitive_extension(factory):
    """Test case-insensitive file extension handling."""
    assert factory.detect_language(Path('Test.CS')) == 'csharp'
    assert factory.detect_language(Path('Test.TS')) == 'typescript'
    assert factory.detect_language(Path('Test.CFC')) == 'coldfusion'
    assert factory.detect_language(Path('Test.SQL')) == 'sql'
