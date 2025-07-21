#!/usr/bin/env python3
"""
Error Handler for Cover Letter Agent
===================================

Provides comprehensive error handling and logging for the cover letter agent.
"""

import logging
import traceback
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class ErrorInfo:
    """Represents error information for logging and debugging."""
    error_type: str
    error_message: str
    component: str
    timestamp: datetime
    context: Dict[str, Any]
    stack_trace: str


class CoverLetterAgentError(Exception):
    """Base exception for cover letter agent errors."""
    
    def __init__(self, message: str, component: str = "unknown", context: Dict[str, Any] = None):
        super().__init__(message)
        self.component = component
        self.context = context or {}
        self.timestamp = datetime.now()


class ConfigurationError(CoverLetterAgentError):
    """Raised when there are configuration issues."""
    pass


class DataLoadError(CoverLetterAgentError):
    """Raised when data loading fails."""
    pass


class CaseStudySelectionError(CoverLetterAgentError):
    """Raised when case study selection fails."""
    pass


class WorkHistoryError(CoverLetterAgentError):
    """Raised when work history processing fails."""
    pass


class LLMError(CoverLetterAgentError):
    """Raised when LLM operations fail."""
    pass


class ErrorHandler:
    """Handles errors and provides logging and recovery mechanisms."""
    
    def __init__(self):
        """Initialize the error handler."""
        self.error_log: List[ErrorInfo] = []
        self.recovery_strategies: Dict[str, Callable] = {}
        
    def handle_error(self, error: Exception, component: str, context: Dict[str, Any] = None) -> ErrorInfo:
        """Handle an error and log it appropriately."""
        error_info = ErrorInfo(
            error_type=type(error).__name__,
            error_message=str(error),
            component=component,
            timestamp=datetime.now(),
            context=context or {},
            stack_trace=traceback.format_exc()
        )
        
        # Log the error
        logger.error(f"Error in {component}: {error}")
        logger.error(f"Context: {context}")
        logger.debug(f"Stack trace: {error_info.stack_trace}")
        
        # Store error info
        self.error_log.append(error_info)
        
        # Try recovery strategy
        self._try_recovery(error_info)
        
        return error_info
    
    def _try_recovery(self, error_info: ErrorInfo) -> bool:
        """Try to recover from an error using registered strategies."""
        recovery_strategy = self.recovery_strategies.get(error_info.component)
        if recovery_strategy:
            try:
                recovery_strategy(error_info)
                logger.info(f"Recovery successful for {error_info.component}")
                return True
            except Exception as e:
                logger.error(f"Recovery failed for {error_info.component}: {e}")
                return False
        return False
    
    def register_recovery_strategy(self, component: str, strategy: Callable) -> None:
        """Register a recovery strategy for a component."""
        self.recovery_strategies[component] = strategy
        logger.info(f"Registered recovery strategy for {component}")
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of all errors."""
        if not self.error_log:
            return {"total_errors": 0, "errors_by_component": {}}
        
        errors_by_component = {}
        for error in self.error_log:
            component = error.component
            if component not in errors_by_component:
                errors_by_component[component] = []
            errors_by_component[component].append({
                "type": error.error_type,
                "message": error.error_message,
                "timestamp": error.timestamp.isoformat(),
                "context": error.context
            })
        
        return {
            "total_errors": len(self.error_log),
            "errors_by_component": errors_by_component,
            "latest_error": self.error_log[-1].timestamp.isoformat() if self.error_log else None
        }
    
    def clear_error_log(self) -> None:
        """Clear the error log."""
        self.error_log.clear()
        logger.info("Error log cleared")


def safe_execute(func: Callable, component: str, error_handler: ErrorHandler, *args, **kwargs) -> Any:
    """Safely execute a function with error handling."""
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler.handle_error(e, component, {
            "function": func.__name__,
            "args": str(args),
            "kwargs": str(kwargs)
        })
        raise


def retry_on_error(max_retries: int = 3, delay: float = 1.0):
    """Decorator to retry functions on error."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_error = e
                    logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}")
                    if attempt < max_retries - 1:
                        import time
                        time.sleep(delay)
            
            # All retries failed
            logger.error(f"All {max_retries} attempts failed for {func.__name__}")
            raise last_error
        return wrapper
    return decorator


def validate_input(data: Any, expected_type: type, field_name: str) -> None:
    """Validate input data and raise appropriate errors."""
    if not isinstance(data, expected_type):
        raise ValueError(f"Invalid {field_name}: expected {expected_type.__name__}, got {type(data).__name__}")


def test_error_handler():
    """Test the error handling functionality."""
    print("🧪 Testing Error Handler...")
    
    error_handler = ErrorHandler()
    
    # Test basic error handling
    try:
        raise ValueError("Test error")
    except Exception as e:
        error_info = error_handler.handle_error(e, "test_component", {"test": "data"})
        print(f"  Error handled: {error_info.error_type}")
    
    # Test error summary
    summary = error_handler.get_error_summary()
    print(f"  Total errors: {summary['total_errors']}")
    print(f"  Errors by component: {list(summary['errors_by_component'].keys())}")
    
    # Test safe_execute
    def test_function(x):
        if x < 0:
            raise ValueError("Negative number")
        return x * 2
    
    try:
        result = safe_execute(test_function, "test", error_handler, 5)
        print(f"  Safe execute success: {result}")
    except Exception as e:
        print(f"  Safe execute failed as expected: {e}")
    
    # Test input validation
    try:
        validate_input("string", str, "test_field")
        print("  Input validation passed")
    except Exception as e:
        print(f"  Input validation failed: {e}")
    
    print("✅ Error Handler test completed!")


if __name__ == "__main__":
    test_error_handler() 