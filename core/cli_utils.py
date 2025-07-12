#!/usr/bin/env python3
"""
CLI Utilities for Cover Letter Agent
===================================

Provides enhanced user experience features for the command-line interface.
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

try:
    from colorama import Fore, Back, Style, init

    COLORAMA_AVAILABLE = True
    init(autoreset=True)
except ImportError:
    COLORAMA_AVAILABLE = False

    # Fallback color constants
    class Fore:
        GREEN = ""
        RED = ""
        YELLOW = ""
        BLUE = ""
        CYAN = ""
        MAGENTA = ""
        WHITE = ""
        RESET = ""

    class Back:
        GREEN = ""
        RED = ""
        YELLOW = ""
        BLUE = ""
        RESET = ""

    class Style:
        BRIGHT = ""
        DIM = ""
        NORMAL = ""
        RESET = ""


try:
    import tqdm

    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False


class CLIError(Exception):
    """Custom exception for CLI-related errors."""

    pass


class ProgressIndicator:
    """Progress indicator for long-running operations."""

    def __init__(self, description: str, total: int = 0):
        self.description = description
        self.total = total
        self.current = 0

    def __enter__(self):
        if TQDM_AVAILABLE:
            self.pbar = tqdm.tqdm(desc=self.description, total=self.total, unit="steps", colour="green")
        else:
            print(f"{Fore.CYAN}⏳ {self.description}...{Style.RESET}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if TQDM_AVAILABLE:
            self.pbar.close()
        else:
            print(f"{Fore.GREEN}✅ {self.description} completed{Style.RESET}")

    def update(self, increment: int = 1, description: Optional[str] = None):
        """Update progress."""
        self.current += increment
        if TQDM_AVAILABLE:
            if description:
                self.pbar.set_description(description)
            self.pbar.update(increment)
        else:
            if description:
                print(f"{Fore.CYAN}⏳ {description}...{Style.RESET}")


def print_header(title: str, subtitle: Optional[str] = None):
    """Print a formatted header."""
    width = 60
    print(f"\n{Fore.CYAN}{'=' * width}{Style.RESET}")
    print(f"{Fore.CYAN}{Style.BRIGHT}{title.center(width)}{Style.RESET}")
    if subtitle:
        print(f"{Fore.CYAN}{subtitle.center(width)}{Style.RESET}")
    print(f"{Fore.CYAN}{'=' * width}{Style.RESET}")


def print_section(title: str):
    """Print a section header."""
    print(f"\n{Fore.BLUE}{Style.BRIGHT}{title}{Style.RESET}")
    print(f"{Fore.BLUE}{'-' * len(title)}{Style.RESET}")


def print_success(message: str):
    """Print a success message."""
    print(f"{Fore.GREEN}✅ {message}{Style.RESET}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Fore.RED}❌ {message}{Style.RESET}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Fore.YELLOW}⚠️  {message}{Style.RESET}")


def print_info(message: str):
    """Print an info message."""
    print(f"{Fore.BLUE}ℹ️  {message}{Style.RESET}")


def print_debug(message: str):
    """Print a debug message."""
    print(f"{Fore.MAGENTA}🔍 {message}{Style.RESET}")


def confirm_action(prompt: str, default: bool = True) -> bool:
    """Interactive confirmation prompt."""
    default_text = "Y/n" if default else "y/N"
    response = input(f"{Fore.YELLOW}❓ {prompt} ({default_text}): {Style.RESET}").strip().lower()

    if not response:
        return default
    return response in ["y", "yes", "true", "1"]


def select_from_list(options: List[str], prompt: str = "Select an option:") -> Optional[int]:
    """Interactive list selection."""
    if not options:
        return None

    print(f"\n{Fore.CYAN}{prompt}{Style.RESET}")
    for i, option in enumerate(options, 1):
        print(f"{Fore.WHITE}{i:2d}. {option}{Style.RESET}")

    while True:
        try:
            choice = input(f"\n{Fore.YELLOW}Enter choice (1-{len(options)}): {Style.RESET}").strip()
            if not choice:
                return None

            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return choice_num - 1
            else:
                print_error(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print_error("Please enter a valid number")


def input_with_validation(prompt: str, validator: callable = None, default: str = "", allow_empty: bool = False) -> str:
    """Get user input with validation."""
    while True:
        if default:
            display_prompt = f"{prompt} [{default}]: "
        else:
            display_prompt = f"{prompt}: "

        value = input(f"{Fore.CYAN}{display_prompt}{Style.RESET}").strip()

        if not value and default:
            value = default

        if not value and not allow_empty:
            print_error("This field cannot be empty")
            continue

        if validator:
            try:
                validator(value)
                return value
            except ValueError as e:
                print_error(str(e))
                continue

        return value


def print_table(headers: List[str], rows: List[List[str]], title: Optional[str] = None):
    """Print a formatted table."""
    if not rows:
        return

    # Calculate column widths
    col_widths = []
    for i in range(len(headers)):
        max_width = len(headers[i])
        for row in rows:
            if i < len(row):
                max_width = max(max_width, len(row[i]))
        col_widths.append(max_width)

    # Print title
    if title:
        print_section(title)

    # Print header
    header_line = " | ".join(f"{headers[i]:<{col_widths[i]}}" for i in range(len(headers)))
    print(f"{Fore.CYAN}{Style.BRIGHT}{header_line}{Style.RESET}")
    print(f"{Fore.CYAN}{'-' * len(header_line)}{Style.RESET}")

    # Print rows
    for row in rows:
        row_line = " | ".join(
            f"{row[i]:<{col_widths[i]}}" if i < len(row) else " " * col_widths[i] for i in range(len(headers))
        )
        print(row_line)


def print_key_value_pairs(data: Dict[str, Any], title: Optional[str] = None):
    """Print key-value pairs in a formatted way."""
    if not data:
        return

    if title:
        print_section(title)

    max_key_length = max(len(str(k)) for k in data.keys())

    for key, value in data.items():
        key_str = f"{key}:".ljust(max_key_length + 1)
        print(f"{Fore.CYAN}{key_str}{Style.RESET} {value}")


def print_status_indicator(status: str, message: str):
    """Print a status indicator with message."""
    status_indicators = {
        "success": f"{Fore.GREEN}✅",
        "error": f"{Fore.RED}❌",
        "warning": f"{Fore.YELLOW}⚠️",
        "info": f"{Fore.BLUE}ℹ️",
        "loading": f"{Fore.CYAN}⏳",
        "done": f"{Fore.GREEN}✅",
    }

    indicator = status_indicators.get(status, "•")
    print(f"{indicator} {message}{Style.RESET}")


def format_file_size(size_bytes: int) -> str:
    """Format file size in human-readable format."""
    if size_bytes == 0:
        return "0B"

    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1

    return f"{size_bytes:.1f}{size_names[i]}"


def print_file_info(file_path: Path):
    """Print formatted file information."""
    if not file_path.exists():
        print_error(f"File not found: {file_path}")
        return

    stat = file_path.stat()
    size = format_file_size(stat.st_size)
    modified = stat.st_mtime

    print(f"{Fore.CYAN}📄 {file_path.name}{Style.RESET}")
    print(f"   Size: {size}")
    print(f"   Modified: {modified}")


def create_spinner(description: str):
    """Create a simple spinner for loading operations."""
    import time
    import threading

    class Spinner:
        def __init__(self, description: str):
            self.description = description
            self.spinning = False
            self.spinner_thread = None

        def __enter__(self):
            self.spinning = True
            self.spinner_thread = threading.Thread(target=self._spin)
            self.spinner_thread.start()
            return self

        def __exit__(self, exc_type, exc_val, exc_tb):
            self.spinning = False
            if self.spinner_thread:
                self.spinner_thread.join()
            print(f"\r{Fore.GREEN}✅ {self.description} completed{Style.RESET}")

        def _spin(self):
            spinner_chars = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
            i = 0
            while self.spinning:
                print(
                    f"\r{Fore.CYAN}{spinner_chars[i % len(spinner_chars)]} {self.description}...{Style.RESET}",
                    end="",
                    flush=True,
                )
                time.sleep(0.1)
                i += 1

    return Spinner(description)


def print_help_text():
    """Print help text for the CLI."""
    help_text = f"""
{Fore.CYAN}Cover Letter Agent CLI Help{Style.RESET}

