# CORTEX Conversation Capture - Direct Mode Enhancement

**Purpose:** Add direct file import mode to conversation capture functionality  
**Date:** 2025-11-18  
**Author:** Asif Hussain  
**Status:** Planning  

---

## 🎯 Enhancement Overview

### Current Behavior
```
User: "capture conversation"
→ Creates empty template file
→ User pastes conversation
→ User runs "import conversation [id]"
→ System reads file and imports to Tier 1
```

### New Direct Mode
```
User: "capture conversation file:x file:y"
→ System reads provided files directly
→ Parses conversation content
→ Imports to Tier 1 immediately
→ No intermediate capture file created
```

### Design Decision: Dual-Mode Architecture

**Mode 1: Legacy Template Mode** (no parameters)
- User: `capture conversation` 
- Creates template file for manual paste
- User edits, saves, then imports
- **Use case:** Capturing from chat window, external sources

**Mode 2: Direct Import Mode** (with file parameters)
- User: `capture conversation file:/path/to/conv1.md file:/path/to/conv2.md`
- Reads files directly
- Parses and validates content
- Imports to Tier 1 immediately  
- **Use case:** Batch import, automation, existing conversation files

---

## 📋 Implementation Plan

### Phase 1: Command Detection Enhancement (30 min)

**File:** `src/conversation_capture/command_processor.py`

**Changes:**
1. Add file parameter detection to capture command pattern
2. Extract file paths from command string
3. Route to appropriate handler (template mode vs direct mode)

**New Pattern:**
```python
# Detect: "capture conversation file:path1 file:path2"
r'capture\s+conversation(?:\s+file:([^\s]+))+' 
```

**Example Detection:**
```python
Input: "capture conversation file:conv1.md file:conv2.md"
Detected: {
    'command': 'capture',
    'mode': 'direct',
    'files': ['conv1.md', 'conv2.md']
}
```

---

### Phase 2: Direct Import Handler (60 min)

**File:** `src/conversation_capture/capture_manager.py`

**New Method:** `import_files_directly(file_paths: List[str])`

**Workflow:**
```python
def import_files_directly(self, file_paths: List[str]) -> Dict[str, Any]:
    """
    Direct mode: Read files and import to Tier 1 without template
    
    Args:
        file_paths: List of file paths to import
        
    Returns:
        Dict with import results for each file
    """
    results = []
    
    for file_path in file_paths:
        # 1. Validate file exists and is readable
        if not self._validate_file(file_path):
            results.append({'file': file_path, 'success': False, 'error': 'File not found or not readable'})
            continue
        
        # 2. Read file content
        try:
            content = self._read_file_content(file_path)
        except Exception as e:
            results.append({'file': file_path, 'success': False, 'error': f'Read failed: {e}'})
            continue
        
        # 3. Parse conversation (reuse existing parser)
        conversation_data = self._parse_conversation_content(content, source_file=file_path)
        
        if not conversation_data['messages']:
            results.append({'file': file_path, 'success': False, 'error': 'No conversation messages found'})
            continue
        
        # 4. Import to Tier 1 (reuse existing import logic)
        memory_result = self._import_to_working_memory(conversation_data)
        
        if memory_result['success']:
            results.append({
                'file': file_path,
                'success': True,
                'conversation_id': memory_result['conversation_id'],
                'messages_imported': len(conversation_data['messages']),
                'entities_extracted': len(conversation_data['entities'])
            })
        else:
            results.append({
                'file': file_path,
                'success': False,
                'error': memory_result.get('error', 'Import failed')
            })
    
    # Summary
    total = len(file_paths)
    success_count = sum(1 for r in results if r['success'])
    
    return {
        'success': success_count > 0,
        'total_files': total,
        'successful_imports': success_count,
        'failed_imports': total - success_count,
        'results': results
    }
```

**Supporting Methods:**
```python
def _validate_file(self, file_path: str) -> bool:
    """Validate file exists and is readable"""
    path = Path(file_path)
    return path.exists() and path.is_file() and os.access(path, os.R_OK)

def _read_file_content(self, file_path: str) -> str:
    """Read file content with encoding detection"""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()
```

---

