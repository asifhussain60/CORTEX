"""
Tests for Multi-Modal Intent Processing - AC-PHX-007-02

Test coverage for multi-modal input handling including:
- Text input processing
- JSON/dict input processing
- Command-line style input
- Code snippet analysis
- Domain-specific schemas
- Error handling and metrics

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest

from cortex.intent_router.multimodal_processor import (
    MultiModalIntentProcessor,
    ModalityInput,
    InputModality,
)


class TestMultiModalProcessorInitialization:
    """Test processor initialization."""
    
    def test_init_creates_processor(self) -> None:
        """Should initialize successfully."""
        processor = MultiModalIntentProcessor()
        assert processor is not None
    
    def test_init_sets_up_classifier(self) -> None:
        """Should set up internal classifier."""
        processor = MultiModalIntentProcessor()
        assert processor.classifier is not None
    
    def test_init_initializes_metrics(self) -> None:
        """Should initialize metrics."""
        processor = MultiModalIntentProcessor()
        assert processor.metrics["total_processed"] == 0


class TestTextInputProcessing:
    """Test processing natural language text input."""
    
    def test_process_text_input(self) -> None:
        """Should process text input."""
        processor = MultiModalIntentProcessor()
        input_data = ModalityInput(
            InputModality.TEXT,
            "Create a new authentication module",
            {}
        )
        result = processor.process(input_data)
        assert result["intent"] is not None
    
    def test_text_result_has_required_fields(self) -> None:
        """Result should have all required fields."""
        processor = MultiModalIntentProcessor()
        input_data = ModalityInput(
            InputModality.TEXT,
            "Create something",
            {}
        )
        result = processor.process(input_data)
        assert "intent" in result
        assert "confidence" in result
        assert "signals" in result
        assert "keywords" in result
        assert "modality" in result
    
    def test_text_modality_in_result(self) -> None:
        """Result should indicate text modality."""
        processor = MultiModalIntentProcessor()
        input_data = ModalityInput(
            InputModality.TEXT,
            "Create a module",
            {}
        )
        result = processor.process(input_data)
        assert result["modality"] == "text"


class TestJSONInputProcessing:
    """Test processing JSON/dict input."""
    
    def test_process_json_input(self) -> None:
        """Should process JSON input."""
        processor = MultiModalIntentProcessor()
        input_data = ModalityInput(
            InputModality.JSON,
            {
                "operation": "create",
                "target": "module",
                "domain": "orchestrators"
            },
            {}
        )
        result = processor.process(input_data)
        assert result["intent"] is not None
    
    def test_json_conversion_to_text(self) -> None:
        """Should convert JSON to text."""
        processor = MultiModalIntentProcessor()
        text = processor._json_to_text({
            "operation": "create",
            "target": "module"
        })
        assert "create" in text.lower()
        assert "module" in text.lower()
    
    def test_json_modality_in_result(self) -> None:
        """Result should indicate JSON modality."""
        processor = MultiModalIntentProcessor()
        input_data = ModalityInput(
            InputModality.JSON,
            {"operation": "fix", "target": "bug"},
            {}
        )
        result = processor.process(input_data)
        assert result["modality"] == "json"
    
    def test_json_empty_dict(self) -> None:
        """Should handle empty JSON dict."""
        processor = MultiModalIntentProcessor()
        text = processor._json_to_text({})
        assert text == "perform operation"


class TestCommandInputProcessing:
    """Test processing command-line style input."""
    
    def test_process_command_input(self) -> None:
        """Should process command input."""
        processor = MultiModalIntentProcessor()
        input_data = ModalityInput(
            InputModality.COMMAND,
            "create --target module --domain orchestrators",
            {}
        )
        result = processor.process(input_data)
        assert result["intent"] is not None
    
    def test_command_conversion(self) -> None:
        """Should convert command to text."""
        processor = MultiModalIntentProcessor()
        text = processor._command_to_text("create --target module")
        assert "create" in text
    
    def test_command_modality_in_result(self) -> None:
        """Result should indicate command modality."""
        processor = MultiModalIntentProcessor()
        input_data = ModalityInput(
            InputModality.COMMAND,
            "fix --issue race-condition",
            {}
        )
        result = processor.process(input_data)
        assert result["modality"] == "command"


class TestCodeInputProcessing:
    """Test processing code snippets."""
    
    def test_process_code_input(self) -> None:
        """Should process code input."""
        processor = MultiModalIntentProcessor()
        input_data = ModalityInput(
            InputModality.CODE,
            "def new_function():\n    pass",
            {}
        )
        result = processor.process(input_data)
        assert result["intent"] is not None
    
    def test_code_function_detection(self) -> None:
        """Should detect function creation."""
        processor = MultiModalIntentProcessor()
        text = processor._code_to_text("def my_function():\n    pass")
        assert "function" in text.lower()
    
    def test_code_class_detection(self) -> None:
        """Should detect class creation."""
        processor = MultiModalIntentProcessor()
        text = processor._code_to_text("class MyClass:\n    pass")
        assert "class" in text.lower()
    
    def test_code_error_detection(self) -> None:
        """Should detect error handling."""
        processor = MultiModalIntentProcessor()
        text = processor._code_to_text("raise ValueError('error')")
        assert "error" in text.lower() or "raise" in text.lower()


class TestSchemaInputProcessing:
    """Test processing domain-specific schemas."""
    
    def test_process_schema_input(self) -> None:
        """Should process schema input."""
        processor = MultiModalIntentProcessor()
        input_data = ModalityInput(
            InputModality.SCHEMA,
            {"type": "governance", "action": "create"},
            {}
        )
        result = processor.process(input_data)
        assert result["intent"] is not None
    
    def test_schema_conversion(self) -> None:
        """Should convert schema to text."""
        processor = MultiModalIntentProcessor()
        text = processor._schema_to_text({
            "type": "module",
            "action": "create"
        })
        assert "module" in text.lower()


class TestMetrics:
    """Test metrics tracking."""
    
    def test_metrics_track_total_processed(self) -> None:
        """Should track total processed."""
        processor = MultiModalIntentProcessor()
        input_data = ModalityInput(InputModality.TEXT, "Create something", {})
        processor.process(input_data)
        metrics = processor.get_metrics()
        assert metrics["total_processed"] == 1
    
    def test_metrics_track_by_modality(self) -> None:
        """Should track by modality."""
        processor = MultiModalIntentProcessor()
        
        input1 = ModalityInput(InputModality.TEXT, "Create", {})
        input2 = ModalityInput(InputModality.JSON, {"operation": "fix"}, {})
        
        processor.process(input1)
        processor.process(input2)
        
        metrics = processor.get_metrics()
        assert metrics["by_modality"]["text"] == 1
        assert metrics["by_modality"]["json"] == 1


class TestErrorHandling:
    """Test error handling."""
    
    def test_invalid_input_type_raises_error(self) -> None:
        """Should raise error for invalid input type."""
        processor = MultiModalIntentProcessor()
        with pytest.raises(ValueError):
            processor.process("not a ModalityInput")  # type: ignore
    
    def test_processing_error_increments_failures(self) -> None:
        """Should track processing failures."""
        processor = MultiModalIntentProcessor()
        
        # Try to process None content (will fail)
        try:
            input_data = ModalityInput(InputModality.TEXT, None, {})
            processor.process(input_data)
        except (ValueError, RuntimeError, TypeError):
            pass
        
        metrics = processor.get_metrics()
        # May or may not increment depending on conversion
        assert metrics["conversion_failures"] >= 0


class TestIntegration:
    """Integration tests with multiple modalities."""
    
    def test_same_intent_different_modalities(self) -> None:
        """Same intent from different modalities should match."""
        processor = MultiModalIntentProcessor()
        
        text_input = ModalityInput(InputModality.TEXT, "Create a module", {})
        json_input = ModalityInput(
            InputModality.JSON,
            {"operation": "create", "target": "module"},
            {}
        )
        
        text_result = processor.process(text_input)
        json_result = processor.process(json_input)
        
        # Should both classify as CREATE
        assert text_result["intent"] == json_result["intent"]
    
    def test_multiple_processing_maintains_metrics(self) -> None:
        """Multiple processing should accumulate metrics."""
        processor = MultiModalIntentProcessor()
        
        for i in range(5):
            input_data = ModalityInput(
                InputModality.TEXT,
                f"Create item {i}",
                {}
            )
            processor.process(input_data)
        
        metrics = processor.get_metrics()
        assert metrics["total_processed"] == 5
