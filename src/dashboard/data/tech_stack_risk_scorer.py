"""
Phase 8.2: Technology Risk Scorer (Backend)

GREEN phase: Implements risk scoring system that integrates EOL data from
endoflife.date API and calculates comprehensive risk scores.

Risk Formula: Age(30%) + EOL(40%) + CVE(30%) = Total Risk (0-100)
"""

import requests
from datetime import datetime
from typing import Dict, Optional, Any, List
from dateutil.relativedelta import relativedelta


class TechStackRiskScorer:
    """
    Scores technology risk based on age, EOL proximity, and CVE count.
    
    Integrates with endoflife.date API to fetch EOL dates and calculates
    comprehensive risk scores for dashboard visualization.
    
    Formula:
    - Age Score (30%): months_since_update / 24 months * 30
    - EOL Score (40%): max(0, (12 - months_to_eol) / 12) * 40
    - CVE Score (30%): min(cve_count / 10, 1.0) * 30
    """
    
    def __init__(self):
        """Initialize risk scorer with empty cache."""
        self._cache: Dict[str, Any] = {}
        self._tech_name_mapping = {
            ".net": "dotnet",
            ".net framework": "dotnetfx",
            "node.js": "nodejs",
            "nodejs": "nodejs",
            "postgresql": "postgresql",
            "redis": "redis",
            "python": "python",
            "go": "go",
            "java": "java",
            "mongodb": "mongodb",
            "mysql": "mysql",
            "sql server": "mssql",
            "elasticsearch": "elasticsearch"
        }
    
    def fetch_eol_data(self, tech_name: str, version: str) -> Optional[Dict[str, Any]]:
        """
        Fetch EOL data from endoflife.date API.
        
        Args:
            tech_name: Technology name (e.g., "dotnet", "nodejs")
            version: Version to lookup (e.g., "8", "20")
            
        Returns:
            EOL data dict with cycle, eol, releaseDate fields, or None if not found
        """
        # Check cache first
        cache_key = self.get_cache_key(tech_name, version)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        try:
            url = f"https://endoflife.date/api/{tech_name}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            # Find matching version
            for entry in data:
                if str(entry.get("cycle")) == str(version):
                    # Cache the result
                    self._cache[cache_key] = entry
                    return entry
            
            return None
            
        except Exception:
            return None
    
    def get_cache_key(self, tech_name: str, version: str) -> str:
        """
        Generate cache key for tech+version combination.
        
        Args:
            tech_name: Technology name
            version: Version string
            
        Returns:
            Cache key string
        """
        return f"{tech_name}:{version}"
    
    def map_tech_name_to_api(self, tech_name: str) -> str:
        """
        Map technology name to endoflife.date API endpoint name.
        
        Args:
            tech_name: Display name (e.g., ".NET", "Node.js")
            
        Returns:
            API endpoint name (e.g., "dotnet", "nodejs")
        """
        normalized = tech_name.lower()
        return self._tech_name_mapping.get(normalized, normalized)
    
    def calculate_age_score(self, months_since_update: int) -> float:
        """
        Calculate age risk score (0-30 points).
        
        Formula: min(months_since_update / 24, 1.0) * 30
        
        Args:
            months_since_update: Months since last update/release
            
        Returns:
            Age score (0-30)
        """
        if months_since_update < 0:
            return 0.0
        
        ratio = min(months_since_update / 24.0, 1.0)
        return ratio * 30.0
    
    def calculate_eol_score(self, months_to_eol: Optional[int]) -> float:
        """
        Calculate EOL proximity risk score (0-40 points).
        
        Formula: max(0, (12 - months_to_eol) / 12) * 40
        Score increases as EOL approaches. >12 months = 0, <0 months = 40.
        
        Args:
            months_to_eol: Months until EOL (negative if already EOL)
            
        Returns:
            EOL score (0-40)
        """
        if months_to_eol is None:
            return 0.0  # No EOL data = no penalty
        
        ratio = max(0.0, (12.0 - months_to_eol) / 12.0)
        ratio = min(ratio, 1.0)  # Cap at 1.0
        return ratio * 40.0
    
    def calculate_cve_score(self, cve_count: int) -> float:
        """
        Calculate CVE risk score (0-30 points).
        
        Formula: min(cve_count / 10, 1.0) * 30
        
        Args:
            cve_count: Number of CVEs
            
        Returns:
            CVE score (0-30)
        """
        if cve_count < 0:
            return 0.0
        
        ratio = min(cve_count / 10.0, 1.0)
        return ratio * 30.0
    
    def calculate_risk_score(
        self,
        months_since_update: int,
        months_to_eol: Optional[int],
        cve_count: int
    ) -> float:
        """
        Calculate total risk score (0-100).
        
        Args:
            months_since_update: Months since last update
            months_to_eol: Months until EOL (None if no EOL)
            cve_count: Number of CVEs
            
        Returns:
            Total risk score (0-100)
        """
        age_score = self.calculate_age_score(months_since_update)
        eol_score = self.calculate_eol_score(months_to_eol)
        cve_score = self.calculate_cve_score(cve_count)
        
        total = age_score + eol_score + cve_score
        return min(max(total, 0.0), 100.0)  # Clamp to [0, 100]
    
    def calculate_months_since_update(self, release_date: str) -> int:
        """
        Calculate months between release date and now.
        
        Args:
            release_date: ISO date string (YYYY-MM-DD)
            
        Returns:
            Months since release (999 if invalid date)
        """
        try:
            release = datetime.strptime(release_date, "%Y-%m-%d")
            delta = relativedelta(datetime.now(), release)
            return delta.years * 12 + delta.months
        except (ValueError, TypeError):
            return 999  # Sentinel for invalid date
    
    def calculate_months_to_eol(self, eol_date: str) -> int:
        """
        Calculate months until EOL date.
        
        Args:
            eol_date: ISO date string (YYYY-MM-DD)
            
        Returns:
            Months to EOL (negative if already EOL, 999 if invalid date)
        """
        try:
            eol = datetime.strptime(eol_date, "%Y-%m-%d")
            delta = relativedelta(eol, datetime.now())
            return delta.years * 12 + delta.months
        except (ValueError, TypeError):
            return 999  # Sentinel for invalid date
    
    def enrich_technology(self, tech: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich technology dict with EOL data and risk score.
        
        Args:
            tech: Technology dict with name, version, cve_count
            
        Returns:
            Enriched dict with eol_date, months_to_eol, risk_score
        """
        enriched = tech.copy()
        
        # Get technology details
        name = tech.get("name", "")
        version = tech.get("version")
        cve_count = tech.get("cve_count", 0)
        
        # Initialize EOL fields
        enriched["eol_date"] = None
        enriched["months_to_eol"] = None
        enriched["months_since_update"] = 999  # Unknown by default
        
        # Skip if no version
        if not version or version == "unknown":
            enriched["risk_score"] = self.calculate_risk_score(
                months_since_update=999,
                months_to_eol=None,
                cve_count=cve_count
            )
            return enriched
        
        # Map tech name to API name
        api_name = self.map_tech_name_to_api(name)
        
        # Fetch EOL data
        eol_data = self.fetch_eol_data(api_name, version)
        
        if eol_data:
            # Extract EOL date
            eol = eol_data.get("eol")
            if eol and eol is not False:  # Handle both None and False
                enriched["eol_date"] = eol
                enriched["months_to_eol"] = self.calculate_months_to_eol(eol)
            
            # Extract release date for age calculation
            release_date = eol_data.get("releaseDate")
            if release_date:
                enriched["months_since_update"] = self.calculate_months_since_update(release_date)
        
        # Calculate risk score
        enriched["risk_score"] = self.calculate_risk_score(
            months_since_update=enriched["months_since_update"],
            months_to_eol=enriched["months_to_eol"],
            cve_count=cve_count
        )
        
        return enriched
    
    def enrich_tech_stack(self, tech_stack: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich complete tech-stack.json with EOL data and risk scores.
        
        Args:
            tech_stack: Tech stack dict with backend, frontend, database sections
            
        Returns:
            Enriched tech stack with risk data for all technologies
        """
        enriched = tech_stack.copy()
        
        # Enrich each category
        for category in ["backend", "frontend", "database", "devops"]:
            if category in enriched:
                enriched[category] = [
                    self.enrich_technology(tech)
                    for tech in enriched[category]
                ]
        
        # Preserve summary section
        if "summary" in tech_stack:
            enriched["summary"] = tech_stack["summary"].copy()
        
        return enriched
