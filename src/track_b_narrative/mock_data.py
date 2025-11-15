"""
CORTEX 3.0 Track B - Mock Dual-Channel Data

Mock data generator for Track B Phase 4 development.
Creates realistic conversation and daemon capture YAML files following
the dual-channel schema defined in Phase 0.5.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import yaml
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import uuid
from pathlib import Path
import random


@dataclass
class MockConversation:
    """Mock conversation data structure"""
    conversation_id: str
    timestamp: datetime
    session_type: str  # "copilot_chat", "terminal", "manual_import"
    messages: List[Dict[str, Any]]
    project_context: Dict[str, Any]
    files_mentioned: List[str]
    entities_extracted: List[str]


@dataclass  
class MockDaemonCapture:
    """Mock daemon capture data structure"""
    capture_id: str
    timestamp: datetime
    event_type: str  # "file_change", "git_commit", "terminal_command"
    file_path: str
    change_type: str  # "created", "modified", "deleted"
    content_delta: Optional[str]
    git_metadata: Optional[Dict[str, Any]]


class DualChannelMockData:
    """
    Mock data generator for dual-channel development.
    
    Provides realistic mock data that follows the dual-channel schema
    for narrative generation development during Track B Phase 4.
    """
    
    def __init__(self, data_dir: str = None):
        """Initialize mock data generator"""
        self.data_dir = Path(data_dir) if data_dir else Path.cwd() / "mock_data"
        self.data_dir.mkdir(exist_ok=True)
        
        # Mock project structure
        self.mock_files = [
            "src/main.py", "src/utils.py", "src/models/user.py",
            "tests/test_main.py", "README.md", "requirements.txt",
            "src/api/endpoints.py", "src/database/schema.sql"
        ]
        
        # Mock conversation patterns
        self.conversation_patterns = [
            {"type": "feature_request", "files": ["src/api/endpoints.py"], "complexity": "medium"},
            {"type": "bug_fix", "files": ["src/main.py", "tests/test_main.py"], "complexity": "low"},
            {"type": "refactor", "files": ["src/utils.py"], "complexity": "high"},
            {"type": "documentation", "files": ["README.md"], "complexity": "low"},
        ]
    
    def generate_mock_conversations(self, count: int = 10) -> List[MockConversation]:
        """Generate realistic mock conversations"""
        conversations = []
        
        for i in range(count):
            pattern = random.choice(self.conversation_patterns)
            conversation = self._create_mock_conversation(pattern, i)
            conversations.append(conversation)
            
        return conversations
    
    def _create_mock_conversation(self, pattern: Dict[str, Any], index: int) -> MockConversation:
        """Create a single mock conversation"""
        conversation_id = f"conv_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now() - timedelta(days=random.randint(1, 30))
        
        messages = self._generate_conversation_messages(pattern)
        
        return MockConversation(
            conversation_id=conversation_id,
            timestamp=timestamp,
            session_type="copilot_chat",
            messages=messages,
            project_context={
                "project_name": "CORTEX",
                "branch": "main",
                "last_commit": f"abc{random.randint(1000, 9999)}",
                "files_in_project": len(self.mock_files)
            },
            files_mentioned=pattern["files"],
            entities_extracted=[
                f"class_{random.choice(['User', 'Database', 'API', 'Utils'])}",
                f"method_{random.choice(['process', 'validate', 'transform', 'save'])}",
                f"variable_{random.choice(['data', 'result', 'config', 'response'])}"
            ]
        )
    
    def _generate_conversation_messages(self, pattern: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate realistic conversation messages based on pattern"""
        if pattern["type"] == "feature_request":
            return [
                {
                    "role": "user",
                    "content": f"I need to add a new API endpoint for {random.choice(['user management', 'data processing', 'file upload'])}",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "role": "assistant", 
                    "content": "I'll help you create that endpoint. Let me examine the current API structure and suggest the implementation approach.",
                    "timestamp": (datetime.now() + timedelta(seconds=30)).isoformat()
                },
                {
                    "role": "user",
                    "content": "Great! Can you show me how to implement it with proper error handling?",
                    "timestamp": (datetime.now() + timedelta(minutes=2)).isoformat()
                }
            ]
        elif pattern["type"] == "bug_fix":
            return [
                {
                    "role": "user",
                    "content": f"There's a bug in {pattern['files'][0]} causing {random.choice(['null pointer exception', 'validation error', 'timeout issue'])}",
                    "timestamp": datetime.now().isoformat()
                },
                {
                    "role": "assistant",
                    "content": "Let me analyze the code and identify the root cause of this issue.",
                    "timestamp": (datetime.now() + timedelta(seconds=45)).isoformat()
                }
            ]
        else:
            return [
                {
                    "role": "user", 
                    "content": f"Help me with {pattern['type']} in {pattern['files'][0]}",
                    "timestamp": datetime.now().isoformat()
                }
            ]
    
    def generate_mock_daemon_captures(self, count: int = 20) -> List[MockDaemonCapture]:
        """Generate realistic mock daemon captures"""
        captures = []
        
        for i in range(count):
            capture = self._create_mock_daemon_capture(i)
            captures.append(capture)
            
        return captures
    
    def _create_mock_daemon_capture(self, index: int) -> MockDaemonCapture:
        """Create a single mock daemon capture"""
        capture_id = f"capture_{uuid.uuid4().hex[:8]}"
        timestamp = datetime.now() - timedelta(hours=random.randint(1, 48))
        
        event_type = random.choice(["file_change", "git_commit", "terminal_command"])
        file_path = random.choice(self.mock_files)
        
        change_type = random.choice(["created", "modified", "deleted"])
        if event_type == "git_commit":
            change_type = "modified"
            
        git_metadata = None
        if event_type == "git_commit":
            git_metadata = {
                "commit_hash": f"abc{random.randint(100000, 999999)}",
                "author": "Developer",
                "message": f"Fix {random.choice(['bug', 'feature', 'test'])} in {Path(file_path).stem}",
                "files_changed": [file_path]
            }
        
        content_delta = None
        if event_type == "file_change":
            content_delta = f"+    def new_function():\\n+        return True\\n-    # TODO: implement"
            
        return MockDaemonCapture(
            capture_id=capture_id,
            timestamp=timestamp,
            event_type=event_type,
            file_path=file_path,
            change_type=change_type,
            content_delta=content_delta,
            git_metadata=git_metadata
        )
    
    def save_mock_data_as_yaml(self, conversations: List[MockConversation] = None, 
                              captures: List[MockDaemonCapture] = None) -> Dict[str, str]:
        """Save mock data as YAML files"""
        if conversations is None:
            conversations = self.generate_mock_conversations()
        if captures is None:
            captures = self.generate_mock_daemon_captures()
            
        # Save conversations
        conv_file = self.data_dir / "mock_conversations.yaml" 
        conv_data = {
            "metadata": {
                "schema_version": "1.0",
                "generated_at": datetime.now().isoformat(),
                "source": "Track B Phase 4 Mock Data",
                "count": len(conversations)
            },
            "conversations": [asdict(conv) for conv in conversations]
        }
        
        with open(conv_file, 'w') as f:
            yaml.dump(conv_data, f, default_flow_style=False, sort_keys=False)
            
        # Save daemon captures
        capture_file = self.data_dir / "mock_daemon_captures.yaml"
        capture_data = {
            "metadata": {
                "schema_version": "1.0", 
                "generated_at": datetime.now().isoformat(),
                "source": "Track B Phase 4 Mock Data",
                "count": len(captures)
            },
            "captures": [asdict(capture) for capture in captures]
        }
        
        with open(capture_file, 'w') as f:
            yaml.dump(capture_data, f, default_flow_style=False, sort_keys=False)
            
        return {
            "conversations": str(conv_file),
            "captures": str(capture_file)
        }
    
    def load_mock_conversations(self) -> List[MockConversation]:
        """Load mock conversations from YAML file"""
        conv_file = self.data_dir / "mock_conversations.yaml"
        if not conv_file.exists():
            return self.generate_mock_conversations()
            
        with open(conv_file, 'r') as f:
            data = yaml.safe_load(f)
            
        conversations = []
        for conv_data in data.get("conversations", []):
            # Convert timestamp strings back to datetime
            conv_data["timestamp"] = datetime.fromisoformat(conv_data["timestamp"])
            conversations.append(MockConversation(**conv_data))
            
        return conversations
    
    def load_mock_captures(self) -> List[MockDaemonCapture]:
        """Load mock daemon captures from YAML file"""
        capture_file = self.data_dir / "mock_daemon_captures.yaml"
        if not capture_file.exists():
            return self.generate_mock_daemon_captures()
            
        with open(capture_file, 'r') as f:
            data = yaml.safe_load(f)
            
        captures = []
        for capture_data in data.get("captures", []):
            # Convert timestamp strings back to datetime
            capture_data["timestamp"] = datetime.fromisoformat(capture_data["timestamp"])
            captures.append(MockDaemonCapture(**capture_data))
            
        return captures


def create_track_b_mock_data():
    """Convenience function to create Track B mock data"""
    mock_data = DualChannelMockData()
    
    # Generate realistic mock data
    conversations = mock_data.generate_mock_conversations(15)
    captures = mock_data.generate_mock_daemon_captures(30)
    
    # Save to YAML files
    file_paths = mock_data.save_mock_data_as_yaml(conversations, captures)
    
    print(f"✅ Track B Mock Data Created:")
    print(f"   Conversations: {file_paths['conversations']}")
    print(f"   Daemon Captures: {file_paths['captures']}")
    print(f"   Total Files: {len(conversations)} conversations, {len(captures)} captures")
    
    return mock_data


if __name__ == "__main__":
    create_track_b_mock_data()