### Phase 3: Command Processor Integration (30 min)

**File:** `src/conversation_capture/command_processor.py`

**Enhanced `_handle_capture_command`:**
```python
def _handle_capture_command(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """Handle capture conversation command (template mode or direct mode)"""
    
    # Check if files were provided
    if 'files' in params and params['files']:
        # DIRECT MODE: Import files immediately
        return self._handle_direct_import(params['files'])
    else:
        # TEMPLATE MODE: Create empty template (existing behavior)
        user_hint = params.get('hint', '')
        result = self.capture_manager.create_capture_file(user_hint)
        
        if result['success']:
            return {
                'handled': True,
                'success': True,
                'operation': 'capture_created',
                'capture_id': result['capture_id'],
                'response': self._format_capture_success_response(result),
                'next_steps': [...]
            }
        # ... rest of existing code
```

**New Method:**
```python
def _handle_direct_import(self, file_paths: List[str]) -> Dict[str, Any]:
    """Handle direct file import mode"""
    result = self.capture_manager.import_files_directly(file_paths)
    
    if result['success']:
        return {
            'handled': True,
            'success': True,
            'operation': 'direct_import_completed',
            'response': self._format_direct_import_response(result),
            'brain_integration': {
                'tier': 'Tier 1 Working Memory',
                'total_files': result['total_files'],
                'successful_imports': result['successful_imports'],
                'failed_imports': result['failed_imports']
            }
        }
    else:
        return {
            'handled': True,
            'success': False,
            'operation': 'direct_import_failed',
            'error': 'All file imports failed',
            'response': self._format_direct_import_failure_response(result)
        }

def _format_direct_import_response(self, result: Dict[str, Any]) -> str:
    """Format success response for direct file import"""
    response = f"""
🧠 **Direct Import Completed!** 

✅ **Batch Import Summary**
- **Total Files:** {result['total_files']}
- **Successful:** {result['successful_imports']}
- **Failed:** {result['failed_imports']}

📊 **Import Details:**
"""
    
    for item in result['results']:
        if item['success']:
            response += f"\n✅ `{Path(item['file']).name}`"
            response += f"\n   - Conversation ID: `{item['conversation_id']}`"
            response += f"\n   - Messages: {item['messages_imported']}"
            response += f"\n   - Entities: {item['entities_extracted']}"
        else:
            response += f"\n❌ `{Path(item['file']).name}`"
            response += f"\n   - Error: {item['error']}"
    
    response += """

🔗 **Context Continuity NOW ACTIVE**
All imported conversations are now in CORTEX working memory!

🎉 **No template files created** - Direct import mode!
"""
    
    return response.strip()
```

---

### Phase 4: Pattern Matching Enhancement (15 min)

**File:** `src/conversation_capture/command_processor.py`

**Update `_match_command_pattern`:**
```python
def _match_command_pattern(self, user_input: str) -> Optional[Dict[str, Any]]:
    """Match user input against command patterns"""
    for command_type, patterns in self.command_patterns.items():
        for pattern in patterns:
            match = re.search(pattern, user_input, re.IGNORECASE)
            if match:
                params = {}
                
                # Extract file parameters for direct mode
                if command_type == 'capture':
                    # Check for file: parameters
                    file_matches = re.findall(r'file:([^\s]+)', user_input, re.IGNORECASE)
                    if file_matches:
                        params['files'] = file_matches
                        params['mode'] = 'direct'
                    else:
                        params['mode'] = 'template'
                        # Extract optional hint
                        hint_match = re.search(r'about\s+(.*)', user_input, re.IGNORECASE)
                        if hint_match:
                            params['hint'] = hint_match.group(1)
                
                # ... rest of existing parameter extraction
                
                return {
                    'command': command_type,
                    'params': params,
                    'matched_pattern': pattern
                }
    return None
```

---

### Phase 5: Testing & Validation (30 min)

**Test Cases:**

1. **Template Mode (No Parameters)**
   ```python
   Input: "capture conversation"
   Expected: Creates template file, returns capture_id
   ```

2. **Direct Mode (Single File)**
   ```python
   Input: "capture conversation file:conv1.md"
   Expected: Reads conv1.md, imports to Tier 1, no template created
   ```

