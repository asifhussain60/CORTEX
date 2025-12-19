"""Test C# detection"""
from src.workflows.code_cleanup_validator import CodeCleanupValidator
from pathlib import Path
import tempfile

# Create temp file
temp = Path(tempfile.mkdtemp())
test_file = temp / 'test.cs'
test_file.write_text('''public class Test {
    public void Debug() {
        Console.WriteLine("Debug message");
    }
}
''')

# Test validator
validator = CodeCleanupValidator()

# Debug
lang = validator._get_language(test_file)
print(f'Detected language: {lang}')
print(f'File excluded: {validator._is_excluded(test_file)}')

issues = validator.scan_file(test_file)

print(f'\nIssues found: {len(issues)}')
for issue in issues:
    print(f'  {issue}')

# Test 2: NotImplementedException
test_file2 = temp / 'test2.cs'
test_file2.write_text('''public class Test {
    public void NotDone() {
        throw new NotImplementedException();
    }
}
''')

issues2 = validator.scan_file(test_file2)
print(f'\nNotImplementedException test:')
print(f'Issues found: {len(issues2)}')
for issue in issues2:
    print(f'  {issue}')

# Cleanup
import shutil
shutil.rmtree(temp)
