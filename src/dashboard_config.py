"""
Dashboard Configuration Loader

Purpose: Load and validate dashboard configuration from YAML file.
Provides centralized access to all dashboard settings.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DashboardPaths:
    """Dashboard path configuration"""
    data_root: Path
    repos: Path
    mock: Path
    schema: Path
    templates: Path
    cache: Path
    ui: Path
    ui_components: Path
    ui_services: Path
    ui_styles: Path
    config: Path
    repository_registry: Path


@dataclass
class CollectorConfig:
    """Data collector configuration"""
    deep_analysis: bool
    quick_scan_fallback: bool
    timeout: int
    parallel_workers: int
    show_progress: bool
    progress_interval: int
    required_files: list


@dataclass
class DiscoveryConfig:
    """Repository discovery configuration"""
    auto_scan: bool
    scan_on_startup: bool
    scan_interval: int
    validate_data_files: bool
    remove_missing: bool
    min_data_files: int
    require_metadata: bool


@dataclass
class UIConfig:
    """UI configuration"""
    logo_path: str
    logo_width: int
    logo_height: int
    logo_alt: str
    refresh_interval: int
    enable_polling: bool
    enable_websocket: bool
    theme: str
    accent_color: str
    show_repository_count: bool
    show_last_updated: bool
    enable_notifications: bool


class DashboardConfig:
    """
    Dashboard configuration loader and manager.

    Provides centralized access to all dashboard settings loaded from
    dashboard-config.yaml file.
    """

    _instance = None
    _config = None
    _config_path = None

    def __new__(cls):
        """Singleton pattern to ensure single config instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize configuration loader"""
        if self._config is None:
            self._load_config()

    def _load_config(self) -> None:
        """Load configuration from YAML file"""
        try:
            # Determine config file path (src/dashboard_config.py -> CORTEX root is 1 level up)
            cortex_root = Path(__file__).parent.parent
            self._config_path = cortex_root / "cortex-brain" / "dashboards" / "config" / "dashboard-config.yaml"

            if not self._config_path.exists():
                logger.warning(f"Config file not found: {self._config_path}, using defaults")
                self._config = self._get_default_config()
                return

            # Load YAML
            with open(self._config_path, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f)

            logger.info(f"Dashboard config loaded from: {self._config_path}")

            # Validate config
            self._validate_config()

        except Exception as e:
            logger.error(f"Failed to load dashboard config: {e}")
            logger.warning("Using default configuration")
            self._config = self._get_default_config()

    def _validate_config(self) -> None:
        """Validate configuration structure"""
        required_sections = ['version', 'paths', 'collectors', 'discovery', 'ui']

        for section in required_sections:
            if section not in self._config:
                logger.warning(f"Missing config section: {section}")

    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file not found"""
        return {
            'version': '1.0',
            'paths': {
                'data_root': 'dashboards/data',
                'repos': 'dashboards/data/repos',
                'mock': 'dashboards/data/mock',
                'schema': 'dashboards/data/schema',
                'templates': 'dashboards/data/templates',
                'cache': 'dashboards/data/cache',
                'ui': 'dashboards/ui',
                'repository_registry': 'dashboards/data/repository-registry.json'
            },
            'collectors': {
                'deep_analysis': True,
                'timeout': 300,
                'parallel_workers': 4,
                'show_progress': True
            },
            'discovery': {
                'auto_scan': True,
                'scan_on_startup': True,
                'remove_missing': True
            },
            'ui': {
                'logo_path': 'static/images/cortex-logo.png',
                'logo_width': 180,
                'logo_height': 60,
                'refresh_interval': 5000
            }
        }

    def get_path(self, key: str) -> Path:
        """
        Get absolute path for configuration key.

        Args:
            key: Path configuration key (e.g., 'repos', 'ui', 'cache')

        Returns:
            Absolute Path object
        """
        cortex_root = Path(__file__).parent.parent.parent.parent
        brain_path = cortex_root / "cortex-brain"

        relative_path = self._config.get('paths', {}).get(key, '')

        if not relative_path:
            logger.warning(f"Path key not found in config: {key}")
            return brain_path / "dashboards"

        return brain_path / relative_path

    def get_paths(self) -> DashboardPaths:
        """Get all paths as structured object"""
        return DashboardPaths(
            data_root=self.get_path('data_root'),
            repos=self.get_path('repos'),
            mock=self.get_path('mock'),
            schema=self.get_path('schema'),
            templates=self.get_path('templates'),
            cache=self.get_path('cache'),
            ui=self.get_path('ui'),
            ui_components=self.get_path('ui_components'),
            ui_services=self.get_path('ui_services'),
            ui_styles=self.get_path('ui_styles'),
            config=self.get_path('config'),
            repository_registry=self.get_path('repository_registry')
        )

    def get_collector_config(self) -> CollectorConfig:
        """Get collector configuration"""
        collector_dict = self._config.get('collectors', {})
        config = CollectorConfig(
            deep_analysis=collector_dict.get('deep_analysis', True),
            quick_scan_fallback=collector_dict.get('quick_scan_fallback', False),
            timeout=collector_dict.get('timeout', 300),
            parallel_workers=collector_dict.get('parallel_workers', 4),
            show_progress=collector_dict.get('show_progress', True),
            progress_interval=collector_dict.get('progress_interval', 5),
            required_files=collector_dict.get('required_files', [])
        )
        # Add benchmarks as dynamic attribute
        config.benchmarks = collector_dict.get('benchmarks', {})
        return config

    def get_discovery_config(self) -> DiscoveryConfig:
        """Get discovery configuration"""
        discovery_dict = self._config.get('discovery', {})
        return DiscoveryConfig(
            auto_scan=discovery_dict.get('auto_scan', True),
            scan_on_startup=discovery_dict.get('scan_on_startup', True),
            scan_interval=discovery_dict.get('scan_interval', 30),
            validate_data_files=discovery_dict.get('validate_data_files', True),
            remove_missing=discovery_dict.get('remove_missing', True),
            min_data_files=discovery_dict.get('min_data_files', 3),
            require_metadata=discovery_dict.get('require_metadata', True)
        )

    def get_ui_config(self) -> UIConfig:
        """Get UI configuration"""
        ui_dict = self._config.get('ui', {})
        return UIConfig(
            logo_path=ui_dict.get('logo_path', 'static/images/cortex-logo.png'),
            logo_width=ui_dict.get('logo_width', 180),
            logo_height=ui_dict.get('logo_height', 60),
            logo_alt=ui_dict.get('logo_alt', 'CORTEX'),
            refresh_interval=ui_dict.get('refresh_interval', 5000),
            enable_polling=ui_dict.get('enable_polling', True),
            enable_websocket=ui_dict.get('enable_websocket', False),
            theme=ui_dict.get('theme', 'dark'),
            accent_color=ui_dict.get('accent_color', '#00d4ff'),
            show_repository_count=ui_dict.get('show_repository_count', True),
            show_last_updated=ui_dict.get('show_last_updated', True),
            enable_notifications=ui_dict.get('enable_notifications', True)
        )

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by dot-notation key.

        Args:
            key: Configuration key (e.g., 'collectors.timeout')
            default: Default value if key not found

        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self._config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return default
            else:
                return default

        return value if value is not None else default

    def reload(self) -> None:
        """Reload configuration from file"""
        self._config = None
        self._load_config()
        logger.info("Dashboard configuration reloaded")

    @property
    def version(self) -> str:
        """Get configuration version"""
        return self._config.get('version', '1.0')

    @property
    def config_dict(self) -> Dict[str, Any]:
        """Get full configuration dictionary"""
        return self._config.copy()


# Global config instance
_config = DashboardConfig()


def get_config() -> DashboardConfig:
    """Get global dashboard configuration instance"""
    return _config


def get_path(key: str) -> Path:
    """Convenience function to get path"""
    return _config.get_path(key)


def get_paths() -> DashboardPaths:
    """Convenience function to get all paths"""
    return _config.get_paths()


# Export commonly used functions
__all__ = [
    'DashboardConfig',
    'DashboardPaths',
    'CollectorConfig',
    'DiscoveryConfig',
    'UIConfig',
    'get_config',
    'get_path',
    'get_paths'
]
