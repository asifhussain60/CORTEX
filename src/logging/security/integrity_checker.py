"""
Integrity Checker - Audit Trail Integrity Verification.

Features:
- SHA-256 checksums for log files
- Tamper detection
- Immutable checksum chain (blockchain-inspired)
- Digital signature verification
- Batch verification
- Comprehensive integrity reports
"""

import hashlib
import hmac
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any


class IntegrityViolation(Exception):
    """Base exception for integrity violations."""
    pass


class ChecksumMismatch(IntegrityViolation):
    """Raised when checksum doesn't match stored value."""
    pass


class TamperDetected(IntegrityViolation):
    """Raised when file tampering is detected."""
    pass


class SignatureInvalid(IntegrityViolation):
    """Raised when digital signature is invalid."""
    pass


class IntegrityChecker:
    """
    Integrity checker for audit logs with tamper detection.
    
    Features:
    - Generate and verify SHA-256 checksums
    - Store checksum metadata
    - Detect file tampering
    - Chain checksums for immutable audit trail
    - Digital signature support
    - Batch verification
    """
    
    def __init__(
        self,
        log_dir: Path,
        algorithm: str = "sha256",
        metadata_dir: str = ".integrity"
    ):
        """
        Initialize integrity checker.
        
        Args:
            log_dir: Directory containing log files
            algorithm: Hash algorithm (default: sha256)
            metadata_dir: Directory for checksum metadata
        """
        self.log_dir = Path(log_dir)
        self.algorithm = algorithm
        self.metadata_dir = self.log_dir / metadata_dir
        self.metadata_dir.mkdir(parents=True, exist_ok=True)
        
        # Chain storage
        self.chain_file = self.metadata_dir / "chain.json"
        self._init_chain()
    
    def _init_chain(self):
        """Initialize chain file if it doesn't exist."""
        if not self.chain_file.exists():
            self.chain_file.write_text(json.dumps({"entries": []}, indent=2))
    
    def generate_checksum(self, file_path: Path) -> str:
        """
        Generate checksum for file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hexadecimal checksum string
            
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not Path(file_path).exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        hasher = hashlib.new(self.algorithm)
        
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        
        return hasher.hexdigest()
    
    def _get_metadata_path(self, file_path: Path) -> Path:
        """Get metadata file path for log file."""
        file_path = Path(file_path)
        metadata_name = f"{file_path.name}.checksum"
        return self.metadata_dir / metadata_name
    
    def store_checksum(self, file_path: Path, checksum: str):
        """
        Store checksum metadata.
        
        Args:
            file_path: Path to log file
            checksum: Checksum to store
        """
        file_path = Path(file_path)
        metadata = {
            "checksum": checksum,
            "algorithm": self.algorithm,
            "timestamp": datetime.utcnow().isoformat(),
            "file_size": file_path.stat().st_size,
            "file_path": str(file_path)
        }
        
        metadata_path = self._get_metadata_path(file_path)
        metadata_path.write_text(json.dumps(metadata, indent=2))
    
    def get_stored_checksum(self, file_path: Path) -> Optional[str]:
        """
        Retrieve stored checksum.
        
        Args:
            file_path: Path to log file
            
        Returns:
            Stored checksum or None if not found
        """
        metadata_path = self._get_metadata_path(file_path)
        
        if not metadata_path.exists():
            return None
        
        metadata = json.loads(metadata_path.read_text())
        return metadata.get("checksum")
    
    def verify_integrity(self, file_path: Path, strict: bool = True) -> bool:
        """
        Verify file integrity against stored checksum.
        
        Args:
            file_path: Path to log file
            strict: If True, raise exception on mismatch; if False, return False
            
        Returns:
            True if integrity verified, False otherwise
            
        Raises:
            TamperDetected: If file has been tampered with (strict mode only)
        """
        stored_checksum = self.get_stored_checksum(file_path)
        
        if stored_checksum is None:
            if strict:
                raise TamperDetected(f"No stored checksum found for {file_path}")
            return False
        
        current_checksum = self.generate_checksum(file_path)
        
        if current_checksum != stored_checksum:
            if strict:
                raise TamperDetected(
                    f"File has been tampered with: {file_path}\n"
                    f"Expected: {stored_checksum}\n"
                    f"Got: {current_checksum}"
                )
            return False
        
        return True
    
    def verify_batch(self, file_paths: List[Path]) -> Dict[Path, bool]:
        """
        Verify integrity of multiple files.
        
        Args:
            file_paths: List of file paths to verify
            
        Returns:
            Dictionary mapping file paths to verification results
        """
        results = {}
        
        for file_path in file_paths:
            try:
                results[file_path] = self.verify_integrity(file_path, strict=False)
            except Exception:
                results[file_path] = False
        
        return results
    
    def create_chain_entry(
        self,
        file_path: Path,
        checksum: str
    ) -> Dict[str, Any]:
        """
        Create checksum chain entry.
        
        Args:
            file_path: Path to log file
            checksum: Current checksum
            
        Returns:
            Chain entry dictionary
        """
        # Load existing chain
        chain_data = json.loads(self.chain_file.read_text())
        entries = chain_data.get("entries", [])
        
        # Get previous hash
        previous_hash = None
        if entries:
            # Find last entry for this file
            file_entries = [
                e for e in entries
                if e.get("file_path") == str(file_path)
            ]
            if file_entries:
                previous_hash = file_entries[-1].get("entry_hash")
        
        # Create new entry
        entry = {
            "file_path": str(file_path),
            "checksum": checksum,
            "previous_hash": previous_hash,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Generate entry hash
        entry_data = f"{checksum}{previous_hash}{entry['timestamp']}"
        entry["entry_hash"] = hashlib.sha256(entry_data.encode()).hexdigest()
        
        # Append to chain
        entries.append(entry)
        chain_data["entries"] = entries
        
        # Save chain
        self.chain_file.write_text(json.dumps(chain_data, indent=2))
        
        return entry
    
    def verify_chain(self, file_path: Path) -> bool:
        """
        Verify integrity of checksum chain.
        
        Args:
            file_path: Path to log file
            
        Returns:
            True if chain is valid, False otherwise
        """
        chain_data = json.loads(self.chain_file.read_text())
        entries = chain_data.get("entries", [])
        
        # Get entries for this file
        file_entries = [
            e for e in entries
            if e.get("file_path") == str(file_path)
        ]
        
        if not file_entries:
            return True  # No chain to verify
        
        # Verify each link
        for i, entry in enumerate(file_entries):
            # Verify entry hash
            entry_data = f"{entry['checksum']}{entry['previous_hash']}{entry['timestamp']}"
            expected_hash = hashlib.sha256(entry_data.encode()).hexdigest()
            
            if entry["entry_hash"] != expected_hash:
                return False
            
            # Verify previous_hash link
            if i > 0:
                if entry["previous_hash"] != file_entries[i-1]["entry_hash"]:
                    return False
            else:
                # First entry should have None as previous
                if entry["previous_hash"] is not None:
                    return False
        
        return True
    
    def sign_checksum(self, checksum: str, key: str) -> str:
        """
        Generate HMAC signature for checksum.
        
        Args:
            checksum: Checksum to sign
            key: Secret key for signing
            
        Returns:
            Hexadecimal signature
        """
        signature = hmac.new(
            key.encode(),
            checksum.encode(),
            hashlib.sha256
        )
        return signature.hexdigest()
    
    def verify_signature(
        self,
        checksum: str,
        signature: str,
        key: str
    ) -> bool:
        """
        Verify HMAC signature.
        
        Args:
            checksum: Original checksum
            signature: Signature to verify
            key: Secret key
            
        Returns:
            True if signature is valid, False otherwise
        """
        try:
            expected_signature = self.sign_checksum(checksum, key)
            return hmac.compare_digest(signature, expected_signature)
        except Exception:
            return False
    
    def generate_report(self, directory: Path) -> Dict[str, Any]:
        """
        Generate comprehensive integrity report.
        
        Args:
            directory: Directory to scan
            
        Returns:
            Report dictionary with verification results
        """
        directory = Path(directory)
        log_files = [
            f for f in directory.iterdir()
            if f.is_file() and not f.name.startswith(".")
        ]
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "directory": str(directory),
            "total_files": len(log_files),
            "verified_files": 0,
            "tampered_files": 0,
            "missing_checksums": 0,
            "tampered_list": [],
            "missing_list": []
        }
        
        for log_file in log_files:
            stored_checksum = self.get_stored_checksum(log_file)
            
            if stored_checksum is None:
                report["missing_checksums"] += 1
                report["missing_list"].append(str(log_file))
                continue
            
            try:
                if self.verify_integrity(log_file, strict=False):
                    report["verified_files"] += 1
                else:
                    report["tampered_files"] += 1
                    report["tampered_list"].append(str(log_file))
            except Exception:
                report["tampered_files"] += 1
                report["tampered_list"].append(str(log_file))
        
        return report
