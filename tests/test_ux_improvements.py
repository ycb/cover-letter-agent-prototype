#!/usr/bin/env python3
"""
Test UX Improvements
===================

Tests for the enhanced user experience features.
"""

import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Add the project root to the path
sys.path.append(str(Path(__file__).parent.parent))

from core.cli_utils import (
    CLIError,
    ProgressIndicator,
    check_dependencies,
    confirm_action,
    create_spinner,
    format_file_size,
    input_with_validation,
    print_debug,
    print_error,
    print_header,
    print_info,
    print_key_value_pairs,
    print_section,
    print_status_indicator,
    print_success,
    print_table,
    print_warning,
    select_from_list,
    validate_file_path,
    validate_user_id,
)


class TestCLIUtils:
    """Test CLI utility functions."""
    
    def test_validate_user_id_valid(self):
        """Test valid user ID validation."""
        valid_ids = ["john", "john_doe", "john-doe", "user123", "user_123"]
        for user_id in valid_ids:
            result = validate_user_id(user_id)
            assert result == user_id.lower()
    
    def test_validate_user_id_invalid(self):
        """Test invalid user ID validation."""
        invalid_ids = ["", "john@doe", "john.doe", "user 123", "user@123"]
        for user_id in invalid_ids:
            with pytest.raises(CLIError):
                validate_user_id(user_id)
    
    def test_validate_file_path_exists(self):
        """Test file path validation with existing file."""
        with tempfile.NamedTemporaryFile() as f:
            result = validate_file_path(f.name)
            assert result == Path(f.name)
    
    def test_validate_file_path_not_exists(self):
        """Test file path validation with non-existent file."""
        with pytest.raises(CLIError):
            validate_file_path("nonexistent_file.txt")
    
    def test_validate_file_path_not_exists_allowed(self):
        """Test file path validation with non-existent file allowed."""
        result = validate_file_path("nonexistent_file.txt", must_exist=False)
        assert result == Path("nonexistent_file.txt")
    
    def test_format_file_size(self):
        """Test file size formatting."""
        assert format_file_size(0) == "0B"
        assert format_file_size(1024) == "1.0KB"
        assert format_file_size(1024 * 1024) == "1.0MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.0GB"
    
    def test_check_dependencies(self):
        """Test dependency checking."""
        dependencies = check_dependencies()
        assert isinstance(dependencies, dict)
        assert "colorama" in dependencies
        assert "tqdm" in dependencies
    
    @patch('builtins.input', return_value='y')
    def test_confirm_action_yes(self, mock_input):
        """Test confirmation with yes."""
        result = confirm_action("Test prompt")
        assert result is True
    
    @patch('builtins.input', return_value='n')
    def test_confirm_action_no(self, mock_input):
        """Test confirmation with no."""
        result = confirm_action("Test prompt")
        assert result is False
    
    @patch('builtins.input', return_value='')
    def test_confirm_action_default(self, mock_input):
        """Test confirmation with default."""
        result = confirm_action("Test prompt", default=True)
        assert result is True
    
    @patch('builtins.input', side_effect=['5', '2'])
    def test_select_from_list_valid(self, mock_input):
        """Test list selection with valid input."""
        options = ["Option 1", "Option 2", "Option 3"]
        result = select_from_list(options, "Select an option:")
        assert result == 1  # Index 1 corresponds to "Option 2"
    
    @patch('builtins.input', return_value='')
    def test_select_from_list_empty(self, mock_input):
        """Test list selection with empty input."""
        options = ["Option 1", "Option 2", "Option 3"]
        result = select_from_list(options, "Select an option:")
        assert result is None
    
    @patch('builtins.input', side_effect=['invalid', '2'])
    def test_select_from_list_invalid_then_valid(self, mock_input):
        """Test list selection with invalid then valid input."""
        options = ["Option 1", "Option 2", "Option 3"]
        result = select_from_list(options, "Select an option:")
        assert result == 1
    
    @patch('builtins.input', side_effect=['test_value'])
    def test_input_with_validation_success(self, mock_input):
        """Test input validation with success."""
        result = input_with_validation("Enter value:")
        assert result == "test_value"
    
    @patch('builtins.input', side_effect=['', 'test_value'])
    def test_input_with_validation_empty_then_valid(self, mock_input):
        """Test input validation with empty then valid input."""
        result = input_with_validation("Enter value:", allow_empty=False)
        assert result == "test_value"
    
    @patch('builtins.input', side_effect=['test_value'])
    def test_input_with_validation_with_default(self, mock_input):
        """Test input validation with default value."""
        result = input_with_validation("Enter value:", default="default_value")
        assert result == "test_value"
    
    @patch('builtins.input', side_effect=['', 'test_value'])
    def test_input_with_validation_empty_with_default(self, mock_input):
        """Test input validation with empty input and default."""
        result = input_with_validation("Enter value:", default="default_value")
        assert result == "default_value"
    
    def test_print_table(self, capsys):
        """Test table printing."""
        headers = ["Name", "Age", "City"]
        rows = [
            ["John", "30", "New York"],
            ["Jane", "25", "San Francisco"],
            ["Bob", "35", "Chicago"]
        ]
        
        print_table(headers, rows, "Test Table")
        captured = capsys.readouterr()
        
        assert "Test Table" in captured.out
        assert "Name" in captured.out
        assert "John" in captured.out
        assert "Jane" in captured.out
        assert "Bob" in captured.out
    
    def test_print_key_value_pairs(self, capsys):
        """Test key-value pair printing."""
        data = {
            "Name": "John Doe",
            "Age": "30",
            "City": "New York"
        }
        
        print_key_value_pairs(data, "Test Data")
        captured = capsys.readouterr()
        
        assert "Test Data" in captured.out
        assert "Name:" in captured.out
        assert "John Doe" in captured.out
    
    def test_progress_indicator(self, capsys):
        """Test progress indicator."""
        with ProgressIndicator("Test Progress", 3) as progress:
            progress.update(1, "Step 1")
            progress.update(1, "Step 2")
            progress.update(1, "Step 3")
        
        captured = capsys.readouterr()
        # tqdm outputs to stderr, so check both stdout and stderr
        output = captured.out + captured.err
        assert "Test Progress" in output
        # When tqdm is available, it doesn't print "completed" message
        # Just check that the progress indicator worked
        assert "100%" in output or "completed" in output
    
    def test_create_spinner(self, capsys):
        """Test spinner creation."""
        with create_spinner("Test Spinner"):
            import time
            time.sleep(0.1)  # Brief sleep to see spinner
        
        captured = capsys.readouterr()
        assert "Test Spinner" in captured.out
        assert "completed" in captured.out


