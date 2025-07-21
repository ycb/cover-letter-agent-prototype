"""
Comprehensive tests for schema validation system.

Tests the JSON schema validation, custom validations, and CLI tools.
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch, mock_open

from core.schema_validator import SchemaValidator, validate_user_blurbs, validate_all_user_blurbs


class TestSchemaValidator:
    """Test the SchemaValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = SchemaValidator()
        
        # Sample valid blurbs
        self.valid_blurbs = {
            "intro": [
                {
                    "id": "standard",
                    "tags": ["all"],
                    "text": "I'm a product leader with 15+ years of experience building user-centric products."
                }
            ],
            "paragraph2": [
                {
                    "id": "cleantech",
                    "tags": ["cleantech", "climate", "energy"],
                    "text": "Five years in solar SaaS has given me a deep understanding of the needs of homeowners."
                }
            ],
            "examples": [
                {
                    "id": "enact",
                    "tags": ["growth", "leadership", "founding_pm"],
                    "text": "At Enact, I led product for post-sale tools that monitor performance."
                }
            ]
        }
    
    def test_valid_blurbs_pass_validation(self):
        """Test that valid blurbs pass validation."""
        is_valid, errors = self.validator.validate_blurbs(self.valid_blurbs)
        assert is_valid
        assert len(errors) == 0
    
    def test_missing_required_sections(self):
        """Test validation fails when required sections are missing."""
        invalid_blurbs = {
            "intro": self.valid_blurbs["intro"]
            # Missing paragraph2 and examples
        }
        
        is_valid, errors = self.validator.validate_blurbs(invalid_blurbs)
        assert not is_valid
        assert len(errors) >= 1  # Should have at least one error for missing sections
    
    def test_missing_required_fields(self):
        """Test validation fails when required fields are missing."""
        invalid_blurbs = {
            "intro": [
                {
                    "id": "standard",
                    "text": "Missing tags field"
                }
            ],
            "paragraph2": self.valid_blurbs["paragraph2"],
            "examples": self.valid_blurbs["examples"]
        }
        
        is_valid, errors = self.validator.validate_blurbs(invalid_blurbs)
        assert not is_valid
        assert any("required" in error.lower() for error in errors)
    
    def test_duplicate_blurb_ids(self):
        """Test validation fails when blurb IDs are duplicated."""
        invalid_blurbs = {
            "intro": [
                {
                    "id": "standard",
                    "tags": ["all"],
                    "text": "First blurb"
                },
                {
                    "id": "standard",  # Duplicate ID
                    "tags": ["growth"],
                    "text": "Second blurb with same ID"
                }
            ],
            "paragraph2": self.valid_blurbs["paragraph2"],
            "examples": self.valid_blurbs["examples"]
        }
        
        is_valid, errors = self.validator.validate_blurbs(invalid_blurbs)
        assert not is_valid
        assert any("Duplicate blurb ID" in error for error in errors)
    
    def test_invalid_blurb_id_format(self):
        """Test validation fails with invalid blurb ID format."""
        invalid_blurbs = {
            "intro": [
                {
                    "id": "invalid-id",  # Contains hyphen
                    "tags": ["all"],
                    "text": "Valid text"
                }
            ],
            "paragraph2": self.valid_blurbs["paragraph2"],
            "examples": self.valid_blurbs["examples"]
        }
        
        is_valid, errors = self.validator.validate_blurbs(invalid_blurbs)
        assert not is_valid
        assert any("pattern" in error.lower() or "invalid" in error.lower() for error in errors)
    
    def test_invalid_tag_format(self):
        """Test validation fails with invalid tag format."""
        invalid_blurbs = {
            "intro": [
                {
                    "id": "standard",
                    "tags": ["valid_tag", "invalid-tag"],  # Contains hyphen
                    "text": "Valid text"
                }
            ],
            "paragraph2": self.valid_blurbs["paragraph2"],
            "examples": self.valid_blurbs["examples"]
        }
        
        is_valid, errors = self.validator.validate_blurbs(invalid_blurbs)
        assert not is_valid
        assert any("pattern" in error.lower() or "invalid" in error.lower() for error in errors)
    
    def test_text_length_validation(self):
        """Test validation of text length constraints."""
        # Test too short text
        short_blurbs = {
            "intro": [
                {
                    "id": "short",
                    "tags": ["all"],
                    "text": "Too short"  # Less than 10 characters
                }
            ],
            "paragraph2": self.valid_blurbs["paragraph2"],
            "examples": self.valid_blurbs["examples"]
        }
        
        is_valid, errors = self.validator.validate_blurbs(short_blurbs)
        assert not is_valid
        assert any("too short" in error for error in errors)
        
        # Test too long text
        long_text = "x" * 2001  # More than 2000 characters
        long_blurbs = {
            "intro": [
                {
                    "id": "long",
                    "tags": ["all"],
                    "text": long_text
                }
            ],
            "paragraph2": self.valid_blurbs["paragraph2"],
            "examples": self.valid_blurbs["examples"]
        }
        
        is_valid, errors = self.validator.validate_blurbs(long_blurbs)
        assert not is_valid
        assert any("too long" in error for error in errors)
    
    def test_malformed_blurb_structure(self):
        """Test validation fails with malformed blurb structure."""
        invalid_blurbs = {
            "intro": [
                "not_a_dict",  # Should be a dictionary
                {
                    "id": "valid",
                    "tags": ["all"],
                    "text": "Valid blurb"
                }
            ],
            "paragraph2": self.valid_blurbs["paragraph2"],
            "examples": self.valid_blurbs["examples"]
        }
        
        is_valid, errors = self.validator.validate_blurbs(invalid_blurbs)
        assert not is_valid
        assert any("type" in error.lower() or "object" in error.lower() for error in errors)
    
    def test_optional_fields_validation(self):
        """Test validation of optional fields."""
        blurbs_with_optional = {
            "intro": [
                {
                    "id": "standard",
                    "tags": ["all"],
                    "text": "Valid text",
                    "priority": "high",
                    "job_types": ["general", "ai_ml"],
                    "experience_level": "senior",
                    "company_stage": "startup"
                }
            ],
            "paragraph2": self.valid_blurbs["paragraph2"],
            "examples": self.valid_blurbs["examples"]
        }
        
        is_valid, errors = self.validator.validate_blurbs(blurbs_with_optional)
        assert is_valid
        assert len(errors) == 0
    
    def test_empty_optional_sections(self):
        """Test that empty optional sections are allowed."""
        blurbs_with_empty_optional = {
            "intro": self.valid_blurbs["intro"],
            "paragraph2": self.valid_blurbs["paragraph2"],
            "examples": self.valid_blurbs["examples"],
            "star_stories": [],  # Empty optional section
            "leadership": [],     # Empty optional section
            "closing": []         # Empty optional section
        }
        
        is_valid, errors = self.validator.validate_blurbs(blurbs_with_empty_optional)
        assert is_valid
        assert len(errors) == 0
    
    def test_metadata_section(self):
        """Test that metadata section is allowed."""
        blurbs_with_metadata = {
            "intro": self.valid_blurbs["intro"],
            "paragraph2": self.valid_blurbs["paragraph2"],
            "examples": self.valid_blurbs["examples"],
            "metadata": {
                "last_updated": "2025-01-01",
                "total_examples": 5
            }
        }
        
        is_valid, errors = self.validator.validate_blurbs(blurbs_with_metadata)
        assert is_valid
        assert len(errors) == 0


