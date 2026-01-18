"""
Hash Verifier - Tamper Detection and Integrity Verification

Production-grade hash chain verification with:
- SHA-256 incremental verification
- Hash chain integrity validation
- Tamper detection
- Performance-optimized verification (caching)
- Audit trail integration

Satisfies: NFR-003-02 - Hash Chain Integrity Verification

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import hashlib
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cortex.brain.core.result import Err, Ok, Result


@dataclass
class HashChainEntry:
    """Single entry in a hash chain."""
    
    id: str
    timestamp: str
    data_hash: str  # SHA-256 of entry data
    previous_hash: str  # Hash of previous entry
    entry_hash: str  # SHA-256 of (data_hash + previous_hash)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'data_hash': self.data_hash,
            'previous_hash': self.previous_hash,
            'entry_hash': self.entry_hash,
        }


class HashVerifier:
    """
    Verify hash chain integrity and detect tampering.
    
    Maintains cryptographic chain where each entry's hash
    includes the previous entry's hash, making tampering
    instantly detectable.
    """
    
    def __init__(self, cache_size: int = 1000):
        """
        Initialize hash verifier.
        
        Args:
            cache_size: Number of recent verifications to cache
        """
        self.cache_size = cache_size
        self._verification_cache: Dict[str, bool] = {}
        self._cache_order: List[str] = []
    
    @staticmethod
    def compute_hash(data: str) -> str:
        """
        Compute SHA-256 hash of data.
        
        Args:
            data: Data to hash
            
        Returns:
            Hex-encoded SHA-256 hash
        """
        return hashlib.sha256(data.encode('utf-8')).hexdigest()
    
    @staticmethod
    def compute_entry_hash(data_hash: str, previous_hash: str) -> str:
        """
        Compute entry hash from data hash and previous hash.
        
        Args:
            data_hash: SHA-256 of entry data
            previous_hash: Hash from previous entry
            
        Returns:
            SHA-256 of concatenated hashes
        """
        combined = f"{data_hash}:{previous_hash}"
        return HashVerifier.compute_hash(combined)
    
    def create_chain_entry(
        self,
        entry_id: str,
        data: str,
        previous_hash: str = "0" * 64,  # All-zeros for first entry
    ) -> HashChainEntry:
        """
        Create a new hash chain entry.
        
        Args:
            entry_id: Unique identifier for entry
            data: Data to hash
            previous_hash: Hash from previous entry (or all-zeros for first)
            
        Returns:
            HashChainEntry with computed hashes
        """
        timestamp = datetime.now(timezone.utc).isoformat()
        data_hash = self.compute_hash(data)
        entry_hash = self.compute_entry_hash(data_hash, previous_hash)
        
        return HashChainEntry(
            id=entry_id,
            timestamp=timestamp,
            data_hash=data_hash,
            previous_hash=previous_hash,
            entry_hash=entry_hash,
        )
    
    def verify_chain(self, entries: List[Dict[str, Any]]) -> Result[Tuple[bool, str]]:
        """
        Verify integrity of entire hash chain.
        
        Args:
            entries: List of hash chain entries (dicts)
            
        Returns:
            Result[Tuple[bool, str]] - (chain_valid, details)
        """
        if not entries:
            return Ok((True, "Empty chain (valid)"))
        
        try:
            # Start with all-zeros for first entry
            expected_previous = "0" * 64
            tamper_detected = []
            
            for i, entry in enumerate(entries):
                # Verify structure
                required_fields = {'entry_hash', 'data_hash', 'previous_hash', 'id'}
                if not all(field in entry for field in required_fields):
                    return Ok((False, f"Entry {i} missing required fields"))
                
                # Verify entry hash
                computed_hash = self.compute_entry_hash(
                    entry['data_hash'],
                    entry['previous_hash']
                )
                
                if computed_hash != entry['entry_hash']:
                    tamper_detected.append({
                        'entry_id': entry['id'],
                        'index': i,
                        'expected_hash': computed_hash,
                        'actual_hash': entry['entry_hash'],
                    })
                
                # Verify chain linkage
                if entry['previous_hash'] != expected_previous:
                    tamper_detected.append({
                        'entry_id': entry['id'],
                        'index': i,
                        'issue': 'chain_link_broken',
                        'expected_previous': expected_previous,
                        'actual_previous': entry['previous_hash'],
                    })
                
                expected_previous = entry['entry_hash']
            
            if tamper_detected:
                details = f"Chain tampering detected in {len(tamper_detected)} entries"
                return Ok((False, details))
            
            return Ok((True, f"Chain verified: {len(entries)} entries"))
        
        except Exception as e:
            return Err(f"Chain verification error: {e}")
    
    def verify_from_database(self, db_path: Path, table_name: str = "audit_log") -> Result[Tuple[bool, str]]:
        """
        Verify hash chain from SQLite database.
        
        Args:
            db_path: Path to SQLite database
            table_name: Name of table containing entries
            
        Returns:
            Result[Tuple[bool, str]] - (chain_valid, details)
        """
        try:
            if not db_path.exists():
                return Err(f"Database not found: {db_path}")
            
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                # Get all entries ordered by timestamp
                cursor.execute(f"""
                    SELECT entry_hash, data_hash, previous_hash, id
                    FROM {table_name}
                    ORDER BY timestamp ASC
                """)
                
                entries = [dict(row) for row in cursor.fetchall()]
                
                return self.verify_chain(entries)
        
        except sqlite3.DatabaseError as e:
            return Err(f"Database error: {e}")
        except Exception as e:
            return Err(f"Verification error: {e}")
    
    def verify_entry(self, entry: Dict[str, Any]) -> Result[bool]:
        """
        Verify a single hash chain entry.
        
        Args:
            entry: Entry dict with entry_hash, data_hash, previous_hash
            
        Returns:
            Result[bool] - True if entry hash is valid
        """
        try:
            required_fields = {'entry_hash', 'data_hash', 'previous_hash'}
            if not all(field in entry for field in required_fields):
                return Err("Entry missing required hash fields")
            
            computed_hash = self.compute_entry_hash(
                entry['data_hash'],
                entry['previous_hash']
            )
            
            is_valid = computed_hash == entry['entry_hash']
            return Ok(is_valid)
        
        except Exception as e:
            return Err(f"Verification error: {e}")
    
    def get_verification_proof(
        self,
        entry: Dict[str, Any],
        verifiable: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate verification proof for an entry.
        
        Args:
            entry: Entry to generate proof for
            verifiable: Whether entry should be verifiable
            
        Returns:
            Dictionary with verification details
        """
        computed_hash = self.compute_entry_hash(
            entry['data_hash'],
            entry['previous_hash']
        )
        
        is_valid = computed_hash == entry['entry_hash']
        
        return {
            'entry_id': entry.get('id'),
            'computed_hash': computed_hash,
            'claimed_hash': entry['entry_hash'],
            'match': is_valid,
            'data_hash': entry['data_hash'],
            'previous_hash': entry['previous_hash'],
            'verification_timestamp': datetime.now(timezone.utc).isoformat(),
        }
    
    def cache_verification(self, key: str, result: bool):
        """
        Cache verification result.
        
        Args:
            key: Cache key (usually entry ID)
            result: Verification result
        """
        self._verification_cache[key] = result
        self._cache_order.append(key)
        
        # Evict oldest if cache full
        if len(self._cache_order) > self.cache_size:
            oldest = self._cache_order.pop(0)
            del self._verification_cache[oldest]
    
    def get_cached_verification(self, key: str) -> Optional[bool]:
        """
        Get cached verification result if available.
        
        Args:
            key: Cache key
            
        Returns:
            Cached result or None if not cached
        """
        return self._verification_cache.get(key)
    
    def clear_cache(self):
        """Clear verification cache."""
        self._verification_cache.clear()
        self._cache_order.clear()
    
    def export_chain_to_json(self, entries: List[Dict[str, Any]]) -> str:
        """
        Export hash chain to JSON.
        
        Args:
            entries: List of chain entries
            
        Returns:
            JSON string representation
        """
        return json.dumps({
            'chain': entries,
            'entry_count': len(entries),
            'exported_at': datetime.now(timezone.utc).isoformat(),
        }, indent=2)
    
    def detect_tampering_indicators(self, entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect indicators of tampering in chain.
        
        Args:
            entries: List of chain entries
            
        Returns:
            List of detected tampering indicators
        """
        indicators = []
        
        if not entries:
            return indicators
        
        expected_previous = "0" * 64
        
        for i, entry in enumerate(entries):
            # Check for hash mismatch
            if 'entry_hash' in entry and 'data_hash' in entry:
                computed = self.compute_entry_hash(
                    entry['data_hash'],
                    entry['previous_hash']
                )
                if computed != entry['entry_hash']:
                    indicators.append({
                        'type': 'hash_mismatch',
                        'entry_index': i,
                        'entry_id': entry.get('id'),
                    })
            
            # Check for broken chain linkage
            if 'previous_hash' in entry:
                if entry['previous_hash'] != expected_previous:
                    indicators.append({
                        'type': 'chain_link_broken',
                        'entry_index': i,
                        'entry_id': entry.get('id'),
                    })
            
            # Check for timestamp anomalies
            if 'timestamp' in entry and i > 0:
                current_time = datetime.fromisoformat(entry['timestamp'])
                prev_time = datetime.fromisoformat(entries[i-1]['timestamp'])
                if current_time < prev_time:
                    indicators.append({
                        'type': 'timestamp_anomaly',
                        'entry_index': i,
                        'entry_id': entry.get('id'),
                    })
            
            expected_previous = entry.get('entry_hash', '0' * 64)
        
        return indicators
