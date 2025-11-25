"""
CORTEX GitHub Fetcher Module

Fetches latest CORTEX releases from GitHub, downloads and extracts packages,
and verifies integrity. Handles both public and private repository access.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
import os
import tempfile
import zipfile
import hashlib
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


class GitHubFetcher:
    """Fetches CORTEX releases from GitHub repository."""
    
    REPO_OWNER = "asifhussain60"
    REPO_NAME = "CORTEX"
    GITHUB_API_BASE = "https://api.github.com"
    GITHUB_RAW_BASE = "https://raw.githubusercontent.com"
    
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialize GitHub fetcher.
        
        Args:
            github_token: Optional GitHub personal access token for private repos
        """
        self.github_token = github_token or os.environ.get("GITHUB_TOKEN")
        self.temp_dir = Path(tempfile.gettempdir()) / "cortex-upgrade"
        self.temp_dir.mkdir(exist_ok=True)
    
    def get_latest_release(self) -> Dict:
        """
        Fetch latest CORTEX release information from GitHub.
        
        Returns:
            Dictionary with release info (tag_name, name, body, assets, etc.)
        """
        url = f"{self.GITHUB_API_BASE}/repos/{self.REPO_OWNER}/{self.REPO_NAME}/releases/latest"
        
        try:
            release_data = self._github_api_request(url)
            return release_data
        except HTTPError as e:
            if e.code == 404:
                print("⚠️  No releases found. Using branch download method.")
                return self._get_branch_as_release()
            raise
    
    def get_specific_release(self, version: str) -> Dict:
        """
        Fetch specific CORTEX release by version tag.
        
        Args:
            version: Version tag (e.g., "v5.3.0" or "5.3.0")
            
        Returns:
            Dictionary with release info
        """
        # Ensure version has 'v' prefix
        tag = version if version.startswith('v') else f'v{version}'
        
        url = f"{self.GITHUB_API_BASE}/repos/{self.REPO_OWNER}/{self.REPO_NAME}/releases/tags/{tag}"
        
        try:
            return self._github_api_request(url)
        except HTTPError as e:
            if e.code == 404:
                raise ValueError(f"Release {tag} not found")
            raise
    
    def list_releases(self, limit: int = 10) -> List[Dict]:
        """
        List available CORTEX releases.
        
        Args:
            limit: Maximum number of releases to return
            
        Returns:
            List of release dictionaries
        """
        url = f"{self.GITHUB_API_BASE}/repos/{self.REPO_OWNER}/{self.REPO_NAME}/releases?per_page={limit}"
        
        try:
            return self._github_api_request(url)
        except HTTPError as e:
            if e.code == 404:
                return []
            raise
    
    def download_release(
        self,
        version: Optional[str] = None,
        download_path: Optional[Path] = None
    ) -> Path:
        """
        Download CORTEX release package.
        
        Args:
            version: Specific version to download, or None for latest
            download_path: Where to save the download, or None for temp directory
            
        Returns:
            Path to downloaded file
        """
        # Get release info
        if version:
            release = self.get_specific_release(version)
        else:
            release = self.get_latest_release()
        
        # Determine download URL
        if "zipball_url" in release:
            download_url = release["zipball_url"]
        elif "assets" in release and release["assets"]:
            # Use first asset (typically the main package)
            download_url = release["assets"][0]["browser_download_url"]
        else:
            # Fallback: construct archive URL
            tag = release.get("tag_name", "main")
            download_url = f"https://github.com/{self.REPO_OWNER}/{self.REPO_NAME}/archive/refs/tags/{tag}.zip"
        
        # Determine save path
        if download_path is None:
            filename = f"cortex-{release.get('tag_name', 'latest')}.zip"
            download_path = self.temp_dir / filename
        
        # Download file
        print(f"⬇️  Downloading CORTEX from {download_url}...")
        
        try:
            request = Request(download_url)
            if self.github_token:
                request.add_header("Authorization", f"token {self.github_token}")
            
            with urlopen(request) as response:
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(download_path, 'wb') as f:
                    while True:
                        chunk = response.read(8192)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # Progress indicator
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            print(f"\r   Progress: {progress:.1f}% ({downloaded}/{total_size} bytes)", end='')
                
                print()  # New line after progress
                
        except (URLError, HTTPError) as e:
            raise RuntimeError(f"Failed to download release: {e}")
        
        print(f"✅ Downloaded to {download_path}")
        return download_path
    
    def extract_package(
        self,
        zip_path: Path,
        extract_to: Optional[Path] = None
    ) -> Path:
        """
        Extract downloaded CORTEX package.
        
        Args:
            zip_path: Path to zip file
            extract_to: Where to extract, or None for temp directory
            
        Returns:
            Path to extracted directory
        """
        if extract_to is None:
            extract_to = self.temp_dir / "extracted"
        
        extract_to.mkdir(parents=True, exist_ok=True)
        
        print(f"📦 Extracting package...")
        
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            
            # Find the actual CORTEX directory (GitHub archives have a root folder)
            extracted_items = list(extract_to.iterdir())
            if len(extracted_items) == 1 and extracted_items[0].is_dir():
                cortex_dir = extracted_items[0]
            else:
                cortex_dir = extract_to
            
            print(f"✅ Extracted to {cortex_dir}")
            return cortex_dir
            
        except zipfile.BadZipFile as e:
            raise RuntimeError(f"Invalid zip file: {e}")
    
    def verify_integrity(
        self,
        file_path: Path,
        expected_checksum: Optional[str] = None,
        algorithm: str = "sha256"
    ) -> bool:
        """
        Verify file integrity using checksum.
        
        Args:
            file_path: Path to file to verify
            expected_checksum: Expected checksum value, or None to skip
            algorithm: Hash algorithm (sha256, md5, etc.)
            
        Returns:
            True if valid or no checksum provided, False if mismatch
        """
        if expected_checksum is None:
            print("⚠️  No checksum provided, skipping integrity verification")
            return True
        
        print(f"🔍 Verifying file integrity ({algorithm})...")
        
        hash_obj = hashlib.new(algorithm)
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hash_obj.update(chunk)
        
        actual_checksum = hash_obj.hexdigest()
        
        if actual_checksum == expected_checksum:
            print(f"✅ Integrity verified: {actual_checksum}")
            return True
        else:
            print(f"❌ Integrity check failed!")
            print(f"   Expected: {expected_checksum}")
            print(f"   Actual:   {actual_checksum}")
            return False
    
    def get_release_notes(self, version: Optional[str] = None) -> str:
        """
        Get release notes for specific version.
        
        Args:
            version: Version to get notes for, or None for latest
            
        Returns:
            Release notes markdown
        """
        if version:
            release = self.get_specific_release(version)
        else:
            release = self.get_latest_release()
        
        return release.get("body", "No release notes available.")
    
    def cleanup(self) -> None:
        """Clean up temporary download files."""
        import shutil
        
        if self.temp_dir.exists():
            print(f"🧹 Cleaning up temporary files...")
            shutil.rmtree(self.temp_dir)
            print(f"✅ Cleanup complete")
    
    def validate_extracted_package(self, extracted_path: Path) -> Dict[str, bool]:
        """
        Validate extracted CORTEX package has required structure.
        
        Args:
            extracted_path: Path to extracted CORTEX directory
            
        Returns:
            Dictionary of validation results
        """
        print(f"🔍 Validating extracted package...")
        
        required_files = [
            "VERSION",
            ".github/prompts/CORTEX.prompt.md",
            "cortex-brain/templates/response-templates.yaml",
            "cortex-brain/metadata/capabilities.yaml",
            "scripts/cortex-upgrade.py"
        ]
        
        required_dirs = [
            ".github/prompts",
            "cortex-brain",
            "scripts"
        ]
        
        results = {}
        
        # Check files
        for file_path in required_files:
            full_path = extracted_path / file_path
            results[f"file:{file_path}"] = full_path.exists()
            status = "✅" if results[f"file:{file_path}"] else "❌"
            print(f"   {status} {file_path}")
        
        # Check directories
        for dir_path in required_dirs:
            full_path = extracted_path / dir_path
            results[f"dir:{dir_path}"] = full_path.exists() and full_path.is_dir()
            status = "✅" if results[f"dir:{dir_path}"] else "❌"
            print(f"   {status} {dir_path}/")
        
        all_valid = all(results.values())
        print(f"\n{'✅' if all_valid else '❌'} Package validation: {'PASSED' if all_valid else 'FAILED'}")
        
        return results
    
    def _github_api_request(self, url: str) -> Dict:
        """
        Make authenticated GitHub API request.
        
        Args:
            url: API endpoint URL
            
        Returns:
            Parsed JSON response
        """
        request = Request(url)
        request.add_header("Accept", "application/vnd.github.v3+json")
        
        if self.github_token:
            request.add_header("Authorization", f"token {self.github_token}")
        
        try:
            with urlopen(request) as response:
                data = response.read()
                return json.loads(data)
        except HTTPError as e:
            if e.code == 403:
                raise RuntimeError(
                    "GitHub API rate limit exceeded. "
                    "Provide GITHUB_TOKEN environment variable for higher limits."
                )
            raise
    
    def _get_branch_as_release(self, branch: str = "CORTEX-3.0") -> Dict:
        """
        Fallback method: treat branch as a release when no releases exist.
        
        Args:
            branch: Branch name to download
            
        Returns:
            Pseudo-release dictionary
        """
        return {
            "tag_name": branch,
            "name": f"CORTEX {branch}",
            "body": "Development branch (no release notes)",
            "zipball_url": f"https://github.com/{self.REPO_OWNER}/{self.REPO_NAME}/archive/refs/heads/{branch}.zip",
            "assets": []
        }