class TestSchemaValidatorIntegration:
    """Test schema validator integration with file system."""
    
    def test_validate_yaml_file_valid(self, tmp_path):
        """Test validation of a valid YAML file."""
        # Create a temporary valid blurbs file
        blurbs_file = tmp_path / "blurbs.yaml"
        valid_blurbs = {
            "intro": [
                {
                    "id": "standard",
                    "tags": ["all"],
                    "text": "Valid introduction blurb."
                }
            ],
            "paragraph2": [
                {
                    "id": "cleantech",
                    "tags": ["cleantech", "energy"],
                    "text": "Valid paragraph blurb."
                }
            ],
            "examples": [
                {
                    "id": "enact",
                    "tags": ["growth", "leadership"],
                    "text": "Valid example blurb."
                }
            ]
        }
        
        with open(blurbs_file, 'w') as f:
            yaml.dump(valid_blurbs, f)
        
        validator = SchemaValidator()
        is_valid, errors = validator.validate_yaml_file(str(blurbs_file), "blurb")
        
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_yaml_file_invalid(self, tmp_path):
        """Test validation of an invalid YAML file."""
        # Create a temporary invalid blurbs file
        blurbs_file = tmp_path / "blurbs.yaml"
        invalid_blurbs = {
            "intro": [
                {
                    "id": "standard",
                    # Missing tags and text
                }
            ]
        }
        
        with open(blurbs_file, 'w') as f:
            yaml.dump(invalid_blurbs, f)
        
        validator = SchemaValidator()
        is_valid, errors = validator.validate_yaml_file(str(blurbs_file), "blurb")
        
        assert not is_valid
        assert len(errors) > 0
    
    def test_validate_yaml_file_not_found(self):
        """Test validation of non-existent file."""
        validator = SchemaValidator()
        is_valid, errors = validator.validate_yaml_file("nonexistent.yaml", "blurb")
        
        assert not is_valid
        assert any("File not found" in error for error in errors)
    
    def test_validate_yaml_file_invalid_yaml(self, tmp_path):
        """Test validation of file with invalid YAML syntax."""
        # Create a file with invalid YAML
        blurbs_file = tmp_path / "blurbs.yaml"
        with open(blurbs_file, 'w') as f:
            f.write("invalid: yaml: content: [\n")  # Malformed YAML
        
        validator = SchemaValidator()
        is_valid, errors = validator.validate_yaml_file(str(blurbs_file), "blurb")
        
        assert not is_valid
        assert any("YAML parsing error" in error for error in errors)


