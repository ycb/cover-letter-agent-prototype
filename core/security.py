#!/usr/bin/env python3
"""
Security and Secrets Management
==============================

Provides secure handling of API keys, credentials, and sensitive configuration.
"""

import os
import re
import secrets
import string
from pathlib import Path
from typing import Dict, List, Optional, Set
from urllib.parse import urlparse

from .exceptions import SecurityError
from .logging_config import get_logger

logger = get_logger(__name__)


class SecurityManager:
    """Manages security and secrets for the application."""

    def __init__(self):
        """Initialize security manager."""
        self.required_secrets: Set[str] = set()
        self.optional_secrets: Set[str] = set()
        self.secret_patterns: Dict[str, re.Pattern] = {}
        self._initialize_secret_patterns()

    def _initialize_secret_patterns(self) -> None:
        """Initialize patterns for detecting secrets."""
        self.secret_patterns = {
            "openai_api_key": re.compile(r"sk-[a-zA-Z0-9]{48}"),
            "github_token": re.compile(r"ghp_[a-zA-Z0-9]{36}"),
            "google_credentials": re.compile(r'"client_email":\s*"[^"]+@[^"]+\.iam\.gserviceaccount\.com"'),
            "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
            "aws_secret_key": re.compile(r"[0-9a-zA-Z/+]{40}"),
            "generic_api_key": re.compile(r"[a-zA-Z0-9]{32,}"),
        }

    def register_required_secret(self, secret_name: str) -> None:
        """Register a required secret."""
        self.required_secrets.add(secret_name)

    def register_optional_secret(self, secret_name: str) -> None:
        """Register an optional secret."""
        self.optional_secrets.add(secret_name)

    def get_secret(self, secret_name: str, default: Optional[str] = None) -> Optional[str]:
        """Get a secret from environment variables."""
        value = os.getenv(secret_name, default)
        
        if secret_name in self.required_secrets and not value:
            logger.error(f"Required secret '{secret_name}' not found in environment")
            raise SecurityError(f"Required secret '{secret_name}' not found")
        
        if value:
            logger.debug(f"Retrieved secret '{secret_name}' from environment")
        else:
            logger.debug(f"Secret '{secret_name}' not found (optional: {secret_name not in self.required_secrets})")
        
        return value

    def validate_secret_format(self, secret_name: str, value: str) -> bool:
        """Validate secret format based on type."""
        if secret_name == "OPENAI_API_KEY":
            return value.startswith("sk-") and len(value) >= 50
        elif secret_name == "GOOGLE_CREDENTIALS_FILE":
            return Path(value).exists() and value.endswith(".json")
        elif secret_name == "GOOGLE_FOLDER_ID":
            return len(value) > 0
        else:
            # Generic validation for other secrets
            return len(value) >= 8

    def scan_for_secrets(self, file_path: Path) -> List[Dict[str, str]]:
        """Scan a file for potential secrets."""
        if not file_path.exists():
            return []

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            logger.warning(f"Could not read file {file_path}: {e}")
            return []

        found_secrets = []
        
        for secret_type, pattern in self.secret_patterns.items():
            matches = pattern.findall(content)
            for match in matches:
                found_secrets.append({
                    "type": secret_type,
                    "value": match[:10] + "..." if len(match) > 10 else match,
                    "file": str(file_path),
                    "line": self._find_line_number(content, match)
                })

        return found_secrets

    def _find_line_number(self, content: str, match: str) -> int:
        """Find the line number of a match in content."""
        lines = content.split("\n")
        for i, line in enumerate(lines, 1):
            if match in line:
                return i
        return 0

    def audit_secrets(self, directory: Path) -> Dict[str, List[Dict[str, str]]]:
        """Audit a directory for secrets."""
        audit_results = {
            "secrets_found": [],
            "files_scanned": 0,
            "potential_issues": []
        }

        # Files to scan
        scan_extensions = {".py", ".yaml", ".yml", ".json", ".md", ".txt"}
        skip_patterns = {
            "__pycache__", ".git", "venv", "env", ".pytest_cache",
            "node_modules", ".cache", "build", "dist"
        }

        for file_path in directory.rglob("*"):
            if file_path.is_file():
                # Skip certain directories and files
                if any(pattern in str(file_path) for pattern in skip_patterns):
                    continue
                
                if file_path.suffix in scan_extensions:
                    audit_results["files_scanned"] += 1
                    secrets = self.scan_for_secrets(file_path)
                    audit_results["secrets_found"].extend(secrets)

        return audit_results

    def generate_secure_password(self, length: int = 32) -> str:
        """Generate a secure random password."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    def validate_url(self, url: str) -> bool:
        """Validate a URL for security."""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except Exception:
            return False

    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename for security."""
        # Remove potentially dangerous characters
        sanitized = re.sub(r"[^a-zA-Z0-9._-]", "_", filename)
        # Prevent directory traversal
        sanitized = sanitized.replace("..", "_")
        return sanitized

    def check_file_permissions(self, file_path: Path) -> Dict[str, bool]:
        """Check file permissions for security."""
        try:
            stat = file_path.stat()
            return {
                "readable": os.access(file_path, os.R_OK),
                "writable": os.access(file_path, os.W_OK),
                "executable": os.access(file_path, os.X_OK),
                "owner_only": stat.st_mode & 0o777 == 0o600,
            }
        except Exception as e:
            logger.warning(f"Could not check permissions for {file_path}: {e}")
            return {
                "readable": False,
                "writable": False,
                "executable": False,
                "owner_only": False,
            }


