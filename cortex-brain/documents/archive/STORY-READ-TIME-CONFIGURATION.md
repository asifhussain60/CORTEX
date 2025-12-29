# Story Read Time Configuration

**Feature:** Configurable Story Length Validation  
**Status:** ✅ Implemented and Tested  
**Configuration File:** `cortex.config.json`  
**Module:** `src/operations/modules/apply_narrator_voice_module.py`

---

## Overview

The CORTEX story refresh operation now supports configurable read time targets with flexible enforcement modes. This allows you to:

- Set custom read time targets (e.g., 15-20 min, 25-30 min, 45-60 min)
- Adjust validation tolerances
- Choose between blocking (enforced) or warning (advisory) mode
- Maintain consistent story length across versions

---

## Configuration

### Location

Add to `cortex.config.json`:

```json
{
  "story_refresh": {
    "enabled": true,
    "target_read_time_min": 25,
    "target_read_time_max": 30,
    "words_per_minute": 200,
    "tolerance_percent": 7,
    "extended_tolerance_percent": 20,
    "enforce_validation": true,
    "fail_on_critical_length": false
  }
}
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `enabled` | boolean | `true` | Enable/disable read time validation |
| `target_read_time_min` | integer | `25` | Minimum target read time in minutes |
| `target_read_time_max` | integer | `30` | Maximum target read time in minutes |
| `words_per_minute` | integer | `200` | Average reading speed (industry standard) |
| `tolerance_percent` | integer | `7` | Acceptable variance (±%) from target |
| `extended_tolerance_percent` | integer | `20` | Warning threshold (±%) before critical |
| `enforce_validation` | boolean | `true` | Enable validation checks |
| `fail_on_critical_length` | boolean | `false` | Block pipeline on critical length issues |

---

## Validation Thresholds

The module calculates thresholds based on your configuration:

### Example: 25-30 minute target

- **Target Range:** 5,000 - 6,000 words (25-30 min × 200 wpm)
- **Acceptable Range:** 4,650 - 6,420 words (±7% tolerance)
- **Warning Range:** 4,000 - 7,200 words (±20% extended tolerance)
- **Critical:** < 4,000 or > 7,200 words

### Validation Levels

1. **OPTIMAL** ✅
   - Word count within acceptable range
   - No warnings
   - Pipeline continues

2. **SLIGHTLY_SHORT / SLIGHTLY_LONG** ⚠️
   - Outside acceptable but within warning range
   - Warnings displayed with recommendations
   - Pipeline continues

3. **TOO_SHORT / TOO_LONG** ❌
   - Outside warning range (critical)
   - Behavior depends on `fail_on_critical_length`:
     - `true` → Pipeline fails (blocking mode)
     - `false` → Pipeline continues with critical warnings (advisory mode)

---

## Enforcement Modes

### Advisory Mode (Recommended)

**Configuration:**
```json
"fail_on_critical_length": false
```

**Behavior:**
- Validates story length
- Issues warnings for length issues
- Pipeline always completes
- Allows flexibility during development

**Use When:**
- Developing/iterating on story content
- Length targets are guidelines, not hard requirements
- Want visibility without blocking workflow

**Example Output:**
```
[OK] apply_narrator_voice: Narrator voice applied (456 lines, 2654 words, 13.3 min)
    Warnings (4):
      1. CRITICAL: Story too short: 2654 words (13.3 min) - Target: 5,000-6,000 words
      2. Need to add ~2,346 words to meet minimum target
      3. Consider using fuller story version from docs/story/CORTEX-STORY/
      4. Or expand technical details and examples
```

### Blocking Mode (Strict)

**Configuration:**
```json
"fail_on_critical_length": true
```

**Behavior:**
- Validates story length
- Fails pipeline on critical length issues
- Forces correction before completion
- Strict quality gate

**Use When:**
- Publishing production story versions
- Length requirements are mandatory
- Quality assurance before release

**Example Output:**
```
[FAIL] apply_narrator_voice: Story too short: 2654 words (13.3 min) - Target: 5,000-6,000 words
Required module apply_narrator_voice failed, rolling back
Operation: Refresh CORTEX Story
Success: False
```

---

## Common Configurations

### Short Story (15-20 minutes)

```json
"story_refresh": {
  "target_read_time_min": 15,
  "target_read_time_max": 20,
  "words_per_minute": 200,
  "tolerance_percent": 7,
  "extended_tolerance_percent": 20,
  "fail_on_critical_length": false
}
```

- **Target:** 3,000 - 4,000 words
- **Acceptable:** 2,790 - 4,280 words
- **Warning:** 2,400 - 4,800 words

### Medium Story (25-30 minutes) - Default

```json
"story_refresh": {
  "target_read_time_min": 25,
  "target_read_time_max": 30,
  "words_per_minute": 200,
  "tolerance_percent": 7,
  "extended_tolerance_percent": 20,
  "fail_on_critical_length": false
}
```

- **Target:** 5,000 - 6,000 words
- **Acceptable:** 4,650 - 6,420 words
- **Warning:** 4,000 - 7,200 words

### Long Story (45-60 minutes)

```json
"story_refresh": {
  "target_read_time_min": 45,
  "target_read_time_max": 60,
  "words_per_minute": 200,
  "tolerance_percent": 7,
  "extended_tolerance_percent": 20,
  "fail_on_critical_length": false
}
```

- **Target:** 9,000 - 12,000 words
- **Acceptable:** 8,370 - 12,840 words
- **Warning:** 7,200 - 14,400 words

### Lenient Validation

```json
"story_refresh": {
  "target_read_time_min": 25,
  "target_read_time_max": 30,
  "tolerance_percent": 15,
  "extended_tolerance_percent": 40,
  "fail_on_critical_length": false
}
```

- Wider acceptable range (±15%)
- More lenient warnings (±40%)
- Good for exploratory development

### Strict Validation

```json
"story_refresh": {
  "target_read_time_min": 25,
  "target_read_time_max": 30,
  "tolerance_percent": 3,
  "extended_tolerance_percent": 10,
  "fail_on_critical_length": true
}
```

- Narrow acceptable range (±3%)
- Tight warnings (±10%)
- Blocking on critical issues
- Good for production releases

---

## Testing Your Configuration

### 1. Check Current Story Length

```python
from pathlib import Path