def main():
    """CLI entry point for testing GitHub fetcher."""
    import sys
    
    fetcher = GitHubFetcher()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "latest":
            release = fetcher.get_latest_release()
            print(json.dumps(release, indent=2))
            
        elif command == "list":
            releases = fetcher.list_releases()
            print(f"\n🧠 Available CORTEX Releases:\n")
            for release in releases:
                print(f"  • {release['tag_name']} - {release['name']}")
                print(f"    Published: {release['published_at']}")
                print()
            
        elif command == "download":
            version = sys.argv[2] if len(sys.argv) > 2 else None
            zip_path = fetcher.download_release(version)
            print(f"\n✅ Downloaded: {zip_path}")
            
        elif command == "extract":
            if len(sys.argv) < 3:
                print("Usage: python github_fetcher.py extract <zip_file>")
                sys.exit(1)
            
            zip_path = Path(sys.argv[2])
            extracted = fetcher.extract_package(zip_path)
            print(f"\n✅ Extracted: {extracted}")
            
        elif command == "notes":
            version = sys.argv[2] if len(sys.argv) > 2 else None
            notes = fetcher.get_release_notes(version)
            print(f"\n📝 Release Notes:\n")
            print(notes)
            
        elif command == "cleanup":
            fetcher.cleanup()
            
        else:
            print(f"Unknown command: {command}")
            print("\nAvailable commands:")
            print("  latest    - Get latest release info")
            print("  list      - List available releases")
            print("  download [version] - Download release")
            print("  extract <zip_file> - Extract package")
            print("  notes [version] - Get release notes")
            print("  cleanup   - Clean temp files")
            sys.exit(1)
    else:
        # Default: show latest release info
        try:
            release = fetcher.get_latest_release()
            print("\n🧠 Latest CORTEX Release:\n")
            print(f"Version: {release['tag_name']}")
            print(f"Name: {release['name']}")
            print(f"Published: {release.get('published_at', 'N/A')}")
            print(f"\nRelease Notes:\n{release.get('body', 'No notes')}")
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
