"""
Mermaid Sequence Diagram Generator.

Generates Mermaid.js sequence diagrams from interaction metadata.
Supports synchronous/asynchronous messages, returns, notes, and activation blocks.

AC-ID: LENS-DASH-011
Author: Asif Hussain
Phase: 14
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class Participant:
    """Represents a participant in the sequence diagram."""

    name: str
    alias: Optional[str] = None

    def to_mermaid(self) -> str:
        """
        Convert to Mermaid participant format.

        Returns:
            Mermaid participant declaration

        Example:
            >>> participant = Participant("Client", "C")
            >>> participant.to_mermaid()
            'participant C as Client'
        """
        if self.alias:
            return f"participant {self.alias} as {self.name}"
        return f"participant {self.name}"


@dataclass
class Message:
    """Represents a message between participants."""

    from_participant: str
    to_participant: str
    text: str
    message_type: str  # sync, async, return, note

    def to_mermaid(self) -> str:
        """
        Convert to Mermaid message format.

        Returns:
            Mermaid message string with appropriate arrow

        Message Types:
            - sync: Solid arrow (->>)
            - async: Open arrow (-)
            - return: Dotted arrow (-->>)
            - note: Note over participant

        Example:
            >>> msg = Message("Client", "Server", "request()", "sync")
            >>> msg.to_mermaid()
            'Client->>Server: request()'
        """
        if self.message_type == "note":
            return f"Note over {self.to_participant}: {self.text}"
        elif self.message_type == "sync":
            return f"{self.from_participant}->>{self.to_participant}: {self.text}"
        elif self.message_type == "async":
            return f"{self.from_participant}-){self.to_participant}: {self.text}"
        elif self.message_type == "return":
            return f"{self.from_participant}-->>{self.to_participant}: {self.text}"
        else:
            # Default to sync
            return f"{self.from_participant}->>{self.to_participant}: {self.text}"


@dataclass
class ActivationBlock:
    """Represents an activation block for a participant."""

    participant: str

    def to_mermaid_activate(self) -> str:
        """
        Generate activation statement.

        Returns:
            Mermaid activate statement

        Example:
            >>> block = ActivationBlock("Server")
            >>> block.to_mermaid_activate()
            'activate Server'
        """
        return f"activate {self.participant}"

    def to_mermaid_deactivate(self) -> str:
        """
        Generate deactivation statement.

        Returns:
            Mermaid deactivate statement

        Example:
            >>> block = ActivationBlock("Server")
            >>> block.to_mermaid_deactivate()
            'deactivate Server'
        """
        return f"deactivate {self.participant}"


class MermaidSequenceDiagramGenerator:
    """
    Generates Mermaid.js sequence diagrams from interaction metadata.

    Supports:
    - Synchronous and asynchronous messages
    - Return messages
    - Notes
    - Activation blocks (lifeline highlighting)
    - Auto-numbering of messages

    Example:
        >>> generator = MermaidSequenceDiagramGenerator()
        >>> diagram = generator.generate_diagram(interactions)
        >>> generator.generate_to_file(interactions, Path("sequence.mmd"))
    """

    def __init__(self, auto_number: bool = True) -> None:
        """
        Initialize Mermaid Sequence Diagram Generator.

        Args:
            auto_number: Enable automatic message numbering
        """
        self.auto_number = auto_number

    def generate_diagram(self, interactions: list[dict[str, Any]]) -> str:
        """
        Generate Mermaid sequence diagram from interactions.

        Args:
            interactions: List of interaction dictionaries with keys:
                        - from: Source participant name
                        - to: Target participant name
                        - message: Message text
                        - type: Message type (sync/async/return/note)
                        - activate: Optional participant to activate
                        - deactivate: Optional participant to deactivate

        Returns:
            Mermaid diagram as string

        Example:
            >>> interactions = [
            ...     {
            ...         "from": "Client",
            ...         "to": "Server",
            ...         "message": "request()",
            ...         "type": "sync",
            ...     },
            ...     {
            ...         "from": "Server",
            ...         "to": "Client",
            ...         "message": "return response",
            ...         "type": "return",
            ...     }
            ... ]
            >>> diagram = generator.generate_diagram(interactions)
            >>> "sequenceDiagram" in diagram
            True
            >>> "Client->>Server: request()" in diagram
            True
        """
        lines = ["sequenceDiagram"]

        if self.auto_number:
            lines.append("  autonumber")
        lines.append("")

        # Extract unique participants
        participants = self._extract_participants(interactions)

        # Declare participants
        for participant in participants:
            lines.append(f"  {participant.to_mermaid()}")

        if participants:
            lines.append("")

        # Generate interactions
        for interaction in interactions:
            # Handle activation
            if "activate" in interaction:
                block = ActivationBlock(interaction["activate"])
                lines.append(f"  {block.to_mermaid_activate()}")

            # Generate message
            message = Message(
                from_participant=interaction.get("from", ""),
                to_participant=interaction["to"],
                text=interaction["message"],
                message_type=interaction["type"],
            )
            lines.append(f"  {message.to_mermaid()}")

            # Handle deactivation
            if "deactivate" in interaction:
                block = ActivationBlock(interaction["deactivate"])
                lines.append(f"  {block.to_mermaid_deactivate()}")

        return "\n".join(lines)

    def _extract_participants(
        self, interactions: list[dict[str, Any]]
    ) -> list[Participant]:
        """
        Extract unique participants from interactions.

        Args:
            interactions: List of interaction dictionaries

        Returns:
            List of Participant objects in order of first appearance
        """
        seen = set()
        participants = []

        for interaction in interactions:
            # Add 'from' participant
            from_name = interaction.get("from", "")
            if from_name and from_name not in seen:
                seen.add(from_name)
                participants.append(Participant(name=from_name))

            # Add 'to' participant
            to_name = interaction.get("to", "")
            if to_name and to_name not in seen:
                seen.add(to_name)
                participants.append(Participant(name=to_name))

        return participants

    def generate_to_file(
        self, interactions: list[dict[str, Any]], output_path: Path
    ) -> None:
        """
        Generate Mermaid diagram to file.

        Args:
            interactions: List of interaction dictionaries
            output_path: Output file path (.mmd extension recommended)

        Example:
            >>> generator.generate_to_file(interactions, Path("sequence.mmd"))
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        diagram = self.generate_diagram(interactions)

        with open(output_path, "w") as f:
            f.write(diagram)
