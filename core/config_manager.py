#!/usr/bin/env python3
"""
Configuration Manager for Cover Letter Agent
===========================================

Provides centralized configuration management with validation, defaults, and merging.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from .exceptions import ConfigurationError, FileLoadError
from .logging_config import get_logger
from .performance import get_file_cache, get_performance_monitor
from .types import ConfigDict

logger = get_logger(__name__)


@dataclass
class ConfigDefaults:
    """Default configuration values."""

    # Agent defaults
    agent_defaults: ConfigDict = field(
        default_factory=lambda: {
            "llm": {
                "enabled": False,
                "model": "gpt-4",
                "temperature": 0.7,
                "max_tokens": 1000,
                "preserve_truth": True,
                "add_comments": False,
            },
            "google_drive": {"enabled": False, "folder_id": "", "credentials_file": "credentials.json", "materials": {}},
            "profile": {"resume_file": "", "achievements": []},
            "cover_letter": {
                "personal_brand": {"tagline": "", "key_strengths": []},
                "tone": {"default": "professional", "startup": "conversational", "enterprise": "professional"},
            },
        }
    )

    # Logic defaults
    logic_defaults: ConfigDict = field(
        default_factory=lambda: {
            "scoring_rules": {
                "keyword_weights": {"AI": 3.0, "ML": 3.0, "startup": 2.5, "growth": 2.0, "leadership": 2.0, "clean tech": 2.0}
            },
            "go_no_go": {
                "minimum_keywords": 3,
                "minimum_total_score": 5.0,
                "strong_match_keywords": ["AI", "ML", "growth", "startup"],
                "poor_match_keywords": ["junior", "entry-level", "intern"],
            },
            "job_classification": {
                "leadership": {"keywords": ["manager", "director", "lead", "head", "chief"], "min_keyword_count": 1},
                "IC": {"keywords": ["analyst", "specialist", "coordinator"], "min_keyword_count": 1},
            },
            "enhancement_suggestions": {
                "triggers": {"low_score": {"threshold": 3.0, "message": "Consider adding more specific keywords"}}
            },
        }
    )

    # Targeting defaults
    targeting_defaults: ConfigDict = field(
        default_factory=lambda: {
            "titles": {
                "leadership": [
                    "product manager",
                    "product director",
                    "head of product",
                    "senior product manager",
                    "principal product manager",
                ],
                "IC": ["product analyst", "product specialist", "product coordinator"],
            },
            "comp_target": 150000,
            "locations": {"preferred": ["San Francisco", "New York", "Seattle"], "open_to": ["Remote", "Austin", "Boston"]},
            "company_stages": {
                "startup": ["seed", "series a", "series b"],
                "growth": ["series c", "series d", "public"],
                "enterprise": ["public", "fortune 500"],
            },
            "business_models": {"b2b": ["saas", "enterprise", "platform"], "b2c": ["consumer", "marketplace", "mobile"]},
        }
    )


class ConfigManager:
    """Manages configuration loading, validation, and merging."""

    def __init__(self, user_id: Optional[str] = None, config_dir: Optional[Path] = None):
        """Initialize configuration manager."""
        self.user_id = user_id
        self.config_dir = config_dir or Path("data")
        self.defaults = ConfigDefaults()
        self._config_cache: Dict[str, Any] = {}

        if user_id:
            self.user_dir = Path("users") / user_id
            if not self.user_dir.exists():
                raise ConfigurationError(f"User directory not found: {self.user_dir}")
        else:
            self.user_dir = None

    def load_config(self, config_type: str) -> ConfigDict:
        """Load configuration of specified type with defaults and validation."""
        cache_key = f"{self.user_id}_{config_type}" if self.user_id else config_type

        if cache_key in self._config_cache:
            return self._config_cache[cache_key]

        try:
            # Load user-specific config if available
            user_config = self._load_user_config(config_type) if self.user_id else {}

            # Load global config
            global_config = self._load_global_config(config_type)

            # Get defaults for this config type
            defaults = self._get_defaults(config_type)

            # Merge configurations (user overrides global, global overrides defaults)
            merged_config = self._merge_configs(defaults, global_config, user_config)

            # Validate configuration
            self._validate_config(config_type, merged_config)

            # Cache the result
            self._config_cache[cache_key] = merged_config

            logger.debug(f"Loaded {config_type} config for user: {self.user_id}")
            return merged_config

        except Exception as e:
            logger.error(f"Failed to load {config_type} config: {e}")
            raise ConfigurationError(f"Failed to load {config_type} config: {e}")

    def _load_user_config(self, config_type: str) -> ConfigDict:
        """Load user-specific configuration."""
        if not self.user_dir:
            return {}

        config_file = self.user_dir / f"{config_type}.yaml"
        if not config_file.exists():
            logger.debug(f"User config file not found: {config_file}")
            return {}

        try:
            # Use cached file loading
            file_cache = get_file_cache()
            config = file_cache.load_yaml_file(config_file)
            print(f"[DEBUG] Loaded user config from {config_file}:")
            import pprint
            pprint.pprint(config)
            return config
        except Exception as e:
            logger.error(f"Unexpected error loading user config {config_file}: {e}")
            raise FileLoadError(f"Failed to load user config {config_file}: {e}")

    def _load_global_config(self, config_type: str) -> ConfigDict:
        """Load global configuration."""
        config_file = self.config_dir / f"{config_type}.yaml"
        if not config_file.exists():
            logger.debug(f"Global config file not found: {config_file}")
            return {}

        try:
            # Use cached file loading
            file_cache = get_file_cache()
            config = file_cache.load_yaml_file(config_file)

            return config
        except Exception as e:
            logger.error(f"Unexpected error loading global config {config_file}: {e}")
            raise FileLoadError(f"Failed to load global config {config_file}: {e}")

    def _get_defaults(self, config_type: str) -> ConfigDict:
        """Get default configuration for specified type."""
        if config_type == "agent_config":
            return self.defaults.agent_defaults
        elif config_type == "blurb_logic":
            return self.defaults.logic_defaults
        elif config_type == "job_targeting":
            return self.defaults.targeting_defaults
        else:
            return {}

    def _merge_configs(self, *configs: ConfigDict) -> ConfigDict:
        # Debug: print configs being merged
        import pprint
        print("[DEBUG] _merge_configs called with configs:")
        for i, config in enumerate(configs):
            print(f"  Config {i}:")
            pprint.pprint(config)
        merged = {}
        for config in configs:
            if config:
                self._deep_merge(merged, config)
        # After merging, fill in any missing keys from the first config (defaults)
        if configs:
            def fill_missing_keys(default, merged):
                for key, value in default.items():
                    if key not in merged:
                        merged[key] = value
                    elif isinstance(value, dict) and isinstance(merged[key], dict):
                        fill_missing_keys(value, merged[key])
            fill_missing_keys(configs[0], merged)
        # Debug output for profile
        if 'profile' in merged:
            print("[DEBUG] Merged profile config:")
            pprint.pprint(merged['profile'])
        return merged

    def _deep_merge(self, base: ConfigDict, override: ConfigDict) -> None:
        # Debug output for profile
        if 'profile' in override or 'profile' in base:
            import pprint
            print("[DEBUG] _deep_merge called for 'profile':")
            print("  base:")
            pprint.pprint(base.get('profile', base))
            print("  override:")
            pprint.pprint(override.get('profile', override))
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _validate_config(self, config_type: str, config: ConfigDict) -> None:
        """Validate configuration structure and values."""
        if config_type == "agent_config":
            self._validate_agent_config(config)
        elif config_type == "blurb_logic":
            self._validate_logic_config(config)
        elif config_type == "job_targeting":
            self._validate_targeting_config(config)

    def _validate_agent_config(self, config: ConfigDict) -> None:
        """Validate agent configuration."""
        required_sections = ["llm", "google_drive", "profile", "cover_letter"]
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(f"Missing required section '{section}' in agent config")

        # Validate LLM config
        if "llm" in config:
            llm = config["llm"]
            required_llm_fields = ["model", "temperature", "max_tokens"]
            for field in required_llm_fields:
                if field not in llm:
                    raise ConfigurationError(f"Missing required LLM field: {field}")

        # Validate Google Drive config
        if "google_drive" in config:
            gdrive = config["google_drive"]
            if gdrive.get("enabled", False):
                if not gdrive.get("folder_id"):
                    logger.warning("Google Drive enabled but no folder_id specified")

    def _validate_logic_config(self, config: ConfigDict) -> None:
        """Validate logic configuration."""
        required_sections = ["scoring_rules", "go_no_go", "job_classification"]
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(f"Missing required section '{section}' in logic config")

        # Validate scoring rules
        if "scoring_rules" in config:
            scoring = config["scoring_rules"]
            if "keyword_weights" not in scoring:
                raise ConfigurationError("Missing keyword_weights in scoring_rules")

        # Validate go/no-go rules
        if "go_no_go" in config:
            go_no_go = config["go_no_go"]
            required_fields = ["minimum_keywords", "minimum_total_score"]
            for field in required_fields:
                if field not in go_no_go:
                    raise ConfigurationError(f"Missing required field '{field}' in go_no_go")

    def _validate_targeting_config(self, config: ConfigDict) -> None:
        """Validate targeting configuration."""
        required_sections = ["titles", "locations"]
        for section in required_sections:
            if section not in config:
                raise ConfigurationError(f"Missing required section '{section}' in targeting config")

    def save_config(self, config_type: str, config: ConfigDict) -> None:
        """Save configuration to user directory."""
        if not self.user_id:
            raise ConfigurationError("Cannot save config without user_id")

        if not self.user_dir:
            raise ConfigurationError("User directory not available")

        config_file = self.user_dir / f"{config_type}.yaml"

        try:
            # Create backup if file exists
            if config_file.exists():
                backup_file = config_file.with_suffix(".yaml.backup")
                config_file.rename(backup_file)
                logger.debug(f"Created backup: {backup_file}")

            # Save new config
            with open(config_file, "w") as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)

            # Clear cache for this config type
            cache_key = f"{self.user_id}_{config_type}"
            if cache_key in self._config_cache:
                del self._config_cache[cache_key]

            logger.info(f"Saved {config_type} config for user: {self.user_id}")

        except Exception as e:
            logger.error(f"Failed to save {config_type} config: {e}")
            raise ConfigurationError(f"Failed to save {config_type} config: {e}")

    def get_config_value(self, config_type: str, key_path: str, default: Any = None) -> Any:
        """Get a specific configuration value using dot notation."""
        config = self.load_config(config_type)

        keys = key_path.split(".")
        value = config

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default

    def set_config_value(self, config_type: str, key_path: str, value: Any) -> None:
        """Set a specific configuration value using dot notation."""
        config = self.load_config(config_type)

        keys = key_path.split(".")
        current = config

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the value
        current[keys[-1]] = value

        # Save the updated config
        self.save_config(config_type, config)

    def list_available_configs(self) -> List[str]:
        """List available configuration types."""
        configs = []

        # Check user directory
        if self.user_dir and self.user_dir.exists():
            for file in self.user_dir.glob("*.yaml"):
                config_type = file.stem
                if config_type not in configs:
                    configs.append(config_type)

        # Check global directory
        if self.config_dir.exists():
            for file in self.config_dir.glob("*.yaml"):
                config_type = file.stem
                if config_type not in configs:
                    configs.append(config_type)

        return configs

    def create_default_config(self, config_type: str) -> ConfigDict:
        """Create a default configuration template."""
        defaults = self._get_defaults(config_type)
        return defaults.copy()

    def validate_all_configs(self) -> Dict[str, List[str]]:
        """Validate all available configurations and return errors."""
        errors = {}
        configs = self.list_available_configs()

        for config_type in configs:
            try:
                self.load_config(config_type)
            except Exception as e:
                errors[config_type] = [str(e)]

        return errors


def get_config_manager(user_id: Optional[str] = None, config_dir: Optional[Path] = None) -> ConfigManager:
    """Factory function to create a configuration manager."""
    return ConfigManager(user_id, config_dir)