{Fore.YELLOW}Basic Usage:{Style.RESET}
  python scripts/run_cover_letter_agent.py --user <user_id> -i <job_file>
  python scripts/run_cover_letter_agent.py --user <user_id> -t "Job description text"

{Fore.YELLOW}User Management:{Style.RESET}
  python init_user.py <user_id>          # Create new user
  python init_user.py --list             # List existing users

{Fore.YELLOW}Advanced Options:{Style.RESET}
  --debug                                # Show detailed scoring information
  --explain                              # Show reasoning for decisions
  --interactive                          # Step-by-step confirmation
  --track-enhance                        # Log enhancement suggestions
  --log                                  # View enhancement log
  --log-status <status>                  # Filter log by status

{Fore.YELLOW}Output Options:{Style.RESET}
  -o <file>                              # Save cover letter to file
  --verbose                              # Verbose output

{Fore.YELLOW}Examples:{Style.RESET}
  # Process job description file
  python scripts/run_cover_letter_agent.py --user john -i job.txt

  # Process text directly with debug info
  python scripts/run_cover_letter_agent.py --user john -t "Senior PM at TechCorp" --debug

  # Interactive mode with file output
  python scripts/run_cover_letter_agent.py --user john -i job.txt --interactive -o cover.txt

{Fore.YELLOW}For more help:{Style.RESET}
  python scripts/run_cover_letter_agent.py --help
  python init_user.py --help
"""
    print(help_text)


def validate_file_path(file_path: str, must_exist: bool = True) -> Path:
    """Validate and return a file path."""
    path = Path(file_path)

    if must_exist and not path.exists():
        raise CLIError(f"File not found: {file_path}")

    return path


def validate_user_id(user_id: str) -> str:
    """Validate user ID format."""
    if not user_id or not user_id.strip():
        raise CLIError("User ID cannot be empty")

    user_id = user_id.strip().lower()

    # Check for valid characters
    if not user_id.replace("-", "").replace("_", "").isalnum():
        raise CLIError("User ID can only contain letters, numbers, hyphens, and underscores")

    return user_id


def check_dependencies() -> Dict[str, bool]:
    """Check if optional dependencies are available."""
    dependencies = {
        "colorama": COLORAMA_AVAILABLE,
        "tqdm": TQDM_AVAILABLE,
    }

    missing = [name for name, available in dependencies.items() if not available]
    if missing:
        print_warning(f"Optional dependencies missing: {', '.join(missing)}")
        print_info("Install with: pip install colorama tqdm")

    return dependencies
