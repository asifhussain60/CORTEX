# src.tier1.test_tier1

CORTEX Tier 1: Unit Tests
Comprehensive test suite for Tier 1 Working Memory

Task 1.7: Unit Testing
Duration: 1.5 hours
Target: 15 tests, 95% coverage

## Functions

### `temp_dir()`

Create temporary directory for tests

### `db_path(temp_dir)`

Create temporary database path

### `log_path(temp_dir)`

Create temporary log path

### `conversation_manager(db_path)`

Create ConversationManager instance

### `entity_extractor()`

Create EntityExtractor instance

### `file_tracker()`

Create FileTracker instance

### `request_logger(log_path)`

Create RequestLogger instance

### `tier1_api(db_path, log_path)`

Create Tier1API instance

### `test_create_conversation(conversation_manager)`

Test creating a conversation

### `test_add_message(conversation_manager)`

Test adding messages to conversation

### `test_fifo_enforcement(conversation_manager)`

Test FIFO queue enforcement (20 conversation limit)

### `test_entity_tracking(conversation_manager)`

Test entity extraction and tracking

### `test_file_tracking(conversation_manager)`

Test file modification tracking

### `test_extract_file_paths(entity_extractor)`

Test file path extraction

### `test_extract_intents(entity_extractor)`

Test intent extraction

### `test_extract_technical_terms(entity_extractor)`

Test technical term extraction

### `test_file_pattern_detection(file_tracker)`

Test file pattern grouping

### `test_file_statistics(file_tracker)`

Test file statistics generation

### `test_log_request_response(request_logger)`

Test logging requests and responses

### `test_request_statistics(request_logger)`

Test request logging statistics

### `test_api_start_conversation(tier1_api)`

Test starting conversation via API

### `test_api_process_message(tier1_api)`

Test processing message with automatic extraction

### `test_api_conversation_history(tier1_api)`

Test getting conversation history

### `test_full_conversation_workflow(tier1_api)`

Test complete conversation workflow
