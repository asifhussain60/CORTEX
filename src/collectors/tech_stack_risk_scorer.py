"""
Technology Risk Scorer
Calculates risk scores for technologies based on:
- Age score (30%): How old is the version?
- EOL score (40%): End-of-life proximity
- CVE score (30%): Known vulnerabilities

Integrates with endoflife.date API with 7-day caching.
"""

import json
import requests
import sqlite3
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os
import re


class TechStackRiskScorer:
    """Calculate risk scores for technologies in tech stack."""
    
    def __init__(self, cache_db_path: str = None):
        """
        Initialize risk scorer with caching.
        
        Args:
            cache_db_path: Path to SQLite cache database
        """
        if cache_db_path is None:
            cache_dir = os.path.join(os.path.dirname(__file__), '../../cortex-brain/cache')
            os.makedirs(cache_dir, exist_ok=True)
            cache_db_path = os.path.join(cache_dir, 'eol_cache.db')
        
        self.cache_db_path = cache_db_path
        self.api_base_url = 'https://endoflife.date/api'
        self.cache_days = 7
        self._init_cache_db()
    
    def _init_cache_db(self):
        """Initialize SQLite cache database."""
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS eol_cache (
                cache_key TEXT PRIMARY KEY,
                product TEXT,
                version TEXT,
                response_data TEXT,
                cached_at TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def _get_cache_key(self, product: str, version: str) -> str:
        """Generate cache key for product/version."""
        key_string = f"{product}:{version}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_response(self, product: str, version: str) -> Optional[Dict]:
        """Retrieve cached API response if not expired."""
        cache_key = self._get_cache_key(product, version)
        
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT response_data, cached_at FROM eol_cache WHERE cache_key = ?',
            (cache_key,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        response_data, cached_at = row
        cached_datetime = datetime.fromisoformat(cached_at)
        
        # Check if cache expired (7 days)
        if datetime.now() - cached_datetime > timedelta(days=self.cache_days):
            return None
        
        return json.loads(response_data)
    
    def _cache_response(self, product: str, version: str, response_data: Dict):
        """Cache API response."""
        cache_key = self._get_cache_key(product, version)
        
        conn = sqlite3.connect(self.cache_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            '''INSERT OR REPLACE INTO eol_cache 
               (cache_key, product, version, response_data, cached_at)
               VALUES (?, ?, ?, ?, ?)''',
            (cache_key, product, version, json.dumps(response_data), 
             datetime.now().isoformat())
        )
        
        conn.commit()
        conn.close()
    
    def _query_eol_api(self, product: str, version: str) -> Optional[Dict]:
        """Query endoflife.date API for product/version info."""
        # Check cache first
        cached = self._get_cached_response(product, version)
        if cached:
            return cached
        
        # Normalize product name for API
        product_normalized = self._normalize_product_name(product)
        
        try:
            # Query all cycles for product
            url = f"{self.api_base_url}/{product_normalized}.json"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                cycles = response.json()
                
                # Find matching cycle
                for cycle in cycles:
                    cycle_version = str(cycle.get('cycle', ''))
                    if self._version_matches(version, cycle_version):
                        result = {
                            'product': product,
                            'version': version,
                            'cycle': cycle_version,
                            'eol': cycle.get('eol'),
                            'support': cycle.get('support'),
                            'latest': cycle.get('latest'),
                            'releaseDate': cycle.get('releaseDate'),
                            'lts': cycle.get('lts', False)
                        }
                        
                        # Cache successful response
                        self._cache_response(product, version, result)
                        return result
            
            return None
            
        except Exception as e:
            print(f"Error querying EOL API for {product} {version}: {e}")
            return None
    
    def _normalize_product_name(self, product: str) -> str:
        """Normalize product name for endoflife.date API."""
        # Mapping of common product names to API names
        mappings = {
            'dotnet': 'dotnet',
            '.net': 'dotnet',
            '.net framework': 'dotnetfx',
            '.net core': 'dotnet',
            'csharp': 'csharp',
            'c#': 'csharp',
            'entity framework': 'dotnetfx',
            'entityframework': 'dotnetfx',
            'asp.net': 'dotnetfx',
            'asp.net core': 'dotnet',
            'visual studio': 'visual-studio',
            'vs': 'visual-studio',
            'sql server': 'mssqlserver',
            'mssql': 'mssqlserver',
            'nodejs': 'nodejs',
            'node.js': 'nodejs',
            'python': 'python',
            'ubuntu': 'ubuntu',
            'windows': 'windows',
            'docker': 'docker',
            'postgresql': 'postgresql',
            'mysql': 'mysql',
            'redis': 'redis',
            'nginx': 'nginx',
            'apache': 'apache'
        }
        
        product_lower = product.lower().strip()
        return mappings.get(product_lower, product_lower)
    
    def _version_matches(self, version1: str, version2: str) -> bool:
        """Check if two version strings match (major.minor)."""
        def extract_major_minor(v):
            match = re.match(r'(\d+)\.(\d+)', str(v))
            if match:
                return (int(match.group(1)), int(match.group(2)))
            return None
        
        v1 = extract_major_minor(version1)
        v2 = extract_major_minor(version2)
        
        return v1 and v2 and v1 == v2
    
    def calculate_age_score(self, release_date: Optional[str]) -> float:
        """
        Calculate age score (0-100, higher = more risk).
        
        Args:
            release_date: Release date in ISO format (YYYY-MM-DD)
        
        Returns:
            Age score (0-100)
        """
        if not release_date:
            return 50.0  # Unknown = moderate risk
        
        try:
            release_datetime = datetime.fromisoformat(release_date)
            age_years = (datetime.now() - release_datetime).days / 365.25
            
            # Score: 0-1 year = 0, 5+ years = 100
            score = min(100, (age_years / 5.0) * 100)
            return score
            
        except Exception:
            return 50.0
    
    def calculate_eol_score(self, eol_date: Optional[str]) -> Tuple[float, int]:
        """
        Calculate EOL score (0-100, higher = more risk).
        
        Args:
            eol_date: End-of-life date in ISO format or boolean
        
        Returns:
            Tuple of (eol_score, months_to_eol)
        """
        if eol_date is None:
            return (50.0, -1)  # Unknown
        
        if isinstance(eol_date, bool):
            if eol_date:  # Already EOL
                return (100.0, 0)
            else:  # Not EOL
                return (0.0, 999)
        
        try:
            eol_datetime = datetime.fromisoformat(str(eol_date))
            months_to_eol = (eol_datetime - datetime.now()).days / 30.44
            
            if months_to_eol < 0:
                # Already EOL
                months_past_eol = abs(months_to_eol)
                score = min(100, 100 + (months_past_eol / 12.0) * 20)
                return (min(100, score), 0)
            elif months_to_eol <= 6:
                # EOL within 6 months = critical
                score = 100 - (months_to_eol / 6.0) * 30
                return (score, int(months_to_eol))
            elif months_to_eol <= 12:
                # EOL within 1 year = high risk
                score = 70 - ((months_to_eol - 6) / 6.0) * 40
                return (score, int(months_to_eol))
            else:
                # EOL > 1 year = low risk
                score = max(0, 30 - (months_to_eol / 24.0) * 30)
                return (score, int(months_to_eol))
                
        except Exception:
            return (50.0, -1)
    
    def calculate_cve_score(self, cve_count: int) -> float:
        """
        Calculate CVE score (0-100, higher = more risk).
        
        Args:
            cve_count: Number of known CVEs
        
        Returns:
            CVE score (0-100)
        """
        # Score: 0 CVEs = 0, 10+ CVEs = 100
        if cve_count <= 0:
            return 0.0
        
        score = min(100, (cve_count / 10.0) * 100)
        return score
    
    def calculate_risk_score(self, age_score: float, eol_score: float, 
                            cve_score: float) -> float:
        """
        Calculate overall risk score using weighted formula.
        
        Formula: age (30%) + eol (40%) + cve (30%)
        
        Args:
            age_score: Age score (0-100)
            eol_score: EOL score (0-100)
            cve_score: CVE score (0-100)
        
        Returns:
            Overall risk score (0-100)
        """
        return (age_score * 0.30) + (eol_score * 0.40) + (cve_score * 0.30)
    
    def get_recommendation(self, risk_score: float, months_to_eol: int) -> str:
        """
        Generate recommendation based on risk score.
        
        Args:
            risk_score: Overall risk score (0-100)
            months_to_eol: Months until end-of-life
        
        Returns:
            Recommendation string
        """
        if risk_score >= 70:
            if months_to_eol <= 6:
                return "CRITICAL: Upgrade immediately. EOL within 6 months."
            else:
                return "HIGH: Plan upgrade soon. High risk detected."
        elif risk_score >= 40:
            if months_to_eol <= 12:
                return "MEDIUM: Consider upgrade. EOL within 1 year."
            else:
                return "MEDIUM: Monitor and plan upgrade."
        else:
            return "LOW: Continue monitoring. Low risk."
    
    def score_technology(self, product: str, version: str, 
                        cve_count: int = 0) -> Dict:
        """
        Score a technology and return risk assessment.
        
        Args:
            product: Product name (e.g., ".NET", "Visual Studio")
            version: Version string (e.g., "8.0", "2022")
            cve_count: Known CVE count (default: 0)
        
        Returns:
            Risk assessment dictionary
        """
        # Query EOL API
        eol_data = self._query_eol_api(product, version)
        
        # Calculate scores
        release_date = eol_data.get('releaseDate') if eol_data else None
        eol_date = eol_data.get('eol') if eol_data else None
        
        age_score = self.calculate_age_score(release_date)
        eol_score, months_to_eol = self.calculate_eol_score(eol_date)
        cve_score = self.calculate_cve_score(cve_count)
        
        risk_score = self.calculate_risk_score(age_score, eol_score, cve_score)
        recommendation = self.get_recommendation(risk_score, months_to_eol)
        
        return {
            'product': product,
            'version': version,
            'risk_score': round(risk_score, 2),
            'age_score': round(age_score, 2),
            'eol_score': round(eol_score, 2),
            'cve_score': round(cve_score, 2),
            'eol_date': eol_date,
            'months_to_eol': months_to_eol,
            'cve_count': cve_count,
            'recommendation': recommendation,
            'release_date': release_date,
            'latest_version': eol_data.get('latest') if eol_data else None,
            'lts': eol_data.get('lts', False) if eol_data else False
        }
    
    def score_tech_stack(self, tech_stack_path: str) -> List[Dict]:
        """
        Score all technologies in tech stack JSON.
        
        Args:
            tech_stack_path: Path to tech-stack.json
        
        Returns:
            List of risk assessments
        """
        with open(tech_stack_path, 'r') as f:
            tech_stack = json.load(f)
        
        results = []
        
        # Extract unique technologies
        technologies = set()
        
        for backend in tech_stack.get('backend', []):
            metadata = backend.get('metadata', {})
            
            # Framework versions
            for solution in metadata.get('solutions', []):
                for project in solution.get('projects', []):
                    framework = project.get('framework', '')
                    if framework:
                        technologies.add(('Framework', framework))
            
            # VS versions
            for solution in metadata.get('solutions', []):
                vs_version = solution.get('vsVersion', '')
                if vs_version:
                    technologies.add(('Visual Studio', vs_version))
        
        # Score each technology
        for product, version in technologies:
            try:
                score = self.score_technology(product, version)
                results.append(score)
            except Exception as e:
                print(f"Error scoring {product} {version}: {e}")
        
        return results


if __name__ == '__main__':
    # Example usage
    scorer = TechStackRiskScorer()
    
    # Score individual technology
    result = scorer.score_technology('.NET', '8.0')
    print(json.dumps(result, indent=2))
