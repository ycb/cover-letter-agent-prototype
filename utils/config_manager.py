#!/usr/bin/env python3
"""
Configuration Manager for Cover Letter Agent
===========================================

Loads and manages configuration settings from YAML files.
"""

import yaml
import os
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """Manages configuration settings for the cover letter agent."""
    
    def __init__(self, config_path: str = "config/agent_config.yaml"):
        """Initialize the configuration manager."""
        self.config_path = config_path
        self.config = self._load_config()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"Config file not found: {self.config_path}")
                return self._get_default_config()
            
            with open(self.config_path, 'r') as file:
                config = yaml.safe_load(file)
                logger.info(f"Configuration loaded from {self.config_path}")
                return config
                
        except Exception as e:
            logger.error(f"Failed to load config from {self.config_path}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file is not found."""
        return {
            'hybrid_selection': {
                'max_llm_candidates': 10,
                'confidence_threshold': 1.0,
                'llm_cost_per_call': 0.01,
                'max_total_time': 2.0,
                'max_cost_per_application': 0.10
            },
            'work_history': {
                'suppressed_inheritance_tags': [
                    'frontend', 'backend', 'mobile', 'web', 'marketing', 'sales'
                ],
                'tag_weights': {
                    'direct': 1.0,
                    'inherited': 0.6,
                    'semantic': 0.8
                }
            },
            'testing': {
                'performance_threshold': 2.0,
                'cost_threshold': 0.10,
                'confidence_threshold': 0.7,
                'success_rate_threshold': 0.8
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                'file': 'logs/cover_letter_agent.log'
            },
            'paths': {
                'work_history': 'users/peter/work_history.yaml',
                'case_studies': 'data/case_studies.yaml',
                'logs': 'logs/',
                'config': 'config/'
            }
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key (supports nested keys with dots)."""
        try:
            keys = key.split('.')
            value = self.config
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            logger.warning(f"Config key '{key}' not found, using default: {default}")
            return default
    
    def get_hybrid_selection_config(self) -> Dict[str, Any]:
        """Get hybrid selection configuration."""
        return self.get('hybrid_selection', {})
    
    def get_work_history_config(self) -> Dict[str, Any]:
        """Get work history configuration."""
        return self.get('work_history', {})
    
    def get_testing_config(self) -> Dict[str, Any]:
        """Get testing configuration."""
        return self.get('testing', {})
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration."""
        return self.get('logging', {})
    
    def get_paths_config(self) -> Dict[str, Any]:
        """Get paths configuration."""
        return self.get('paths', {})
    
    def reload(self) -> None:
        """Reload configuration from file."""
        self.config = self._load_config()
        logger.info("Configuration reloaded")


def setup_logging(config_manager: ConfigManager) -> None:
    """Setup logging based on configuration."""
    logging_config = config_manager.get_logging_config()
    
    # Create logs directory if it doesn't exist
    log_file = logging_config.get('file', 'logs/cover_letter_agent.log')
    log_dir = os.path.dirname(log_file)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, logging_config.get('level', 'INFO')),
        format=logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    logger.info("Logging configured successfully")


def test_config_manager():
    """Test the configuration manager functionality."""
    print("🧪 Testing Configuration Manager...")
    
    config_manager = ConfigManager()
    
    # Test basic get functionality
    max_candidates = config_manager.get('hybrid_selection.max_llm_candidates')
    print(f"  Max LLM candidates: {max_candidates}")
    
    # Test nested get functionality
    confidence_threshold = config_manager.get('hybrid_selection.confidence_threshold')
    print(f"  Confidence threshold: {confidence_threshold}")
    
    # Test default value
    unknown_key = config_manager.get('unknown.key', 'default_value')
    print(f"  Unknown key with default: {unknown_key}")
    
    # Test configuration sections
    hybrid_config = config_manager.get_hybrid_selection_config()
    print(f"  Hybrid selection config: {hybrid_config}")
    
    work_history_config = config_manager.get_work_history_config()
    print(f"  Work history config: {len(work_history_config.get('suppressed_inheritance_tags', []))} suppressed tags")
    
    print("✅ Configuration Manager test completed!")


if __name__ == "__main__":
    test_config_manager() 