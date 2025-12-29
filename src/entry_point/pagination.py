"""
Pagination Manager for Chat Output

Provides simple persistence for paged outputs to avoid chat length limits.

Pages are stored per conversation under:
  cortex-brain/corpus-callosum/output_pages/{conversation_id}.json

Schema:
{
  "conversation_id": str,
  "continuation_id": str,
  "total": int,
  "current": int,   # 0-based index of last served page
  "pages": [str],
  "created": iso timestamp
}
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any
import json
import uuid

from src.config import config


@dataclass
class PaginationState:
    conversation_id: str
    continuation_id: str
    total: int
    current: int
    pages: List[str]
    created: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conversation_id": self.conversation_id,
            "continuation_id": self.continuation_id,
            "total": self.total,
            "current": self.current,
            "pages": self.pages,
            "created": self.created,
        }


class PaginationManager:
    """Manage persisted paged outputs for a conversation."""

    def __init__(self) -> None:
        brain = config.brain_path
        self.base_dir = Path(brain) / "corpus-callosum" / "output_pages"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _state_path(self, conversation_id: str) -> Path:
        safe_id = conversation_id or "default"
        # Use a single file per conversation; update as we serve pages
        return self.base_dir / f"{safe_id}.json"

    def create_pagination(self, conversation_id: Optional[str], pages: List[str]) -> str:
        """Create a pagination state and persist it; returns continuation_id."""
        conv = conversation_id or "default"
        cont_id = f"CONT_{uuid.uuid4().hex[:8]}"
        state = PaginationState(
            conversation_id=conv,
            continuation_id=cont_id,
            total=len(pages),
            current=0,  # 0 served when first page returned by formatter
            pages=pages,
            created=datetime.now().isoformat(),
        )
        with open(self._state_path(conv), "w", encoding="utf-8") as f:
            json.dump(state.to_dict(), f, ensure_ascii=False, indent=2)
        return cont_id

    def get_next(self, conversation_id: Optional[str]) -> Optional[str]:
        """Return the next page content for a conversation, or None if no more."""
        conv = conversation_id or "default"
        path = self._state_path(conv)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            return None

        current = int(data.get("current", 0))
        total = int(data.get("total", 0))
        pages = data.get("pages", [])
        if not pages or current + 1 >= total:
            # Clean up when done
            try:
                path.unlink(missing_ok=True)
            except Exception:
                pass
            return None

        next_index = current + 1
        data["current"] = next_index
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        header = f"Part {next_index+1}/{total}\n\n"
        tail = "\n\n_Say 'continue' again for the next part, or 'stop' to end._"
        return header + pages[next_index] + tail
