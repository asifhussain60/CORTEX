"""
Phase 5.3 RED - UserProfile Integration Tests

Tests integration between TemplateRenderer and UserProfileManager for dynamic
interaction mode selection from Tier 1 user_profile table.

Test Coverage:
- Mode fetching from user_profile table
- Fallback to default mode when profile missing
- Mode validation and normalization
- Query caching for performance
- Error handling for database failures

Author: Asif Hussain
Phase: 5.3 RED - UserProfile Integration
Created: December 2, 2025
"""

import pytest
from pathlib import Path
from src.response_templates.template_renderer import TemplateRenderer
from src.tier1.user_profile_manager import UserProfileManager


@pytest.fixture
def temp_db_path(tmp_path):
    """Create temporary database path for testing."""
    return tmp_path / "test_working_memory.db"


@pytest.fixture
def profile_manager(temp_db_path):
    """Create UserProfileManager with temporary database."""
    return UserProfileManager(db_path=temp_db_path)


@pytest.fixture
def renderer_with_profile(temp_db_path):
    """Create TemplateRenderer with UserProfileManager integration."""
    return TemplateRenderer(
        template_dir=Path("cortex-brain/response-templates"),
        profile_manager=UserProfileManager(db_path=temp_db_path)
    )


class TestUserProfileIntegration:
    """Test dynamic mode selection from user_profile table."""
    
    def test_renderer_accepts_profile_manager(self, temp_db_path):
        """Test TemplateRenderer accepts UserProfileManager in constructor."""
        profile_manager = UserProfileManager(db_path=temp_db_path)
        renderer = TemplateRenderer(
            template_dir=Path("cortex-brain/response-templates"),
            profile_manager=profile_manager
        )
        
        assert renderer.profile_manager is not None
        assert isinstance(renderer.profile_manager, UserProfileManager)
    
    def test_compose_uses_profile_mode_when_available(self, renderer_with_profile, profile_manager):
        """Test compose_template uses mode from user profile when available."""
        # Set profile mode to 'educational'
        profile_manager._init_database()
        conn = profile_manager.db_path
        import sqlite3
        conn = sqlite3.connect(profile_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_profile (id, interaction_mode, experience_level)
            VALUES (1, 'educational', 'junior')
        """)
        conn.commit()
        conn.close()
        
        # Compose template without specifying mode
        composed = renderer_with_profile.compose_template("planning")
        
        # Should use 'educational' mode from profile
        assert "CORTEX" in composed
        # Educational mode uses detailed format
        assert "🎯" in composed  # Has understanding section
    
    def test_compose_falls_back_to_guided_when_no_profile(self, renderer_with_profile):
        """Test compose_template falls back to 'guided' mode when no profile exists."""
        # No profile set in database
        composed = renderer_with_profile.compose_template("help")
        
        # Should use default 'guided' mode
        assert "### 🎯 My Understanding Of Your Request" in composed
        assert "### 🔍 Next Steps" in composed
    
    def test_explicit_mode_overrides_profile(self, renderer_with_profile, profile_manager):
        """Test explicitly provided mode overrides profile setting."""
        # Set profile mode to 'guided'
        import sqlite3
        conn = sqlite3.connect(profile_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_profile (id, interaction_mode, experience_level)
            VALUES (1, 'guided', 'mid')
        """)
        conn.commit()
        conn.close()
        
        # Explicitly request 'autonomous' mode
        composed = renderer_with_profile.compose_template("status_check", mode="autonomous")
        
        # Should use autonomous mode (compact format, no challenge section)
        assert len(composed) < 500  # Autonomous is brief
    
    def test_invalid_profile_mode_falls_back_to_guided(self, renderer_with_profile, profile_manager):
        """Test invalid mode in profile falls back to 'guided'."""
        # Set invalid mode in profile
        import sqlite3
        conn = sqlite3.connect(profile_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_profile (id, interaction_mode, experience_level)
            VALUES (1, 'invalid_mode', 'mid')
        """)
        conn.commit()
        conn.close()
        
        # Should fall back to 'guided'
        composed = renderer_with_profile.compose_template("planning")
        
        assert "### 🎯 My Understanding Of Your Request" in composed


class TestProfileCaching:
    """Test profile query caching for performance."""
    
    def test_profile_mode_is_cached(self, renderer_with_profile, profile_manager):
        """Test profile mode is cached to avoid repeated database queries."""
        # Set profile mode
        import sqlite3
        conn = sqlite3.connect(profile_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_profile (id, interaction_mode, experience_level)
            VALUES (1, 'pair', 'senior')
        """)
        conn.commit()
        conn.close()
        
        # First call - should query database
        renderer_with_profile.compose_template("planning")
        
        # Second call - should use cached value
        renderer_with_profile.compose_template("planning")
        
        # Verify cache was used (profile_cache_hit_count should be > 0)
        assert hasattr(renderer_with_profile, 'profile_cache_hit_count')
        assert renderer_with_profile.profile_cache_hit_count > 0
    
    def test_profile_cache_respects_ttl(self, renderer_with_profile, profile_manager):
        """Test profile cache expires after TTL (5 minutes)."""
        import sqlite3
        import time
        
        # Set profile mode
        conn = sqlite3.connect(profile_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_profile (id, interaction_mode, experience_level)
            VALUES (1, 'guided', 'mid')
        """)
        conn.commit()
        conn.close()
        
        # First call - populates cache
        renderer_with_profile.compose_template("planning")
        
        # Manually expire cache (simulate TTL)
        if hasattr(renderer_with_profile, '_profile_cache_time'):
            renderer_with_profile._profile_cache_time = time.time() - 301  # 5 min + 1 sec ago
        
        # Second call - should re-query database
        renderer_with_profile.compose_template("planning")
        
        # Verify cache was refreshed
        assert renderer_with_profile._profile_cache_time > time.time() - 10
    
    def test_cache_invalidated_on_profile_update(self, renderer_with_profile, profile_manager):
        """Test cache is invalidated when profile is updated."""
        import sqlite3
        
        # Set initial mode
        conn = sqlite3.connect(profile_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_profile (id, interaction_mode, experience_level)
            VALUES (1, 'guided', 'mid')
        """)
        conn.commit()
        conn.close()
        
        # First call - caches 'guided'
        composed1 = renderer_with_profile.compose_template("planning")
        
        # Update profile
        conn = sqlite3.connect(profile_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE user_profile SET interaction_mode = 'autonomous' WHERE id = 1
        """)
        conn.commit()
        conn.close()
        
        # Clear cache manually (simulating cache invalidation logic)
        if hasattr(renderer_with_profile, '_clear_profile_cache'):
            renderer_with_profile._clear_profile_cache()
        
        # Second call - should use new 'autonomous' mode
        composed2 = renderer_with_profile.compose_template("status_check")
        
        # Autonomous should be shorter
        assert len(composed2) < len(composed1)


class TestErrorHandling:
    """Test error handling for database access failures."""
    
    def test_database_error_falls_back_to_default_mode(self, temp_db_path):
        """Test database connection error falls back to 'guided' mode."""
        # Create renderer with non-existent database path
        bad_path = temp_db_path.parent / "nonexistent" / "db.db"
        profile_manager = UserProfileManager(db_path=bad_path)
        
        renderer = TemplateRenderer(
            template_dir=Path("cortex-brain/response-templates"),
            profile_manager=profile_manager
        )
        
        # Should not crash, should use default 'guided' mode
        composed = renderer.compose_template("planning")
        
        assert "### 🎯 My Understanding Of Your Request" in composed
    
    def test_corrupted_profile_falls_back_to_default(self, renderer_with_profile, profile_manager):
        """Test corrupted profile data falls back to 'guided' mode."""
        import sqlite3
        
        # Insert corrupted data (interaction_mode constraint will fail on read attempt)
        conn = sqlite3.connect(profile_manager.db_path)
        cursor = conn.cursor()
        
        # Disable constraint for insertion
        cursor.execute("PRAGMA foreign_keys = OFF")
        cursor.execute("""
            INSERT OR REPLACE INTO user_profile (id, interaction_mode, experience_level)
            VALUES (1, 'corrupted_value', 'mid')
        """)
        conn.commit()
        conn.close()
        
        # Should handle gracefully and fall back to 'guided'
        composed = renderer_with_profile.compose_template("planning")
        
        assert "CORTEX" in composed
    
    def test_missing_profile_manager_uses_default_mode(self):
        """Test TemplateRenderer works without profile_manager (backward compatibility)."""
        # Create renderer without profile_manager
        renderer = TemplateRenderer(template_dir=Path("cortex-brain/response-templates"))
        
        # Should work with default 'guided' mode
        composed = renderer.compose_template("planning", mode="guided")
        
        assert "### 🎯 My Understanding Of Your Request" in composed


class TestModeResolution:
    """Test mode resolution logic priority."""
    
    def test_mode_resolution_priority_explicit_wins(self, renderer_with_profile, profile_manager):
        """Test explicit mode parameter has highest priority."""
        import sqlite3
        
        # Set profile to 'educational'
        conn = sqlite3.connect(profile_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_profile (id, interaction_mode, experience_level)
            VALUES (1, 'educational', 'junior')
        """)
        conn.commit()
        conn.close()
        
        # Explicitly request 'autonomous'
        composed = renderer_with_profile.compose_template("status_check", mode="autonomous")
        
        # Should use autonomous (brief output)
        assert len(composed) < 500
    
    def test_mode_resolution_profile_second_priority(self, renderer_with_profile, profile_manager):
        """Test profile mode is used when no explicit mode provided."""
        import sqlite3
        
        # Set profile to 'pair'
        conn = sqlite3.connect(profile_manager.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO user_profile (id, interaction_mode, experience_level)
            VALUES (1, 'pair', 'senior')
        """)
        conn.commit()
        conn.close()
        
        # No explicit mode provided
        composed = renderer_with_profile.compose_template("planning")
        
        # Should use pair mode (has "option" or "track" language)
        assert "option" in composed.lower() or "track" in composed.lower()
    
    def test_mode_resolution_default_is_guided(self, renderer_with_profile):
        """Test default mode is 'guided' when no profile and no explicit mode."""
        # No profile set, no explicit mode
        composed = renderer_with_profile.compose_template("planning")
        
        # Should use guided mode (standard 5-part format)
        assert "### 🎯 My Understanding Of Your Request" in composed
        assert "### ⚠️ Challenge" in composed
        assert "### 💬 Response" in composed
        assert "### 📝 Your Request" in composed
        assert "### 🔍 Next Steps" in composed
