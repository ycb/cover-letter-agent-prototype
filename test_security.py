#!/usr/bin/env python3
"""
Test Security and Secrets Management
===================================

NOTE: All secrets and API keys in this file are dummy/test values ONLY. No real credentials are present.

Tests the security and secrets management functionality.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from core.security import (
    SecurityManager,
    EnvironmentConfig,
    SecretsValidator,
    get_security_manager,
    get_environment_config,
    get_secrets_validator,
    validate_secrets,
)
from core.exceptions import SecurityError


class TestSecurityManager:
    """Test security manager functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.security_manager = SecurityManager()

    def test_secret_registration(self):
        """Test secret registration."""
        self.security_manager.register_required_secret("TEST_REQUIRED")
        self.security_manager.register_optional_secret("TEST_OPTIONAL")
        
        assert "TEST_REQUIRED" in self.security_manager.required_secrets
        assert "TEST_OPTIONAL" in self.security_manager.optional_secrets

    def test_get_secret_success(self):
        """Test successful secret retrieval."""
        with patch.dict(os.environ, {"TEST_SECRET": "test_value"}):
            value = self.security_manager.get_secret("TEST_SECRET")
            assert value == "test_value"

    def test_get_required_secret_missing(self):
        """Test missing required secret raises error."""
        self.security_manager.register_required_secret("MISSING_SECRET")
        
        with pytest.raises(SecurityError):
            self.security_manager.get_secret("MISSING_SECRET")

    def test_get_optional_secret_missing(self):
        """Test missing optional secret returns None."""
        self.security_manager.register_optional_secret("OPTIONAL_SECRET")
        
        value = self.security_manager.get_secret("OPTIONAL_SECRET")
        assert value is None

    def test_validate_secret_format(self):
        """Test secret format validation."""
        # Valid OpenAI API key
        assert self.security_manager.validate_secret_format("OPENAI_API_KEY", "sk-test123456789012345678901234567890123456789012345678901234567890")
        
        # Invalid OpenAI API key
        assert not self.security_manager.validate_secret_format("OPENAI_API_KEY", "invalid-key")
        
        # Valid generic secret
        assert self.security_manager.validate_secret_format("GENERIC_SECRET", "valid-secret-123")
        
        # Invalid generic secret (too short)
        assert not self.security_manager.validate_secret_format("GENERIC_SECRET", "short")

    def test_scan_for_secrets(self):
        """Test secret scanning in files."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as f:
            f.write("""
# Test file with potential secrets
api_key = "sk-test123456789012345678901234567890123456789012345678901234567890"
github_token = "ghp_test123456789012345678901234567890123456"
normal_text = "This is just normal text"
""")
            temp_file = Path(f.name)
        
        try:
            secrets = self.security_manager.scan_for_secrets(temp_file)
            
            # Should find OpenAI API key and GitHub token
            secret_types = [secret["type"] for secret in secrets]
            assert "openai_api_key" in secret_types
            assert "github_token" in secret_types
            assert len(secrets) >= 2
            
        finally:
            temp_file.unlink()

    def test_generate_secure_password(self):
        """Test secure password generation."""
        password = self.security_manager.generate_secure_password(16)
        assert len(password) == 16
        assert any(c.isupper() for c in password)
        assert any(c.islower() for c in password)
        assert any(c.isdigit() for c in password)

    def test_validate_url(self):
        """Test URL validation."""
        assert self.security_manager.validate_url("https://example.com")
        assert self.security_manager.validate_url("http://localhost:8000")
        assert not self.security_manager.validate_url("not-a-url")
        assert not self.security_manager.validate_url("")

    def test_sanitize_filename(self):
        """Test filename sanitization."""
        # Test normal filename
        assert self.security_manager.sanitize_filename("test.txt") == "test.txt"
        
        # Test dangerous characters
        assert self.security_manager.sanitize_filename("test<script>.txt") == "test_script_.txt"
        
        # Test directory traversal
        assert self.security_manager.sanitize_filename("../../../etc/passwd") == "______etc_passwd"

    def test_check_file_permissions(self):
        """Test file permission checking."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = Path(f.name)
        
        try:
            permissions = self.security_manager.check_file_permissions(temp_file)
            
            assert isinstance(permissions, dict)
            assert "readable" in permissions
            assert "writable" in permissions
            assert "executable" in permissions
            assert "owner_only" in permissions
            
        finally:
            temp_file.unlink()