3. **Direct Mode (Multiple Files)**
   ```python
   Input: "capture conversation file:conv1.md file:conv2.md file:conv3.md"
   Expected: Batch import all 3 files, summary report
   ```

4. **Direct Mode (File Not Found)**
   ```python
   Input: "capture conversation file:nonexistent.md"
   Expected: Error report, no crash
   ```

5. **Direct Mode (Invalid Content)**
   ```python
   Input: "capture conversation file:empty.md" (file has no conversation)
   Expected: Error report with helpful message
   ```

6. **Mixed Mode (Should Default to Direct)**
   ```python
   Input: "capture conversation about auth file:conv.md"
   Expected: Direct mode takes precedence (file parameter present)
   ```

---

## 📊 Success Criteria

✅ **Template Mode Still Works** - Existing users unaffected  
✅ **Direct Mode Functional** - Files imported without template  
✅ **Batch Import Support** - Multiple files processed  
✅ **Error Handling** - Graceful failures with helpful messages  
✅ **No Regression** - All existing tests pass  
✅ **Performance** - Direct mode faster than template mode  

---

## 🚀 Usage Examples

### Example 1: Existing Workflow (Unchanged)
```
User: "capture conversation"
CORTEX: Creates template file, instructions provided

User: [pastes conversation, saves file]

User: "import conversation capture_20251118_143022_a1b2c3d4"
CORTEX: Imports to Tier 1, context active
```

---

### Example 2: Direct Import (New)
```
User: "capture conversation file:copilot-chat-2025-11-18.md"
CORTEX: ✅ Direct Import Completed!

        Total Files: 1
        Successful: 1
        
        ✅ copilot-chat-2025-11-18.md
           - Conversation ID: conv_20251118_143530_x9y8z7w6
           - Messages: 12
           - Entities: 8 (files, classes, functions)
        
        🔗 Context Continuity NOW ACTIVE
        🎉 No template files created - Direct import mode!
```

---

### Example 3: Batch Import
```
User: "capture conversation file:conv1.md file:conv2.md file:conv3.md"
CORTEX: ✅ Direct Import Completed!

        Total Files: 3
        Successful: 3
        
        ✅ conv1.md
           - Conversation ID: conv_20251118_143530_x9y8z7w6
           - Messages: 8
           - Entities: 5
        
        ✅ conv2.md
           - Conversation ID: conv_20251118_143531_a1b2c3d4
           - Messages: 15
           - Entities: 12
        
        ✅ conv3.md
           - Conversation ID: conv_20251118_143532_e5f6g7h8
           - Messages: 20
           - Entities: 18
        
        🔗 All conversations now in CORTEX working memory!
```

---

### Example 4: Partial Failure
```
User: "capture conversation file:good.md file:bad.md file:missing.md"
CORTEX: ⚠️ Partial Import Completed

        Total Files: 3
        Successful: 1
        Failed: 2
        
        ✅ good.md
           - Conversation ID: conv_20251118_143530_x9y8z7w6
           - Messages: 8
        
        ❌ bad.md
           - Error: No conversation messages found
        
        ❌ missing.md
           - Error: File not found or not readable
        
        ℹ️ 1 conversation imported successfully
```

---

## 🔧 Implementation Checklist

- [ ] Phase 1: Command detection enhancement (30 min)
- [ ] Phase 2: Direct import handler (60 min)
- [ ] Phase 3: Command processor integration (30 min)
- [ ] Phase 4: Pattern matching enhancement (15 min)
- [ ] Phase 5: Testing & validation (30 min)

**Total Estimated Time:** 2.5 hours

---

## 📝 Notes

**Backward Compatibility:** Existing template mode unchanged - users who don't provide file parameters get the same experience as before.

**File Path Resolution:** Support both absolute and relative paths. Relative paths resolved from workspace root.

**Error Handling:** Each file processed independently - one failure doesn't stop the batch.

**Performance:** Direct mode bypasses template creation/editing steps, resulting in faster imports.

**Security:** Validate file paths to prevent directory traversal attacks.

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Repository:** github.com/asifhussain60/CORTEX
