#!/usr/bin/env python3
"""
User Context Management
======================

Handles loading and managing user-specific configuration and data.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class UserContext:
    """Manages user-specific configuration and data."""
    
    def __init__(self, user_id: str):
        """Initialize user context for a specific user."""
        self.user_id = user_id
        self.user_dir = Path("users") / user_id
        
        if not self.user_dir.exists():
            raise ValueError(f"User directory not found: {self.user_dir}")
        
        self.config = self._load_config()
        self.blurbs = self._load_blurbs()
        self.logic = self._load_logic()
        self.targeting = self._load_targeting()
        self.resume_path = self._get_resume_path()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load user configuration."""
        config_path = self.user_dir / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Loaded config for user: {self.user_id}")
        return config
    
    def _load_blurbs(self) -> Dict[str, Any]:
        """Load user blurbs."""
        blurbs_path = self.user_dir / "blurbs.yaml"
        if not blurbs_path.exists():
            raise FileNotFoundError(f"Blurbs file not found: {blurbs_path}")
        
        with open(blurbs_path, 'r') as f:
            blurbs = yaml.safe_load(f)
        
        logger.info(f"Loaded blurbs for user: {self.user_id}")
        return blurbs
    
    def _load_logic(self) -> Dict[str, Any]:
        """Load user blurb logic."""
        logic_path = self.user_dir / "blurb_logic.yaml"
        if not logic_path.exists():
            raise FileNotFoundError(f"Logic file not found: {logic_path}")
        
        with open(logic_path, 'r') as f:
            logic = yaml.safe_load(f)
        
        logger.info(f"Loaded logic for user: {self.user_id}")
        return logic
    
    def _load_targeting(self) -> Dict[str, Any]:
        """Load user job targeting rules."""
        targeting_path = self.user_dir / "job_targeting.yaml"
        if not targeting_path.exists():
            raise FileNotFoundError(f"Targeting file not found: {targeting_path}")
        
        with open(targeting_path, 'r') as f:
            targeting = yaml.safe_load(f)
        
        logger.info(f"Loaded targeting for user: {self.user_id}")
        return targeting
    
    def _get_resume_path(self) -> Optional[Path]:
        """Get user resume path."""
        resume_path = self.user_dir / "resume.pdf"
        if resume_path.exists():
            logger.info(f"Found resume for user: {self.user_id}")
            return resume_path
        else:
            logger.warning(f"No resume found for user: {self.user_id}")
            return None
    
    def get_google_drive_config(self) -> Dict[str, Any]:
        """Get Google Drive configuration for user."""
        return self.config.get('google_drive', {})
    
    def get_profile_config(self) -> Dict[str, Any]:
        """Get profile configuration for user."""
        return self.config.get('profile', {})
    
    def get_cover_letter_config(self) -> Dict[str, Any]:
        """Get cover letter configuration for user."""
        return self.config.get('cover_letter', {})
    
    def get_user_name(self) -> str:
        """Get user's name."""
        return self.config.get('name', self.user_id)
    
    def get_user_role(self) -> str:
        """Get user's role."""
        return self.config.get('role', 'product leader')
    
    def get_user_location(self) -> str:
        """Get user's location."""
        return self.config.get('location', 'San Francisco, CA')
    
    def get_industry_focus(self) -> list:
        """Get user's industry focus areas."""
        return self.config.get('industry_focus', [])
    
    def get_preferred_examples(self) -> list:
        """Get user's preferred examples."""
        return self.config.get('preferred_examples', [])
    
    def get_examples_dir(self) -> Path:
        """Get user's examples directory."""
        examples_dir = self.user_dir / "examples"
        examples_dir.mkdir(exist_ok=True)
        return examples_dir
    
    def save_enhancement_log(self, log_data: list):
        """Save enhancement log for user."""
        log_path = self.user_dir / "enhancement_log.csv"
        
        if not log_data:
            return
        
        import csv
        fieldnames = log_data[0].keys()
        with open(log_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(log_data)
        
        logger.info(f"Saved enhancement log for user: {self.user_id}")
    
    def load_enhancement_log(self) -> list:
        """Load enhancement log for user."""
        log_path = self.user_dir / "enhancement_log.csv"
        
        if not log_path.exists():
            return []
        
        import csv
        with open(log_path, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader)


def load_user_context(user_id: str) -> UserContext:
    """Load user context for a specific user."""
    return UserContext(user_id)


def list_available_users() -> list:
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