class EnvironmentConfig:
    """Manages environment-based configuration securely."""

    def __init__(self):
        """Initialize environment configuration."""
        self.security_manager = SecurityManager()
        self._register_secrets()

    def _register_secrets(self) -> None:
        """Register required and optional secrets."""
        # Required secrets
        self.security_manager.register_required_secret("OPENAI_API_KEY")
        
        # Optional secrets
        self.security_manager.register_optional_secret("GOOGLE_CREDENTIALS_FILE")
        self.security_manager.register_optional_secret("GOOGLE_FOLDER_ID")
        self.security_manager.register_optional_secret("GOOGLE_SERVICE_ACCOUNT_EMAIL")

    def load_environment_config(self) -> Dict[str, str]:
        """Load configuration from environment variables."""
        config = {}
        
        # Load required secrets
        try:
            config["openai_api_key"] = self.security_manager.get_secret("OPENAI_API_KEY")
        except SecurityError as e:
            logger.warning(f"OpenAI API key not available: {e}")
            config["openai_api_key"] = None

        # Load optional secrets
        config["google_credentials_file"] = self.security_manager.get_secret("GOOGLE_CREDENTIALS_FILE", "credentials.json")
        config["google_folder_id"] = self.security_manager.get_secret("GOOGLE_FOLDER_ID", "")
        config["google_service_account_email"] = self.security_manager.get_secret("GOOGLE_SERVICE_ACCOUNT_EMAIL", "")

        return config

    def validate_config(self, config: Dict[str, str]) -> List[str]:
        """Validate configuration for security issues."""
        issues = []
        
        # Check OpenAI API key
        if config.get("openai_api_key"):
            if not self.security_manager.validate_secret_format("OPENAI_API_KEY", config["openai_api_key"]):
                issues.append("Invalid OpenAI API key format")

        # Check Google credentials file
        if config.get("google_credentials_file"):
            creds_file = Path(config["google_credentials_file"])
            if not creds_file.exists():
                issues.append(f"Google credentials file not found: {creds_file}")
            else:
                # Check file permissions
                permissions = self.security_manager.check_file_permissions(creds_file)
                if not permissions["owner_only"]:
                    issues.append(f"Google credentials file has insecure permissions: {creds_file}")

        return issues


class SecretsValidator:
    """Validates secrets and configuration for security."""

    def __init__(self):
        """Initialize secrets validator."""
        self.security_manager = SecurityManager()

    def validate_project_security(self, project_dir: Path) -> Dict[str, any]:
        """Validate project security."""
        results = {
            "audit_results": self.security_manager.audit_secrets(project_dir),
            "environment_config": self._validate_environment(),
            "file_permissions": self._check_critical_files(project_dir),
            "overall_score": 0
        }
        
        # Calculate security score
        score = 100
        
        # Deduct points for found secrets
        if results["audit_results"]["secrets_found"]:
            score -= len(results["audit_results"]["secrets_found"]) * 10
        
        # Deduct points for permission issues
        if results["file_permissions"]["issues"]:
            score -= len(results["file_permissions"]["issues"]) * 5
        
        results["overall_score"] = max(0, score)
        
        return results

    def _validate_environment(self) -> Dict[str, any]:
        """Validate environment configuration."""
        env_config = EnvironmentConfig()
        config = env_config.load_environment_config()
        issues = env_config.validate_config(config)
        
        return {
            "config": config,
            "issues": issues,
            "valid": len(issues) == 0
        }

    def _check_critical_files(self, project_dir: Path) -> Dict[str, any]:
        """Check permissions on critical files."""
        critical_files = [
            project_dir / "credentials.json",
            project_dir / ".env",
            project_dir / "users" / "peter" / "config.yaml",
        ]
        
        issues = []
        for file_path in critical_files:
            if file_path.exists():
                permissions = self.security_manager.check_file_permissions(file_path)
                if not permissions["owner_only"]:
                    issues.append(f"Insecure permissions on {file_path}")
        
        return {
            "files_checked": len(critical_files),
            "issues": issues,
            "secure": len(issues) == 0
        }


# Global instances
security_manager = SecurityManager()
environment_config = EnvironmentConfig()
secrets_validator = SecretsValidator()


def get_security_manager() -> SecurityManager:
    """Get the global security manager instance."""
    return security_manager


def get_environment_config() -> EnvironmentConfig:
    """Get the global environment configuration instance."""
    return environment_config


def get_secrets_validator() -> SecretsValidator:
    """Get the global secrets validator instance."""
    return secrets_validator


def validate_secrets() -> Dict[str, any]:
    """Validate all secrets and configuration."""
    return secrets_validator.validate_project_security(Path(".")) 