class TestValidationFunctions:
    """Test the validation utility functions."""
    
    @patch('core.schema_validator.Path')
    def test_validate_user_blurbs_user_not_found(self, mock_path):
        """Test validation when user blurbs file doesn't exist."""
        mock_path.return_value.exists.return_value = False
        
        result = validate_user_blurbs("nonexistent_user")
        
        assert not result["is_valid"]
        assert result["error_count"] == 1
        assert "not found" in result["errors"][0]
    
    @patch('core.schema_validator.SchemaValidator')
    def test_validate_user_blurbs_valid(self, mock_validator_class):
        """Test validation of valid user blurbs."""
        mock_validator = mock_validator_class.return_value
        mock_validator.get_validation_summary.return_value = {
            "file_path": "users/test/blurbs.yaml",
            "schema_name": "blurb",
            "is_valid": True,
            "error_count": 0,
            "errors": [],
            "timestamp": "1234567890"
        }
        
        with patch('core.schema_validator.Path') as mock_path:
            mock_path.return_value.exists.return_value = True
            
            result = validate_user_blurbs("test")
            
            assert result["is_valid"]
            assert result["error_count"] == 0
            assert len(result["errors"]) == 0
    
    @patch('core.schema_validator.Path')
    def test_validate_all_user_blurbs_no_users_dir(self, mock_path):
        """Test validation when users directory doesn't exist."""
        mock_path.return_value.exists.return_value = False
        
        result = validate_all_user_blurbs()
        
        assert "error" in result
        assert "not found" in result["error"]
    
    @patch('core.schema_validator.Path')
    def test_validate_all_user_blurbs_with_users(self, mock_path):
        """Test validation of all users."""
        # Mock the users directory structure
        mock_users_dir = mock_path.return_value
        mock_users_dir.exists.return_value = True
        mock_users_dir.iterdir.return_value = [
            mock_path.return_value,  # user1
            mock_path.return_value,  # user2
        ]
        
        # Mock individual user directories
        mock_user_dir = mock_path.return_value
        mock_user_dir.is_dir.return_value = True
        mock_user_dir.name = "test_user"
        
        # Mock blurbs file
        mock_blurbs_file = mock_path.return_value
        mock_blurbs_file.exists.return_value = True
        mock_blurbs_file.__truediv__.return_value = mock_blurbs_file
        
        with patch('core.schema_validator.SchemaValidator') as mock_validator_class:
            mock_validator = mock_validator_class.return_value
            mock_validator.get_validation_summary.return_value = {
                "file_path": "users/test_user/blurbs.yaml",
                "schema_name": "blurb",
                "is_valid": True,
                "error_count": 0,
                "errors": [],
                "timestamp": "1234567890"
            }
            
            result = validate_all_user_blurbs()
            
            assert "test_user" in result
            assert result["test_user"]["is_valid"]


if __name__ == "__main__":
    pytest.main([__file__]) 