"""
Schema validation module for cover letter agent.

Provides comprehensive validation for blurbs, config files, and other YAML/JSON data
using JSON Schema validation with detailed error reporting.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from jsonschema import validate, ValidationError, SchemaError
import logging

logger = logging.getLogger(__name__)


class SchemaValidator:
    """Comprehensive schema validation for cover letter agent data."""
    
    def __init__(self, schema_dir: str = "config"):
        """Initialize validator with schema directory."""
        self.schema_dir = Path(schema_dir)
        self.schemas = {}
        self._load_schemas()
    
    def _load_schemas(self) -> None:
        """Load all JSON schemas from the schema directory."""
        schema_files = {
            "blurb": "blurb_schema.json",
            # Add more schemas as needed
            # "config": "config_schema.json",
            # "logic": "logic_schema.json",
        }
        
        for schema_name, filename in schema_files.items():
            schema_path = self.schema_dir / filename
            if schema_path.exists():
                try:
                    with open(schema_path, 'r') as f:
                        self.schemas[schema_name] = json.load(f)
                    logger.info(f"Loaded schema: {schema_name}")
                except (json.JSONDecodeError, FileNotFoundError) as e:
                    logger.error(f"Failed to load schema {schema_name}: {e}")
            else:
                logger.warning(f"Schema file not found: {schema_path}")
    
    def validate_blurbs(self, blurbs_data: Dict[str, Any], file_path: str = "") -> Tuple[bool, List[str]]:
        """
        Validate blurbs against the blurb schema.
        
        Args:
            blurbs_data: The blurbs data to validate
            file_path: Path to the blurbs file (for error reporting)
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if "blurb" not in self.schemas:
            return False, ["Blurb schema not found"]
        
        errors = []
        
        try:
            # Validate against schema
            validate(instance=blurbs_data, schema=self.schemas["blurb"])
            
            # Additional custom validations
            custom_errors = self._validate_blurbs_custom(blurbs_data, file_path)
            errors.extend(custom_errors)
            
            return len(errors) == 0, errors
            
        except ValidationError as e:
            errors.append(f"Schema validation error: {e.message}")
            if e.path:
                errors.append(f"Path: {' -> '.join(str(p) for p in e.path)}")
            return False, errors
        except SchemaError as e:
            errors.append(f"Schema error: {e.message}")
            return False, errors
        except Exception as e:
            errors.append(f"Unexpected validation error: {e}")
            return False, errors
    
    def _validate_blurbs_custom(self, blurbs_data: Dict[str, Any], file_path: str) -> List[str]:
        """Perform custom validations beyond JSON schema."""
        errors = []
        
        # Check for required sections
        required_sections = ["intro", "paragraph2", "examples"]
        for section in required_sections:
            if section not in blurbs_data:
                errors.append(f"Missing required section: {section}")
            elif not blurbs_data[section]:
                # Allow empty sections for optional content like star_stories
                if section not in ["star_stories", "leadership", "closing"]:
                    errors.append(f"Section '{section}' is empty")
        
        # Check for duplicate blurb IDs within sections
        for section_name, section_blurbs in blurbs_data.items():
            if not isinstance(section_blurbs, list):
                continue
                
            blurb_ids = []
            for i, blurb in enumerate(section_blurbs):
                if not isinstance(blurb, dict):
                    continue
                    
                blurb_id = blurb.get("id")
                if blurb_id:
                    if blurb_id in blurb_ids:
                        errors.append(f"Duplicate blurb ID '{blurb_id}' in section '{section_name}'")
                    else:
                        blurb_ids.append(blurb_id)
                
                # Validate individual blurb structure
                blurb_errors = self._validate_single_blurb(blurb, section_name, i)
                errors.extend(blurb_errors)
        
        return errors
    
    def _validate_single_blurb(self, blurb: Dict[str, Any], section_name: str, index: int) -> List[str]:
        """Validate a single blurb."""
        errors = []
        
        if not isinstance(blurb, dict):
            errors.append(f"Blurb at index {index} in section '{section_name}' is not a dictionary")
            return errors
        
        # Check required fields
        required_fields = ["id", "tags", "text"]
        for field in required_fields:
            if field not in blurb:
                errors.append(f"Blurb at index {index} in section '{section_name}' missing required field: {field}")
        
        # Validate ID format
        blurb_id = blurb.get("id")
        if blurb_id and not isinstance(blurb_id, str):
            errors.append(f"Blurb ID at index {index} in section '{section_name}' must be a string")
        elif blurb_id and not blurb_id.replace("_", "").isalnum():
            errors.append(f"Blurb ID '{blurb_id}' at index {index} in section '{section_name}' contains invalid characters")
        
        # Validate tags
        tags = blurb.get("tags")
        if tags and not isinstance(tags, list):
            errors.append(f"Tags at index {index} in section '{section_name}' must be a list")
        elif tags:
            for i, tag in enumerate(tags):
                if not isinstance(tag, str):
                    errors.append(f"Tag {i} at index {index} in section '{section_name}' must be a string")
                elif not tag.replace("_", "").isalnum():
                    errors.append(f"Tag '{tag}' at index {index} in section '{section_name}' contains invalid characters")
        
        # Validate text
        text = blurb.get("text")
        if text and not isinstance(text, str):
            errors.append(f"Text at index {index} in section '{section_name}' must be a string")
        elif text and len(text.strip()) < 10:
            errors.append(f"Text at index {index} in section '{section_name}' is too short (minimum 10 characters)")
        elif text and len(text) > 2000:
            errors.append(f"Text at index {index} in section '{section_name}' is too long (maximum 2000 characters)")
        
        return errors
    
    def validate_yaml_file(self, file_path: str, schema_name: str) -> Tuple[bool, List[str]]:
        """
        Validate a YAML file against a specific schema.
        
        Args:
            file_path: Path to the YAML file
            schema_name: Name of the schema to use
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            
            # Handle empty files
            if data is None:
                return False, ["File is empty or contains no valid YAML"]
            
            if schema_name == "blurb":
                return self.validate_blurbs(data, file_path)
            else:
                return False, [f"Unknown schema: {schema_name}"]
                
        except yaml.YAMLError as e:
            return False, [f"YAML parsing error: {e}"]
        except FileNotFoundError:
            return False, [f"File not found: {file_path}"]
        except Exception as e:
            return False, [f"Unexpected error: {e}"]
    
    def get_validation_summary(self, file_path: str, schema_name: str) -> Dict[str, Any]:
        """
        Get a detailed validation summary for a file.
        
        Args:
            file_path: Path to the file to validate
            schema_name: Name of the schema to use
            
        Returns:
            Dictionary with validation results and details
        """
        is_valid, errors = self.validate_yaml_file(file_path, schema_name)
        
        summary = {
            "file_path": file_path,
            "schema_name": schema_name,
            "is_valid": is_valid,
            "error_count": len(errors),
            "errors": errors,
            "timestamp": str(Path(file_path).stat().st_mtime) if Path(file_path).exists() else None
        }
        
        return summary


def validate_user_blurbs(user_id: str) -> Dict[str, Any]:
    """
    Validate blurbs for a specific user.
    
    Args:
        user_id: The user ID to validate
        
    Returns:
        Validation results dictionary
    """
    validator = SchemaValidator()
    blurbs_path = f"users/{user_id}/blurbs.yaml"
    
    if not Path(blurbs_path).exists():
        return {
            "user_id": user_id,
            "is_valid": False,
            "error_count": 1,
            "errors": [f"Blurbs file not found: {blurbs_path}"],
            "file_path": blurbs_path
        }
    
    return validator.get_validation_summary(blurbs_path, "blurb")


def validate_all_user_blurbs() -> Dict[str, Any]:
    """
    Validate blurbs for all users.
    
    Returns:
        Dictionary with validation results for all users
    """
    validator = SchemaValidator()
    users_dir = Path("users")
    results = {}
    
    if not users_dir.exists():
        return {"error": "Users directory not found"}
    
    for user_dir in users_dir.iterdir():
        if user_dir.is_dir():
            blurbs_path = user_dir / "blurbs.yaml"
            if blurbs_path.exists():
                results[user_dir.name] = validator.get_validation_summary(str(blurbs_path), "blurb")
    
    return results


if __name__ == "__main__":
    # Test validation
    import sys
    
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        results = validate_user_blurbs(user_id)
        print(json.dumps(results, indent=2))
    else:
        results = validate_all_user_blurbs()
        print(json.dumps(results, indent=2)) 