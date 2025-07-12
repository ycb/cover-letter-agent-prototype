#!/usr/bin/env python3
"""
Test Error Handling Improvements
===============================

Tests the improved error handling and logging functionality.
"""

import shutil
import tempfile
import unittest
from pathlib import Path

import yaml

from core.exceptions import ConfigurationError, CoverLetterAgentError, FileLoadError, UserContextError
from core.logging_config import get_logger, setup_logging
from core.user_context import UserContext


class TestErrorHandling(unittest.TestCase):
    """Test error handling improvements."""

    def setUp(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.logger = setup_logging(level="DEBUG")

    def tearDown(self):
        """Clean up test environment."""
        shutil.rmtree(self.temp_dir)

    def test_custom_exceptions(self):
        """Test that custom exceptions work correctly."""
        # Test base exception
        with self.assertRaises(CoverLetterAgentError):
            raise CoverLetterAgentError("Test error")

        # Test specific exceptions
        with self.assertRaises(FileLoadError):
            raise FileLoadError("File not found")

        with self.assertRaises(UserContextError):
            raise UserContextError("User context error")

    def test_logging_setup(self):
        """Test logging configuration."""
        logger = get_logger("test_logger")
        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test_logger")

    def test_file_load_error_handling(self):
        """Test file loading error handling."""
        # Test missing user directory
        with self.assertRaises(UserContextError) as cm:
            UserContext("nonexistent_user")

        self.assertIn("User directory not found", str(cm.exception))

    def test_invalid_yaml_handling(self):
        """Test handling of invalid YAML files."""
        # Create test user directory in the actual users directory
        user_dir = Path("users") / "test_invalid_yaml"
        user_dir.mkdir(exist_ok=True)

        # Create invalid YAML files (UserContext requires all files)
        config_path = user_dir / "config.yaml"
        with open(config_path, "w") as f:
            f.write("invalid: yaml: content: [")

        blurbs_path = user_dir / "blurbs.yaml"
        with open(blurbs_path, "w") as f:
            f.write("valid: content")

        logic_path = user_dir / "blurb_logic.yaml"
        with open(logic_path, "w") as f:
            f.write("valid: content")

        targeting_path = user_dir / "job_targeting.yaml"
        with open(targeting_path, "w") as f:
            f.write("valid: content")

        # Test that invalid YAML raises appropriate exception
        with self.assertRaises(FileLoadError) as cm:
            UserContext("test_invalid_yaml")

        # The error message changed with performance optimizations
        self.assertIn("Failed to load", str(cm.exception))

        # Clean up
        shutil.rmtree(user_dir)

    def test_empty_yaml_handling(self):
        """Test handling of empty YAML files (should not raise, but config should be empty)."""
        # Create test user directory in the actual users directory
        user_dir = Path("users") / "test_empty_yaml"
        user_dir.mkdir(exist_ok=True)

        # Create empty YAML files (UserContext requires all files)
        config_path = user_dir / "config.yaml"
        with open(config_path, "w") as f:
            f.write("")
        blurbs_path = user_dir / "blurbs.yaml"
        with open(blurbs_path, "w") as f:
            f.write("")
        logic_path = user_dir / "blurb_logic.yaml"
        with open(logic_path, "w") as f:
            f.write("")
        targeting_path = user_dir / "job_targeting.yaml"
        with open(targeting_path, "w") as f:
            f.write("")

        # Should not raise, but config should be empty
        ctx = UserContext("test_empty_yaml")
        self.assertEqual(ctx.config, {})

    def test_config_validation_on_empty(self):
        """Test that config validation fails on empty config."""
        from core.config_manager import ConfigManager, ConfigurationError

        user_dir = Path("users") / "test_empty_yaml"
        ctx = UserContext("test_empty_yaml")
        config_manager = ConfigManager("test_empty_yaml", config_dir=Path("data"))
        # Should raise on validation if required keys are missing
        with self.assertRaises(ConfigurationError):
            config_manager._validate_config("agent_config", ctx.config)

    def test_valid_config_loading(self):
        """Test loading valid configuration."""
        # Create test user directory in the actual users directory
        user_dir = Path("users") / "test_valid_user"
        user_dir.mkdir(exist_ok=True)

        # Create valid config file
        config_path = user_dir / "config.yaml"
        config_data = {"name": "Test User", "role": "product leader", "location": "San Francisco, CA"}

        with open(config_path, "w") as f:
            yaml.dump(config_data, f)

        # Create other required files
        for filename in ["blurbs.yaml", "blurb_logic.yaml", "job_targeting.yaml"]:
            file_path = user_dir / filename
            with open(file_path, "w") as f:
                yaml.dump({"test": "data"}, f)

        # Test that valid config loads without error
        try:
            user_context = UserContext("test_valid_user")
            self.assertEqual(user_context.get_user_name(), "Test User")
            self.assertEqual(user_context.get_user_role(), "product leader")
        except Exception as e:
            self.fail(f"Valid config should load without error: {e}")
        finally:
            # Clean up
            shutil.rmtree(user_dir)


if __name__ == "__main__":
    unittest.main()
