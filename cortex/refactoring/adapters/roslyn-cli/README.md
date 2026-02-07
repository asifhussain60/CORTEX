# CortexRoslynCli - C# Refactoring Tool

.NET-based CLI tool for semantic C# refactoring using Roslyn compiler services.

## Overview

CortexRoslynCli is a JSON-RPC style command-line tool that provides 8 C# refactoring operations:

1. **rename** - Rename symbols (variables, methods, classes)
2. **extract_method** - Extract code into new method
3. **inline_method** - Inline method calls
4. **encapsulate_field** - Generate getter/setter for field
5. **extract_interface** - Extract interface from class
6. **introduce_parameter** - Convert local variable to parameter
7. **move_to_new_file** - Move type to new file
8. **change_signature** - Modify method signature

## Requirements

- .NET 8.0 SDK or higher
- Roslyn API packages (automatically restored)

## Building

From the `roslyn-cli` directory:

```bash
# Restore packages and build
dotnet restore
dotnet build -c Release

# Output: bin/Release/net8.0/CortexRoslynCli.dll
```

## Usage

### Command-Line Mode

```bash
# Show version
dotnet CortexRoslynCli.dll --version

# Show help
dotnet CortexRoslynCli.dll --help

# Execute refactoring (reads JSON from stdin)
echo '{"action":"refactor","operation":"rename",...}' | dotnet CortexRoslynCli.dll refactor
```

### JSON Request Format

```json
{
  "action": "refactor",
  "operation": "rename",
  "file_path": "/path/to/file.cs",
  "parameters": {
    "offset": 150,
    "new_name": "NewName"
  }
}
```

### JSON Response Format

**Success:**
```json
{
  "success": true,
  "modified_files": ["/path/to/file.cs"],
  "description": "Renamed 'OldName' to 'NewName'",
  "warnings": [],
  "metadata": {}
}
```

**Error:**
```json
{
  "success": false,
  "error": "No symbol found at offset 150",
  "modified_files": [],
  "description": "",
  "warnings": [],
  "metadata": {}
}
```

## Operation Parameters

### rename
- `offset` (int): Position of symbol to rename
- `new_name` (string): New symbol name

### extract_method
- `start_offset` (int): Start of code to extract
- `end_offset` (int): End of code to extract
- `new_name` (string): Name of new method

### inline_method
- `offset` (int): Position of method to inline

### encapsulate_field
- `offset` (int): Position of field
- `property_name` (string): Name of generated property

### extract_interface
- `offset` (int): Position of class
- `interface_name` (string): Name of new interface

### introduce_parameter
- `offset` (int): Position of local variable
- `parameter_name` (string): Name of new parameter

### move_to_new_file
- `offset` (int): Position of type
- `new_file_path` (string): Path to new file

### change_signature
- `offset` (int): Position of method
- `new_parameters` (array): New parameter list

## Testing

Integration tests are located in `tests/integration/refactoring/test_roslyn_cli_operations.py`.

Run tests:
```bash
# From CORTEX root directory
python3 -m pytest tests/integration/refactoring/test_roslyn_cli_operations.py -v
```

## Architecture

- **Program.cs**: Entry point, command-line parsing, JSON-RPC handling
- **RefactoringService.cs**: Core refactoring operations using Roslyn APIs
- **CortexRoslynCli.csproj**: Project configuration with Roslyn dependencies

## Integration with CORTEX

Used by `RoslynAdapter` in Python via subprocess:

```python
from cortex.refactoring.adapters.roslyn_adapter import RoslynAdapter

adapter = RoslynAdapter()
if adapter.is_available():
    request = RefactoringRequest(...)
    result = adapter.execute_refactoring(request)
```

## Development Notes

- Rename operation: Fully implemented using Roslyn's `Renamer` API
- Other operations: Simplified implementations (production would need full Roslyn services)
- Error handling: Graceful degradation with detailed error messages
- Type safety: Strong typing for parameters and responses

## Phase Information

**Phase:** 24.2.2 - C# Refactoring (Type-Safe Operations)  
**Audit Code:** AC-PHASE24.2.2-002, AC-PHASE24.2.2-003  
**Author:** Asif Hussain  
**Created:** 2026-02-07
