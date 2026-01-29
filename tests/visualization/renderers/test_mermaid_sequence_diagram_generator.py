"""
Tests for MermaidSequenceDiagramGenerator.

AC-ID: LENS-DASH-011
Author: Asif Hussain
Phase: 14
"""

from pathlib import Path

import pytest

from cortex.visualization.renderers.mermaid_sequence_diagram_generator import (
    MermaidSequenceDiagramGenerator,
    Participant,
    Message,
    ActivationBlock,
)


@pytest.fixture
def sample_interactions() -> list[dict]:
    """Sample interaction data for testing."""
    return [
        {
            "from": "Client",
            "to": "APIGateway",
            "message": "POST /api/users",
            "type": "sync",
        },
        {
            "from": "APIGateway",
            "to": "AuthService",
            "message": "validate_token(token)",
            "type": "sync",
        },
        {
            "from": "AuthService",
            "to": "APIGateway",
            "message": "return valid",
            "type": "return",
        },
        {
            "from": "APIGateway",
            "to": "UserService",
            "message": "create_user(data)",
            "type": "sync",
        },
        {
            "from": "UserService",
            "to": "Database",
            "message": "INSERT INTO users",
            "type": "async",
        },
        {
            "from": "UserService",
            "to": "APIGateway",
            "message": "return user_id",
            "type": "return",
        },
        {
            "from": "APIGateway",
            "to": "Client",
            "message": "return 201 Created",
            "type": "return",
        },
    ]


@pytest.fixture
def generator() -> MermaidSequenceDiagramGenerator:
    """Create generator instance."""
    return MermaidSequenceDiagramGenerator()


class TestParticipant:
    """Test Participant dataclass."""

    def test_initialization(self) -> None:
        """Test Participant initialization."""
        participant = Participant(name="Client", alias="C")
        
        assert participant.name == "Client"
        assert participant.alias == "C"

    def test_to_mermaid(self) -> None:
        """Test Mermaid format."""
        participant = Participant(name="Client", alias="C")
        
        result = participant.to_mermaid()
        
        assert result == "participant C as Client"

    def test_to_mermaid_without_alias(self) -> None:
        """Test Mermaid format without alias."""
        participant = Participant(name="Client")
        
        result = participant.to_mermaid()
        
        assert result == "participant Client"


class TestMessage:
    """Test Message dataclass."""

    def test_initialization(self) -> None:
        """Test Message initialization."""
        message = Message(
            from_participant="Client",
            to_participant="Server",
            text="GET /api",
            message_type="sync",
        )
        
        assert message.from_participant == "Client"
        assert message.to_participant == "Server"
        assert message.text == "GET /api"
        assert message.message_type == "sync"

    def test_to_mermaid_sync(self) -> None:
        """Test synchronous message format."""
        message = Message("Client", "Server", "request()", "sync")
        
        result = message.to_mermaid()
        
        assert result == "Client->>Server: request()"

    def test_to_mermaid_async(self) -> None:
        """Test asynchronous message format."""
        message = Message("Client", "Server", "notify()", "async")
        
        result = message.to_mermaid()
        
        assert result == "Client-)Server: notify()"

    def test_to_mermaid_return(self) -> None:
        """Test return message format."""
        message = Message("Server", "Client", "return result", "return")
        
        result = message.to_mermaid()
        
        assert result == "Server-->>Client: return result"

    def test_to_mermaid_note(self) -> None:
        """Test note format."""
        message = Message("", "Client", "This is a note", "note")
        
        result = message.to_mermaid()
        
        assert result == "Note over Client: This is a note"


class TestActivationBlock:
    """Test ActivationBlock dataclass."""

    def test_initialization(self) -> None:
        """Test ActivationBlock initialization."""
        block = ActivationBlock(participant="Server")
        
        assert block.participant == "Server"

    def test_to_mermaid_activate(self) -> None:
        """Test activation format."""
        block = ActivationBlock(participant="Server")
        
        result = block.to_mermaid_activate()
        
        assert result == "activate Server"

    def test_to_mermaid_deactivate(self) -> None:
        """Test deactivation format."""
        block = ActivationBlock(participant="Server")
        
        result = block.to_mermaid_deactivate()
        
        assert result == "deactivate Server"


