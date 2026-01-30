"""Domain Auto-Detection (STATIC-VIZ-006)."""
from typing import Optional

class DomainDetector:
    def detect(self, url: str, override: Optional[str] = None) -> str:
        if override: return override
        return url.split("/")[-2] if "/" in url else "unknown"