class TestEnhancedCLI:
    """Test enhanced CLI functionality."""
    
    def test_cli_imports(self):
        """Test that CLI modules can be imported."""
        try:
            from scripts.cli import CoverLetterCLI
            assert CoverLetterCLI is not None
        except ImportError as e:
            pytest.skip(f"CLI module not available: {e}")
    
    def test_cli_initialization(self):
        """Test CLI initialization."""
        try:
            from scripts.cli import CoverLetterCLI
            cli = CoverLetterCLI()
            assert cli.agent is None
            assert cli.user_id is None
        except ImportError:
            pytest.skip("CLI module not available")


class TestUserManagement:
    """Test user management features."""
    
    def test_user_creation_validation(self):
        """Test user creation with validation."""
        # Test valid user ID
        valid_id = "test_user_123"
        result = validate_user_id(valid_id)
        assert result == valid_id.lower()
        
        # Test invalid user ID
        with pytest.raises(CLIError):
            validate_user_id("invalid@user")
    
    def test_user_directory_structure(self):
        """Test user directory structure creation."""
        # This would test the actual user creation process
        # For now, just test the validation
        assert validate_user_id("test_user") == "test_user"


class TestErrorHandling:
    """Test error handling in CLI."""
    
    def test_cli_error_exception(self):
        """Test CLIError exception."""
        error = CLIError("Test error message")
        assert str(error) == "Test error message"
    
    def test_file_validation_error(self):
        """Test file validation error handling."""
        with pytest.raises(CLIError) as exc_info:
            validate_file_path("nonexistent_file.txt")
        assert "File not found" in str(exc_info.value)
    
    def test_user_validation_error(self):
        """Test user validation error handling."""
        with pytest.raises(CLIError) as exc_info:
            validate_user_id("")
        assert "cannot be empty" in str(exc_info.value)


class TestOutputFormatting:
    """Test output formatting functions."""
    
    def test_print_functions(self, capsys):
        """Test all print functions."""
        # Test success message
        print_success("Success message")
        captured = capsys.readouterr()
        assert "Success message" in captured.out
        
        # Test error message
        print_error("Error message")
        captured = capsys.readouterr()
        assert "Error message" in captured.out
        
        # Test warning message
        print_warning("Warning message")
        captured = capsys.readouterr()
        assert "Warning message" in captured.out
        
        # Test info message
        print_info("Info message")
        captured = capsys.readouterr()
        assert "Info message" in captured.out
        
        # Test debug message
        print_debug("Debug message")
        captured = capsys.readouterr()
        assert "Debug message" in captured.out
    
    def test_print_header(self, capsys):
        """Test header printing."""
        print_header("Test Header", "Test Subtitle")
        captured = capsys.readouterr()
        assert "Test Header" in captured.out
        assert "Test Subtitle" in captured.out
    
    def test_print_section(self, capsys):
        """Test section printing."""
        print_section("Test Section")
        captured = capsys.readouterr()
        assert "Test Section" in captured.out
    
    def test_print_status_indicator(self, capsys):
        """Test status indicator printing."""
        print_status_indicator("success", "Operation completed")
        captured = capsys.readouterr()
        assert "Operation completed" in captured.out


class TestInteractiveFeatures:
    """Test interactive CLI features."""
    
    @patch('builtins.input', return_value='test_value')
    def test_input_validation_success(self, mock_input):
        """Test successful input validation."""
        result = input_with_validation("Enter value:")
        assert result == "test_value"
    
    @patch('builtins.input', side_effect=['', 'valid_value'])
    def test_input_validation_retry(self, mock_input):
        """Test input validation with retry."""
        result = input_with_validation("Enter value:", allow_empty=False)
        assert result == "valid_value"
    
    def test_input_validation_with_validator(self):
        """Test input validation with custom validator."""
        def validator(value):
            if len(value) < 3:
                raise ValueError("Value too short")
            return value
        
        with patch('builtins.input', side_effect=['a', 'valid']):
            result = input_with_validation("Enter value:", validator=validator)
            assert result == "valid"


if __name__ == "__main__":
    pytest.main([__file__]) 