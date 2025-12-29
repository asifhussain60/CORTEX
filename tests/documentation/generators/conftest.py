"""
Test configuration and fixtures for documentation generators

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import pytest
import sys
from pathlib import Path


@pytest.fixture(scope="session", autouse=True)
def setup_import_path():
    """Add cortex-brain/admin to Python path for importing generators"""
    cortex_brain_admin = Path(__file__).parent.parent.parent.parent / "cortex-brain" / "admin"
    
    if str(cortex_brain_admin) not in sys.path:
        sys.path.insert(0, str(cortex_brain_admin))
    
    yield
    
    # Cleanup
    if str(cortex_brain_admin) in sys.path:
        sys.path.remove(str(cortex_brain_admin))