class TestMermaidSequenceDiagramGenerator:
    """Test MermaidSequenceDiagramGenerator."""

    def test_initialization(
        self, generator: MermaidSequenceDiagramGenerator
    ) -> None:
        """Test generator initialization."""
        assert generator.auto_number is True

    def test_extract_participants(
        self, generator: MermaidSequenceDiagramGenerator, sample_interactions: list[dict]
    ) -> None:
        """Test extracting unique participants."""
        participants = generator._extract_participants(sample_interactions)
        
        assert len(participants) == 5
        participant_names = {p.name for p in participants}
        assert participant_names == {
            "Client",
            "APIGateway",
            "AuthService",
            "UserService",
            "Database",
        }

    def test_generate_diagram(
        self, generator: MermaidSequenceDiagramGenerator, sample_interactions: list[dict]
    ) -> None:
        """Test generating sequence diagram."""
        result = generator.generate_diagram(sample_interactions)
        
        assert result.startswith("sequenceDiagram")
        assert "autonumber" in result
        assert "participant Client" in result
        assert "Client->>APIGateway: POST /api/users" in result
        assert "APIGateway->>AuthService: validate_token(token)" in result
        assert "UserService-)Database: INSERT INTO users" in result
        assert "APIGateway-->>Client: return 201 Created" in result

    def test_generate_diagram_without_autonumber(self) -> None:
        """Test generating diagram without auto-numbering."""
        generator = MermaidSequenceDiagramGenerator(auto_number=False)
        
        result = generator.generate_diagram([])
        
        assert "sequenceDiagram" in result
        assert "autonumber" not in result

    def test_sync_message_arrow(
        self, generator: MermaidSequenceDiagramGenerator
    ) -> None:
        """Test synchronous message arrow format."""
        interactions = [
            {
                "from": "A",
                "to": "B",
                "message": "sync call",
                "type": "sync",
            }
        ]
        
        result = generator.generate_diagram(interactions)
        
        assert "A->>B: sync call" in result

    def test_async_message_arrow(
        self, generator: MermaidSequenceDiagramGenerator
    ) -> None:
        """Test asynchronous message arrow format."""
        interactions = [
            {
                "from": "A",
                "to": "B",
                "message": "async call",
                "type": "async",
            }
        ]
        
        result = generator.generate_diagram(interactions)
        
        assert "A-)B: async call" in result

    def test_return_message_arrow(
        self, generator: MermaidSequenceDiagramGenerator
    ) -> None:
        """Test return message arrow format."""
        interactions = [
            {
                "from": "B",
                "to": "A",
                "message": "return value",
                "type": "return",
            }
        ]
        
        result = generator.generate_diagram(interactions)
        
        assert "B-->>A: return value" in result

    def test_empty_interactions(
        self, generator: MermaidSequenceDiagramGenerator
    ) -> None:
        """Test generating diagram with no interactions."""
        result = generator.generate_diagram([])
        
        assert result.startswith("sequenceDiagram")
        assert "autonumber" in result

    def test_generate_to_file(
        self, generator: MermaidSequenceDiagramGenerator, sample_interactions: list[dict], tmp_path: Path
    ) -> None:
        """Test generating diagram to file."""
        output_file = tmp_path / "sequence_diagram.mmd"
        
        generator.generate_to_file(sample_interactions, output_file)
        
        assert output_file.exists()
        
        content = output_file.read_text()
        assert "sequenceDiagram" in content
        assert "participant Client" in content

    def test_participant_ordering(
        self, generator: MermaidSequenceDiagramGenerator
    ) -> None:
        """Test participants are declared in order of appearance."""
        interactions = [
            {"from": "C", "to": "B", "message": "msg1", "type": "sync"},
            {"from": "A", "to": "C", "message": "msg2", "type": "sync"},
        ]
        
        result = generator.generate_diagram(interactions)
        
        lines = result.split("\n")
        # Find participant declarations
        participant_lines = [l for l in lines if l.strip().startswith("participant")]
        
        # Should be ordered: C, B, A (order of first appearance)
        assert "participant C" in participant_lines[0]
        assert "participant B" in participant_lines[1]
        assert "participant A" in participant_lines[2]

    def test_activation_blocks(
        self, generator: MermaidSequenceDiagramGenerator
    ) -> None:
        """Test activation blocks for participants."""
        interactions = [
            {
                "from": "Client",
                "to": "Server",
                "message": "request()",
                "type": "sync",
                "activate": "Server",
            },
            {
                "from": "Server",
                "to": "Client",
                "message": "return response",
                "type": "return",
                "deactivate": "Server",
            },
        ]
        
        result = generator.generate_diagram(interactions)
        
        assert "activate Server" in result
        assert "deactivate Server" in result
