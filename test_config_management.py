#!/usr/bin/env python3
"""
Test Configuration Management
============================

Tests the centralized configuration management system.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from core.config_manager import ConfigDefaults, ConfigManager
from core.exceptions import ConfigurationError, FileLoadError


class TestConfigManagement(unittest.TestCase):
    """Test configuration management functionality."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_dir = Path(self.temp_dir) / "data"
        self.config_dir.mkdir()

        # Create test user directory
        self.user_dir = Path("users") / "test_config"
        self.user_dir.mkdir(exist_ok=True)

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)
        if self.user_dir.exists():
            shutil.rmtree(self.user_dir)

    def test_config_manager_initialization(self):
        """Test config manager initialization."""
        # Test with user_id
        config_manager = ConfigManager("test_config", self.config_dir)
        self.assertEqual(config_manager.user_id, "test_config")
        self.assertEqual(config_manager.config_dir, self.config_dir)
        self.assertIsNotNone(config_manager.user_dir)

        # Test without user_id
        config_manager = ConfigManager(config_dir=self.config_dir)
        self.assertIsNone(config_manager.user_id)
        self.assertIsNone(config_manager.user_dir)

    def test_defaults_are_defined(self):
        """Test that default configurations are properly defined."""
        defaults = ConfigDefaults()

        # Test agent defaults
        self.assertIn("llm", defaults.agent_defaults)
        self.assertIn("google_drive", defaults.agent_defaults)
        self.assertIn("profile", defaults.agent_defaults)
        self.assertIn("cover_letter", defaults.agent_defaults)

        # Test logic defaults
        self.assertIn("scoring_rules", defaults.logic_defaults)
        self.assertIn("go_no_go", defaults.logic_defaults)
        self.assertIn("job_classification", defaults.logic_defaults)

        # Test targeting defaults
        self.assertIn("titles", defaults.targeting_defaults)
        self.assertIn("locations", defaults.targeting_defaults)
        self.assertIn("comp_target", defaults.targeting_defaults)

    def test_load_config_with_defaults(self):
        """Test loading configuration with defaults."""
        config_manager = ConfigManager(config_dir=self.config_dir)

        # Test loading agent config (should return defaults)
        config = config_manager.load_config("agent_config")
        self.assertIn("llm", config)
        self.assertIn("google_drive", config)
        self.assertIn("profile", config)
        self.assertIn("cover_letter", config)

        # Test loading logic config (should return defaults)
        logic = config_manager.load_config("blurb_logic")
        self.assertIn("scoring_rules", logic)
        self.assertIn("go_no_go", logic)
        self.assertIn("job_classification", logic)

        # Test loading targeting config (should return defaults)
        targeting = config_manager.load_config("job_targeting")
        self.assertIn("titles", targeting)
        self.assertIn("locations", targeting)
        self.assertIn("comp_target", targeting)

    def test_load_config_with_global_override(self):
        """Test loading configuration with global override."""
        config_manager = ConfigManager(config_dir=self.config_dir)

        # Create global config file
        global_config = {"llm": {"enabled": True, "model": "gpt-3.5-turbo", "temperature": 0.8}}

        global_config_path = self.config_dir / "agent_config.yaml"
        with open(global_config_path, "w") as f:
            yaml.dump(global_config, f)

        # Load config (should merge with defaults)
        config = config_manager.load_config("agent_config")

        # Check that global config overrides defaults
        self.assertTrue(config["llm"]["enabled"])
        self.assertEqual(config["llm"]["model"], "gpt-3.5-turbo")
        self.assertEqual(config["llm"]["temperature"], 0.8)

        # Check that defaults are still present for other sections
        self.assertIn("google_drive", config)
        self.assertIn("profile", config)
        self.assertIn("cover_letter", config)

    def test_load_config_with_user_override(self):
        """Test loading configuration with user override."""
        config_manager = ConfigManager("test_config", self.config_dir)

        # Create user config file
        user_config = {
            "llm": {"enabled": True, "model": "gpt-4", "temperature": 0.9},
            "profile": {"resume_file": "my_resume.pdf", "linkedin_url": "https://linkedin.com/in/test"},
        }

        user_config_path = self.user_dir / "agent_config.yaml"
        with open(user_config_path, "w") as f:
            yaml.dump(user_config, f)
        # Debug: print user config file contents
        with open(user_config_path, "r") as f:
            print("[DEBUG] User config file contents:")
            print(f.read())

        # Clear file cache for this file to ensure fresh load
        from core.performance import get_file_cache
        file_cache = get_file_cache()
        file_cache.cache_manager.clear(pattern="agent_config.yaml")

        # Load config (should merge defaults, global, and user)
        config = config_manager.load_config("agent_config")

        # Check that user config overrides defaults
        self.assertTrue(config["llm"]["enabled"])
        self.assertEqual(config["llm"]["model"], "gpt-4")
        expected_temperature = user_config["llm"].get("temperature", config_manager.defaults.agent_defaults["llm"]["temperature"])
        self.assertEqual(config["llm"]["temperature"], expected_temperature)

        # Clear cache to ensure fresh load
        config_manager._config_cache.clear()
        self.assertEqual(config["profile"]["resume_file"], "my_resume.pdf")
        self.assertEqual(config["profile"]["linkedin_url"], "https://linkedin.com/in/test")

        # Check that defaults are still present for other sections
        self.assertIn("google_drive", config)
        self.assertIn("cover_letter", config)

    def test_config_validation(self):
        """Test configuration validation."""
        config_manager = ConfigManager(config_dir=self.config_dir)

        # Test valid config
        try:
            config = config_manager.load_config("agent_config")
            # Should not raise exception
        except Exception as e:
            self.fail(f"Valid config should not raise exception: {e}")

        # Test invalid config (missing required fields in llm)
        invalid_config = {
            "llm": {
                "enabled": True,
                # Missing required fields: model, temperature, max_tokens
            },
            "google_drive": {},
            "profile": {},
            "cover_letter": {},
        }

        invalid_config_path = self.config_dir / "agent_config.yaml"
        with open(invalid_config_path, "w") as f:
            yaml.dump(invalid_config, f)

        # Clear cache to force reload
        config_manager._config_cache.clear()

        # Should raise ConfigurationError for invalid config
        with self.assertRaises(ConfigurationError):
            config_manager._validate_agent_config(invalid_config)

    def test_get_config_value(self):
        """Test getting specific configuration values."""
        config_manager = ConfigManager("test_config", self.config_dir)

        # Test getting nested value
        value = config_manager.get_config_value("agent_config", "llm.enabled")
        self.assertIsInstance(value, bool)

        # Test getting non-existent value
        value = config_manager.get_config_value("agent_config", "nonexistent.key", "default")
        self.assertEqual(value, "default")

        # Test getting value with default
        value = config_manager.get_config_value("agent_config", "llm.custom_setting", "default_value")
        self.assertEqual(value, "default_value")

    def test_set_config_value(self):
        """Test setting specific configuration values."""
        config_manager = ConfigManager("test_config", self.config_dir)

        # Test setting a new value
        config_manager.set_config_value("agent_config", "llm.custom_setting", "test_value")

        # Verify the value was set
        value = config_manager.get_config_value("agent_config", "llm.custom_setting")
        self.assertEqual(value, "test_value")

        # Test setting nested value
        config_manager.set_config_value("agent_config", "profile.custom.nested.key", "nested_value")

        # Verify the nested value was set
        value = config_manager.get_config_value("agent_config", "profile.custom.nested.key")
        self.assertEqual(value, "nested_value")

    def test_save_config(self):
        """Test saving configuration."""
        config_manager = ConfigManager("test_config", self.config_dir)

        # Create a test config
        test_config = {"llm": {"enabled": True, "model": "gpt-4"}, "profile": {"resume_file": "test_resume.pdf"}}

        # Save the config
        config_manager.save_config("agent_config", test_config)

        # Verify the file was created
        config_file = self.user_dir / "agent_config.yaml"
        self.assertTrue(config_file.exists())

        # Verify the content
        with open(config_file, "r") as f:
            saved_config = yaml.safe_load(f)

        self.assertEqual(saved_config["llm"]["enabled"], True)
        self.assertEqual(saved_config["llm"]["model"], "gpt-4")
        self.assertEqual(saved_config["profile"]["resume_file"], "test_resume.pdf")

    def test_list_available_configs(self):
        """Test listing available configurations."""
        config_manager = ConfigManager("test_config", self.config_dir)

        # Create some config files
        configs = ["agent_config", "blurb_logic", "job_targeting"]
        for config_type in configs:
            config_path = self.user_dir / f"{config_type}.yaml"
            with open(config_path, "w") as f:
                yaml.dump({"test": "data"}, f)

        # List available configs
        available_configs = config_manager.list_available_configs()

        # Should include all created configs
        for config_type in configs:
            self.assertIn(config_type, available_configs)

    def test_create_default_config(self):
        """Test creating default configuration templates."""
        config_manager = ConfigManager("test_config", self.config_dir)

        # Test creating agent config template
        agent_template = config_manager.create_default_config("agent_config")
        self.assertIn("llm", agent_template)
        self.assertIn("google_drive", agent_template)
        self.assertIn("profile", agent_template)
        self.assertIn("cover_letter", agent_template)

        # Test creating logic config template
        logic_template = config_manager.create_default_config("blurb_logic")
        self.assertIn("scoring_rules", logic_template)
        self.assertIn("go_no_go", logic_template)
        self.assertIn("job_classification", logic_template)

        # Test creating targeting config template
        targeting_template = config_manager.create_default_config("job_targeting")
        self.assertIn("titles", targeting_template)
        self.assertIn("locations", targeting_template)
        self.assertIn("comp_target", targeting_template)

    def test_validate_all_configs(self):
        """Test validating all configurations."""
        config_manager = ConfigManager("test_config", self.config_dir)

        # Create valid configs
        valid_configs = {
            "agent_config": {
                "llm": {"enabled": False, "model": "gpt-4", "temperature": 0.7, "max_tokens": 1000},
                "google_drive": {"enabled": False},
                "profile": {"resume_file": ""},
                "cover_letter": {"personal_brand": {}, "tone": {}},
            },
            "blurb_logic": {
                "scoring_rules": {"keyword_weights": {}},
                "go_no_go": {"minimum_keywords": 3, "minimum_total_score": 5.0},
                "job_classification": {"leadership": {"keywords": [], "min_keyword_count": 1}},
            },
            "job_targeting": {"titles": {"leadership": [], "IC": []}, "locations": {"preferred": [], "open_to": []}},
        }

        for config_type, config_data in valid_configs.items():
            config_path = self.user_dir / f"{config_type}.yaml"
            with open(config_path, "w") as f:
                yaml.dump(config_data, f)

        # Validate all configs
        errors = config_manager.validate_all_configs()

        # Should have no errors
        self.assertEqual(len(errors), 0)

    def test_config_caching(self):
        """Test that configuration caching works correctly."""
        config_manager = ConfigManager("test_config", self.config_dir)

        # Load config twice
        config1 = config_manager.load_config("agent_config")
        config2 = config_manager.load_config("agent_config")

        # Should be the same object (cached)
        self.assertIs(config1, config2)

        # Clear cache by saving new config
        new_config = {"llm": {"enabled": True}}
        config_manager.save_config("agent_config", new_config)

        # Load again (should be different due to cache invalidation)
        config3 = config_manager.load_config("agent_config")
        self.assertIsNot(config1, config3)


if __name__ == "__main__":
    unittest.main()
