"""Quick test for CodeCleanupValidator"""
from src.workflows.code_cleanup_validator import CodeCleanupValidator
from pathlib import Path
import tempfile

# Create temp file
temp = Path(tempfile.mkdtemp())
test_file = temp / 'test.py'
test_file.write_text('''def hello():
    print("Debug message")
    return "Hello"
''')

# Test validator
validator = CodeCleanupValidator()

# Debug: Check what language is detected
lang = validator._get_language(test_file)
print(f'Detected language: {lang}')

# Debug: Check if file is excluded
excluded = validator._is_excluded(test_file)
print(f'File excluded: {excluded}')

# Debug: Read the file
with open(test_file, 'r') as f:
    content = f.read()
    print(f'File content:\n{content}')

# Debug: Check patterns
print(f'\nDebug patterns for python: {validator.DEBUG_PATTERNS.get("python", [])}')

issues = validator.scan_file(test_file)

print(f'\nFile: {test_file}')
print(f'Issues found: {len(issues)}')
for issue in issues:
    print(f'  {issue}')

# Cleanup
import shutil
shutil.rmtree(temp)
