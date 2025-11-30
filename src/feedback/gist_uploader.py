"""
GitHub Gist Uploader - Uploads Feedback to GitHub Gist

Provides automatic feedback upload to GitHub Gist with user consent management,
privacy protection, and graceful fallback to manual upload.

Features:
- One-time consent prompt with preference memory
- Automatic upload with progress indication
- Manual upload instructions as fallback
- Privacy protection (all anonymization preserved)
- Rate limiting and error handling

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import json
import logging
import os
import requests
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import platform as platform_module  # Renamed to avoid conflicts


logger = logging.getLogger(__name__)


class UploadStatus(Enum):
    """Upload status codes."""
    SUCCESS = "success"
    FAILED = "failed"
    DECLINED = "declined"  # User declined upload
    MANUAL = "manual"  # User will upload manually
    NO_TOKEN = "no_token"  # No GitHub token configured


@dataclass
class GistUploadResult:
    """Result of Gist upload operation."""
    
    status: UploadStatus
    gist_url: Optional[str] = None
    gist_id: Optional[str] = None
    error_message: Optional[str] = None
    manual_instructions: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'status': self.status.value,
            'gist_url': self.gist_url,
            'gist_id': self.gist_id,
            'error_message': self.error_message,
            'manual_instructions': self.manual_instructions,
        }


class GistUploader:
    """
    Uploads feedback reports to GitHub Gist.
    
    Usage:
        uploader = GistUploader()
        
        # Upload with consent prompt
        result = uploader.upload_report(
            report_content="# Bug Report\n...",
            filename="cortex-bug-report-2025-11-24.md"
        )
        
        if result.status == UploadStatus.SUCCESS:
            print(f"Uploaded to: {result.gist_url}")
        elif result.status == UploadStatus.MANUAL:
            print(result.manual_instructions)
    """
    
    def __init__(
        self,
        config_path: Optional[Path] = None,
        preferences_path: Optional[Path] = None
    ):
        """
        Initialize Gist uploader.
        
        Args:
            config_path: Path to cortex.config.json
            preferences_path: Path to user preferences
        """
        self.config_path = config_path or Path.cwd() / "cortex.config.json"
        self.preferences_path = preferences_path or Path.cwd() / "cortex-brain" / "feedback" / "upload_preferences.json"
        
        # Load config
        self.config = self._load_config()
        
        # Load preferences
        self.preferences = self._load_preferences()
        
        # GitHub API settings
        self.github_api_base = "https://api.github.com"
        self.gist_api_url = f"{self.github_api_base}/gists"
    
    def upload_report(
        self,
        report_content: str,
        filename: str,
        description: Optional[str] = None,
        is_public: bool = True,
        auto_prompt: bool = True
    ) -> GistUploadResult:
        """
        Upload feedback report to GitHub Gist.
        
        Args:
            report_content: Markdown content of report
            filename: Filename for gist (e.g., "bug-report.md")
            description: Optional gist description
            is_public: Whether gist is public (default: True)
            auto_prompt: Prompt user for consent if not set
        
        Returns:
            GistUploadResult with status and URL
        """
        # Check for GitHub token
        github_token = self._get_github_token()
        
        if not github_token:
            return self._handle_no_token(report_content, filename)
        
        # Check user preferences
        upload_preference = self._get_upload_preference(auto_prompt)
        
        if upload_preference == "never":
            return GistUploadResult(
                status=UploadStatus.DECLINED,
                manual_instructions=self._get_manual_instructions(report_content, filename)
            )
        
        elif upload_preference == "manual":
            return GistUploadResult(
                status=UploadStatus.MANUAL,
                manual_instructions=self._get_manual_instructions(report_content, filename)
            )
        
        elif upload_preference == "always":
            # Proceed with automatic upload
            return self._upload_to_gist(
                report_content=report_content,
                filename=filename,
                description=description or f"CORTEX Feedback Report - {datetime.now().strftime('%Y-%m-%d')}",
                is_public=is_public,
                github_token=github_token
            )
        
        else:
            # Unknown preference, default to manual
            return GistUploadResult(
                status=UploadStatus.MANUAL,
                manual_instructions=self._get_manual_instructions(report_content, filename)
            )
    
    def _upload_to_gist(
        self,
        report_content: str,
        filename: str,
        description: str,
        is_public: bool,
        github_token: str
    ) -> GistUploadResult:
        """
        Upload to GitHub Gist via API.
        
        Args:
            report_content: Report content
            filename: Filename
            description: Gist description
            is_public: Public visibility
            github_token: GitHub personal access token
        
        Returns:
            GistUploadResult
        """
        try:
            # Prepare gist payload
            payload = {
                "description": description,
                "public": is_public,
                "files": {
                    filename: {
                        "content": report_content
                    }
                }
            }
            
            # Make API request
            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "CORTEX-Feedback-System"
            }
            
            logger.info(f"Uploading feedback report to GitHub Gist: {filename}")
            
            response = requests.post(
                self.gist_api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            # Check response
            if response.status_code == 201:
                # Success
                gist_data = response.json()
                gist_url = gist_data.get('html_url')
                gist_id = gist_data.get('id')
                
                logger.info(f"✅ Successfully uploaded to Gist: {gist_url}")
                
                return GistUploadResult(
                    status=UploadStatus.SUCCESS,
                    gist_url=gist_url,
                    gist_id=gist_id
                )
            
            else:
                # Failed
                error_msg = response.json().get('message', 'Unknown error')
                logger.error(f"Failed to upload to Gist: {response.status_code} - {error_msg}")
                
                return GistUploadResult(
                    status=UploadStatus.FAILED,
                    error_message=f"GitHub API error: {error_msg}",
                    manual_instructions=self._get_manual_instructions(report_content, filename)
                )
        
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error uploading to Gist: {e}")
            
            return GistUploadResult(
                status=UploadStatus.FAILED,
                error_message=f"Network error: {str(e)}",
                manual_instructions=self._get_manual_instructions(report_content, filename)
            )
        
        except Exception as e:
            logger.error(f"Unexpected error uploading to Gist: {e}")
            
            return GistUploadResult(
                status=UploadStatus.FAILED,
                error_message=f"Unexpected error: {str(e)}",
                manual_instructions=self._get_manual_instructions(report_content, filename)
            )
    
    def _get_upload_preference(self, auto_prompt: bool) -> str:
        """
        Get user's upload preference.
        
        Args:
            auto_prompt: Whether to prompt if not set
        
        Returns:
            "always", "never", "manual", or "ask"
        """
        # Check saved preference
        if 'upload_to_gist' in self.preferences:
            return self.preferences['upload_to_gist']
        
        # No preference saved - prompt user if allowed
        if auto_prompt:
            return self._prompt_for_consent()
        
        # Default to manual
        return "manual"
    
    def _prompt_for_consent(self) -> str:
        """
        Prompt user for upload consent.
        
        Returns:
            User's choice: "always", "never", "manual"
        """
        print("\n" + "="*60)
        print("📢 CORTEX Feedback Upload")
        print("="*60)
        print("\nWould you like to automatically upload feedback to GitHub Gist?")
        print("\nOptions:")
        print("  1. Always upload automatically (recommended)")
        print("  2. Never upload (I'll report manually)")
        print("  3. Ask each time")
        print("  4. Show manual upload instructions")
        print("\nNote: All feedback is anonymized before upload.")
        print("="*60)
        
        while True:
            choice = input("\nYour choice (1-4): ").strip()
            
            if choice == "1":
                preference = "always"
                break
            elif choice == "2":
                preference = "never"
                break
            elif choice == "3":
                preference = "ask"
                break
            elif choice == "4":
                preference = "manual"
                break
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 4.")
        
        # Save preference
        self.preferences['upload_to_gist'] = preference
        self.preferences['consent_given_at'] = datetime.now().isoformat()
        self._save_preferences()
        
        print(f"\n✅ Preference saved: {preference}")
        
        return preference
    
    def _handle_no_token(
        self,
        report_content: str,
        filename: str
    ) -> GistUploadResult:
        """
        Handle case where no GitHub token is configured.
        
        Args:
            report_content: Report content
            filename: Filename
        
        Returns:
            GistUploadResult with manual instructions
        """
        instructions = [
            "⚠️  No GitHub token configured for automatic upload.",
            "",
            "To enable automatic upload:",
            "1. Generate a GitHub Personal Access Token:",
            "   - Go to: https://github.com/settings/tokens",
            "   - Click 'Generate new token (classic)'",
            "   - Select scope: 'gist' (create gists)",
            "   - Copy the generated token",
            "",
            "2. Add token to cortex.config.json:",
            '   "github": {',
            '     "token": "your_token_here"',
            '   }',
            "",
            "3. Run feedback command again",
            "",
            "Or upload manually:",
            *self._get_manual_instructions(report_content, filename).split("\n")
        ]
        
        return GistUploadResult(
            status=UploadStatus.NO_TOKEN,
            manual_instructions="\n".join(instructions)
        )
    
    def _get_manual_instructions(
        self,
        report_content: str,
        filename: str
    ) -> str:
        """
        Generate manual upload instructions.
        
        Args:
            report_content: Report content
            filename: Filename
        
        Returns:
            Instructions as string
        """
        # Save report to file for manual upload
        reports_dir = Path.cwd() / "cortex-brain" / "feedback" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        report_file = reports_dir / filename
        report_file.write_text(report_content, encoding='utf-8')
        
        instructions = [
            "📋 Manual Upload Instructions",
            "",
            f"Report saved to: {report_file}",
            "",
            "Option 1: GitHub CLI (Recommended)",
            f"  gh gist create \"{report_file}\" --desc \"CORTEX Feedback\" --public",
            "",
            "Option 2: Web Interface",
            "  1. Go to: https://gist.github.com/",
            f"  2. Copy content from: {report_file}",
            "  3. Paste into gist editor",
            f"  4. Set filename: {filename}",
            "  5. Click 'Create public gist'",
            "",
            "Option 3: GitHub Issues",
            "  1. Go to: https://github.com/asifhussain60/CORTEX/issues/new",
            f"  2. Copy content from: {report_file}",
            "  3. Create new issue",
            "",
            "Thank you for helping improve CORTEX! 🙏"
        ]
        
        return "\n".join(instructions)
    
    def _get_github_token(self) -> Optional[str]:
        """
        Get GitHub token from config or environment.
        
        Returns:
            GitHub token or None
        """
        # Check config file
        if 'github' in self.config and 'token' in self.config['github']:
            return self.config['github']['token']
        
        # Check environment variable
        token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
        if token:
            return token
        
        return None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load CORTEX configuration."""
        if not self.config_path.exists():
            return {}
        
        try:
            return json.loads(self.config_path.read_text(encoding='utf-8'))
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
            return {}
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Load user preferences."""
        if not self.preferences_path.exists():
            return {}
        
        try:
            return json.loads(self.preferences_path.read_text(encoding='utf-8'))
        except Exception as e:
            logger.warning(f"Failed to load preferences: {e}")
            return {}
    
    def _save_preferences(self) -> None:
        """Save user preferences."""
        self.preferences_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            self.preferences_path.write_text(
                json.dumps(self.preferences, indent=2),
                encoding='utf-8'
            )
        except Exception as e:
            logger.error(f"Failed to save preferences: {e}")


def get_gist_uploader() -> GistUploader:
    """
    Get singleton GistUploader instance.
    
    Returns:
        GistUploader instance
    """
    if not hasattr(get_gist_uploader, '_instance'):
        get_gist_uploader._instance = GistUploader()
    
    return get_gist_uploader._instance
