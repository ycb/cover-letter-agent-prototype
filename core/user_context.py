#!/usr/bin/env python3
"""
User Context Management
======================

Handles loading and managing user-specific configuration and data.
"""

from pathlib import Path
from typing import Dict, List, Optional

import yaml

from .exceptions import FileLoadError, UserContextError
from .logging_config import get_logger
from .performance import get_file_cache
from .types import BlurbDict, ConfigDict, EnhancementLogEntry, LogicDict, TargetingDict

logger = get_logger(__name__)


class UserContext:
    """Manages user-specific configuration and data."""

    def __init__(self, user_id: str):
        """Initialize user context for a specific user."""
        self.user_id = user_id
        self.user_dir = Path("users") / user_id

        if not self.user_dir.exists():
            raise UserContextError(f"User directory not found: {self.user_dir}")

        self.config = self._load_config()
        self.blurbs = self._load_blurbs()
        self.logic = self._load_logic()
        self.targeting = self._load_targeting()
        self.resume_path = self._get_resume_path()
        self.pm_inference = self.config.get("pm_inference", {})
        self.work_samples = self._load_work_samples()

    def _load_config(self) -> ConfigDict:
        """Load user configuration."""
        config_path = self.user_dir / "config.yaml"
        if not config_path.exists():
            raise FileLoadError(f"Config file not found: {config_path}")

        try:
            # Use cached file loading
            file_cache = get_file_cache()
            config = file_cache.load_yaml_file(config_path)

            logger.info(f"Loaded config for user: {self.user_id}")
            return config
        except Exception as e:
            logger.error(f"Unexpected error loading config for user {self.user_id}: {e}")
            raise FileLoadError(f"Failed to load config for user {self.user_id}: {e}")

    def _load_blurbs(self) -> Dict[str, List[BlurbDict]]:
        """Load user blurbs."""
        blurbs_path = self.user_dir / "blurbs.yaml"
        if not blurbs_path.exists():
            raise FileLoadError(f"Blurbs file not found: {blurbs_path}")

        try:
            # Use cached file loading
            file_cache = get_file_cache()
            blurbs = file_cache.load_yaml_file(blurbs_path)

            logger.info(f"Loaded blurbs for user: {self.user_id}")
            return blurbs
        except Exception as e:
            logger.error(f"Unexpected error loading blurbs for user {self.user_id}: {e}")
            raise FileLoadError(f"Failed to load blurbs for user {self.user_id}: {e}")

    def _load_logic(self) -> LogicDict:
        """Load user blurb logic."""
        logic_path = self.user_dir / "blurb_logic.yaml"
        if not logic_path.exists():
            raise FileLoadError(f"Logic file not found: {logic_path}")

        try:
            # Use cached file loading
            file_cache = get_file_cache()
            logic = file_cache.load_yaml_file(logic_path)

            logger.info(f"Loaded logic for user: {self.user_id}")
            return logic
        except Exception as e:
            logger.error(f"Unexpected error loading logic for user {self.user_id}: {e}")
            raise FileLoadError(f"Failed to load logic for user {self.user_id}: {e}")

    def _load_targeting(self) -> TargetingDict:
        """Load user job targeting rules."""
        targeting_path = self.user_dir / "job_targeting.yaml"
        if not targeting_path.exists():
            raise FileLoadError(f"Targeting file not found: {targeting_path}")

        try:
            # Use cached file loading
            file_cache = get_file_cache()
            targeting = file_cache.load_yaml_file(targeting_path)

            logger.info(f"Loaded targeting for user: {self.user_id}")
            return targeting
        except Exception as e:
            logger.error(f"Unexpected error loading targeting for user {self.user_id}: {e}")
            raise FileLoadError(f"Failed to load targeting for user {self.user_id}: {e}")

    def _load_work_samples(self):
        """Load user work samples (STAR stories, case studies, etc.)."""
        work_samples_file = self.config.get("work_samples_file", "work_samples.yaml")
        work_samples_path = self.user_dir / work_samples_file
        if not work_samples_path.exists():
            logger.warning(f"Work samples file not found: {work_samples_path}")
            return []
        try:
            file_cache = get_file_cache()
            work_samples = file_cache.load_yaml_file(work_samples_path)
            logger.info(f"Loaded work samples for user: {self.user_id}")
            return work_samples
        except Exception as e:
            logger.error(f"Unexpected error loading work samples for user {self.user_id}: {e}")
            return []

    def _get_resume_path(self) -> Optional[Path]:
        """Get user resume path from config.yaml profile.resume_file."""
        resume_file = self.config.get("profile", {}).get("resume_file", "resume.pdf")
        resume_path = self.user_dir / resume_file
        if resume_path.exists():
            logger.info(f"Found resume for user: {self.user_id}")
            return resume_path
        else:
            logger.warning(f"No resume found for user: {self.user_id} at {resume_path}")
            return None

    def get_google_drive_config(self) -> ConfigDict:
        """Get Google Drive configuration for user."""
        return self.config.get("google_drive", {})

    def get_profile_config(self) -> ConfigDict:
        """Get profile configuration for user."""
        return self.config.get("profile", {})

    def get_cover_letter_config(self) -> ConfigDict:
        """Get cover letter configuration for user."""
        return self.config.get("cover_letter", {})

    def get_user_name(self) -> str:
        """Get user's name."""
        return self.config.get("name", self.user_id)

    def get_user_role(self) -> str:
        """Get user's role."""
        return self.config.get("role", "product leader")

    def get_user_location(self) -> str:
        """Get user's location."""
        return self.config.get("location", "San Francisco, CA")

    def get_industry_focus(self) -> List[str]:
        """Get user's industry focus areas."""
        return self.config.get("industry_focus", [])

    def get_preferred_examples(self) -> List[str]:
        """Get user's preferred examples."""
        return self.config.get("preferred_examples", [])

    def get_examples_dir(self) -> Path:
        """Get user's examples directory."""
        examples_dir = self.user_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        return examples_dir

    def get_pm_inference(self) -> Dict:
        """Get PM inference results for user."""
        return self.pm_inference

    def get_work_samples(self) -> List[Dict]:
        """Get user's work samples (STAR stories, case studies, etc.)."""
        return self.work_samples

    def save_enhancement_log(self, log_data: List[EnhancementLogEntry]) -> None:
        """Save enhancement log for user."""
        log_path = self.user_dir / "enhancement_log.csv"

        if not log_data:
            logger.debug(f"No enhancement log data to save for user: {self.user_id}")
            return

        try:
            import csv

            fieldnames = log_data[0].keys()
            with open(log_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(log_data)

            logger.info(f"Saved {len(log_data)} enhancement log entries for user: {self.user_id}")
        except (IOError, OSError) as e:
            logger.error(f"Failed to write enhancement log to {log_path}: {e}")
        except Exception as e:
            logger.error(f"Unexpected error saving enhancement log for user {self.user_id}: {e}")

    def load_enhancement_log(self) -> List[EnhancementLogEntry]:
        """Load enhancement log for user."""
        log_path = self.user_dir / "enhancement_log.csv"

        if not log_path.exists():
            logger.debug(f"Enhancement log file not found for user {self.user_id}: {log_path}")
            return []

        try:
            import csv

            with open(log_path, "r") as f:
                reader = csv.DictReader(f)
                log_entries = list(reader)
                logger.debug(f"Loaded {len(log_entries)} enhancement log entries for user: {self.user_id}")
                return log_entries
        except FileNotFoundError:
            logger.warning(f"Enhancement log file not found for user {self.user_id}: {log_path}")
            return []
        except csv.Error as e:
            logger.error(f"Error parsing enhancement log CSV for user {self.user_id}: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error loading enhancement log for user {self.user_id}: {e}")
            return []


def load_user_context(user_id: str) -> UserContext:
    """Load user context for a specific user."""
    return UserContext(user_id)


def list_available_users() -> List[str]:
    """List all available users."""
    users_dir = Path("users")
    if not users_dir.exists():
        return []

    users = [d.name for d in users_dir.iterdir() if d.is_dir()]
    return sorted(users)


def validate_user_exists(user_id: str) -> bool:
    """Check if a user exists."""
    user_dir = Path("users") / user_id
    return user_dir.exists() and user_dir.is_dir()