class TestEnvironmentConfig:
    """Test environment configuration functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.env_config = EnvironmentConfig()

    def test_register_secrets(self):
        """Test that secrets are properly registered."""
        assert "OPENAI_API_KEY" in self.env_config.security_manager.required_secrets
        assert "GOOGLE_CREDENTIALS_FILE" in self.env_config.security_manager.optional_secrets
        assert "GOOGLE_FOLDER_ID" in self.env_config.security_manager.optional_secrets

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123456789012345678901234567890123456789012345678901234567890"})
    def test_load_environment_config_with_api_key(self):
        """Test loading environment config with API key."""
        config = self.env_config.load_environment_config()
        
        assert config["openai_api_key"] == "sk-test123456789012345678901234567890123456789012345678901234567890"
        assert config["google_credentials_file"] == "credentials.json"
        assert config["google_folder_id"] == ""

    @patch.dict(os.environ, {}, clear=True)
    def test_load_environment_config_without_api_key(self):
        """Test loading environment config without API key."""
        config = self.env_config.load_environment_config()
        
        assert config["openai_api_key"] is None
        assert config["google_credentials_file"] == "credentials.json"

    def test_validate_config_valid(self):
        """Test config validation with valid config."""
        config = {
            "openai_api_key": "sk-test123456789012345678901234567890123456789012345678901234567890",
            "google_credentials_file": "credentials.json"
        }
        
        # Create a temporary credentials file for testing
        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            f.write(b'{"test": "credentials"}')
            temp_creds = Path(f.name)
        
        try:
            config["google_credentials_file"] = str(temp_creds)
            issues = self.env_config.validate_config(config)
            assert len(issues) == 0
        finally:
            temp_creds.unlink()

    def test_validate_config_invalid_api_key(self):
        """Test config validation with invalid API key."""
        config = {
            "openai_api_key": "invalid-key",
            "google_credentials_file": "credentials.json"
        }
        
        issues = self.env_config.validate_config(config)
        assert len(issues) > 0
        assert any("Invalid OpenAI API key format" in issue for issue in issues)


class TestSecretsValidator:
    """Test secrets validator functionality."""

    def setup_method(self):
        """Set up test environment."""
        self.validator = SecretsValidator()

    def test_validate_project_security(self):
        """Test project security validation."""
        results = self.validator.validate_project_security(Path("."))
        
        assert isinstance(results, dict)
        assert "audit_results" in results
        assert "environment_config" in results
        assert "file_permissions" in results
        assert "overall_score" in results
        assert 0 <= results["overall_score"] <= 100

    def test_validate_environment(self):
        """Test environment validation."""
        env_results = self.validator._validate_environment()
        
        assert isinstance(env_results, dict)
        assert "config" in env_results
        assert "issues" in env_results
        assert "valid" in env_results

    def test_check_critical_files(self):
        """Test critical file permission checking."""
        perm_results = self.validator._check_critical_files(Path("."))
        
        assert isinstance(perm_results, dict)
        assert "files_checked" in perm_results
        assert "issues" in perm_results
        assert "secure" in perm_results


class TestGlobalFunctions:
    """Test global security functions."""

    def test_get_security_manager(self):
        """Test getting global security manager."""
        manager = get_security_manager()
        assert isinstance(manager, SecurityManager)

    def test_get_environment_config(self):
        """Test getting global environment config."""
        config = get_environment_config()
        assert isinstance(config, EnvironmentConfig)

    def test_get_secrets_validator(self):
        """Test getting global secrets validator."""
        validator = get_secrets_validator()
        assert isinstance(validator, SecretsValidator)

    def test_validate_secrets(self):
        """Test global validate_secrets function."""
        results = validate_secrets()
        assert isinstance(results, dict)
        assert "overall_score" in results


class TestSecurityIntegration:
    """Test security integration with existing code."""

    @patch.dict(os.environ, {"OPENAI_API_KEY": "sk-test123456789012345678901234567890123456789012345678901234567890"})
    def test_api_key_validation_in_gap_analysis(self):
        """Test that gap analysis validates API keys."""
        from agents.gap_analysis import extract_requirements_llm
        
        # This should not raise an error with a valid API key
        try:
            # Mock the OpenAI client to avoid actual API calls
            with patch('agents.gap_analysis.openai.OpenAI'):
                extract_requirements_llm("test job description", "sk-test123456789012345678901234567890123456789012345678901234567890")
        except Exception as e:
            # Should not raise SecurityError for valid key
            assert not isinstance(e, SecurityError)

    def test_api_key_validation_invalid(self):
        """Test that gap analysis rejects invalid API keys."""
        from agents.gap_analysis import extract_requirements_llm
        
        with pytest.raises(ValueError, match="Invalid OpenAI API key format"):
            extract_requirements_llm("test job description", "invalid-key")


if __name__ == "__main__":
    pytest.main([__file__]) 