story = Path('prompts/shared/story.md').read_text()
words = len([w for w in story.split() if w.strip()])
read_time = round(words / 200, 1)

print(f"Current: {words} words ({read_time} min)")
```

### 2. Test Validation

```python
from src.operations import execute_operation

report = execute_operation("refresh_cortex_story", profile="quick")

print(f"Success: {report.success}")
for module_id in report.modules_executed:
    result = report.module_results.get(module_id)
    if result and 'read_time_status' in result.data:
        print(f"Status: {result.data['read_time_status']}")
        print(f"Words: {result.data['word_count']}")
        print(f"Read Time: {result.data['read_time_minutes']} min")
```

### 3. Review Warnings

Check module output for:
- Validation status (optimal, slightly_short, too_long, etc.)
- Specific recommendations
- Word count gaps

---

## Recommendations

The validation provides actionable recommendations based on status:

### Too Short

```
- Need to add ~2,346 words to meet minimum target
- Consider using fuller story version from docs/story/CORTEX-STORY/
- Or expand technical details and examples
```

### Too Long

```
- Need to trim ~2,000 words to meet maximum target
- Consider condensing technical sections
- Remove redundant explanations
- Or use AI-based summarization for quality
```

### Slightly Short/Long

```
- Consider adding/trimming X words to reach optimal range
```

---

## Integration

### Manual Execution

```bash
python -c "from src.operations import execute_operation; execute_operation('refresh_cortex_story')"
```

### VS Code Command

```
/CORTEX, refresh cortex story
```

### Natural Language

```
refresh the story
update story documentation
```

---

## Troubleshooting

### Validation Not Running

**Check:**
1. `story_refresh.enabled` = `true`
2. `story_refresh.enforce_validation` = `true`
3. Module registered in operations registry

### Unexpected Blocking

**Check:**
1. `fail_on_critical_length` setting
2. Current word count vs. warning thresholds
3. Tolerance percentages

### Configuration Not Applied

**Solution:**
1. Restart Python kernel/process
2. Verify JSON syntax in cortex.config.json
3. Check config module imports

---

## Technical Details

### Module: `apply_narrator_voice_module.py`

**Validation Function:**
```python
def _validate_read_time(self, story_content: str) -> Dict[str, Any]:
    """
    Validate story against configurable read time target.
    
    Reads configuration from cortex.config.json
    Returns validation status and recommendations
    """
```

**Configuration Access:**
```python
from src.config import config

story_config = config.get('story_refresh', {})
min_minutes = story_config.get('target_read_time_min', 25)
max_minutes = story_config.get('target_read_time_max', 30)
```

### Calculation Logic

1. **Word Count:** Filter empty strings, count remaining words
2. **Read Time:** `words / words_per_minute` (rounded to 1 decimal)
3. **Thresholds:**
   - `min_target = min_minutes * words_per_minute`
   - `max_target = max_minutes * words_per_minute`
   - `min_acceptable = min_target * (1 - tolerance / 100)`
   - `max_acceptable = max_target * (1 + tolerance / 100)`
   - `min_warning = min_target * (1 - extended_tolerance / 100)`
   - `max_warning = max_target * (1 + extended_tolerance / 100)`

---

## Version History

- **v2.0** (2025-11-09): Initial configurable validation implementation
  - Added `story_refresh` config section
  - Implemented advisory and blocking modes
  - Integrated with apply_narrator_voice module
  - Tested with 15-20 min and 25-30 min targets

---

## Future Enhancements

1. **AI-Based Trimming/Expansion**
   - Automatically adjust story length to target
   - Maintain narrative quality
   - Intelligent section selection

2. **Multi-Version Support**
   - Short, medium, long story variants
   - Automatic selection based on context
   - Cross-reference consistency

3. **Read Time Analytics**
   - Track story length over time
   - Version comparison
   - Trend analysis

4. **Custom Word Speed Profiles**
   - Technical readers (150 wpm)
   - General readers (200 wpm)
   - Quick skim (300 wpm)

---

**Status:** Production Ready ✅  
**Last Updated:** 2025-11-09  
**Maintainer:** Asif Hussain
