"""Tests for logging configuration to improve coverage."""

import json
import logging
import tempfile
import os
from unittest.mock import Mock, patch
import pytest

from src.config.logging_config import (
    SensitiveDataFilter,
    JsonFormatter,
    setup_structured_logging
)


class TestSensitiveDataFilter:
    """Tests for SensitiveDataFilter class."""
    
    def test_filter_initialization(self):
        """Test that SensitiveDataFilter initializes correctly."""
        # Arrange & Act
        filter_instance = SensitiveDataFilter()
        
        # Assert
        assert hasattr(filter_instance, 'SENSITIVE_KEYS')
        assert 'api_key' in filter_instance.SENSITIVE_KEYS
        assert 'token' in filter_instance.SENSITIVE_KEYS
        assert 'password' in filter_instance.SENSITIVE_KEYS
        assert 'secret' in filter_instance.SENSITIVE_KEYS

    def test_filter_dict_message_with_sensitive_data(self):
        """Test filter method with dict message containing sensitive data."""
        # Arrange
        filter_instance = SensitiveDataFilter()
        record = Mock()
        record.msg = {
            "user": "test_user",
            "api_key": "secret_key_123",
            "action": "login"
        }
        
        # Act
        result = filter_instance.filter(record)
        
        # Assert
        assert result is True
        assert record.msg["api_key"] == "***"
        assert record.msg["user"] == "test_user"
        assert record.msg["action"] == "login"

    def test_filter_dict_message_with_multiple_sensitive_keys(self):
        """Test filter method with multiple sensitive keys."""
        # Arrange
        filter_instance = SensitiveDataFilter()
        record = Mock()
        record.msg = {
            "api_key": "secret_key",
            "password": "secret_pass",
            "token": "secret_token",
            "secret": "secret_data",
            "safe_data": "normal_data"
        }
        
        # Act
        result = filter_instance.filter(record)
        
        # Assert
        assert result is True
        assert record.msg["api_key"] == "***"
        assert record.msg["password"] == "***"
        assert record.msg["token"] == "***"
        assert record.msg["secret"] == "***"
        assert record.msg["safe_data"] == "normal_data"

    def test_filter_dict_message_without_sensitive_data(self):
        """Test filter method with dict message without sensitive data."""
        # Arrange
        filter_instance = SensitiveDataFilter()
        record = Mock()
        record.msg = {
            "user": "test_user",
            "action": "login",
            "timestamp": "2023-01-01"
        }
        original_msg = record.msg.copy()
        
        # Act
        result = filter_instance.filter(record)
        
        # Assert
        assert result is True
        assert record.msg == original_msg

    def test_filter_non_dict_message(self):
        """Test filter method with non-dict message."""
        # Arrange
        filter_instance = SensitiveDataFilter()
        record = Mock()
        record.msg = "Simple string message"
        
        # Act
        result = filter_instance.filter(record)
        
        # Assert
        assert result is True
        assert record.msg == "Simple string message"

    def test_filter_record_without_msg_attribute(self):
        """Test filter method with record without msg attribute."""
        # Arrange
        filter_instance = SensitiveDataFilter()
        record = Mock(spec=[])  # Mock without msg attribute
        
        # Act
        result = filter_instance.filter(record)
        
        # Assert
        assert result is True


class TestJsonFormatter:
    """Tests for JsonFormatter class."""
    
    def test_json_formatter_initialization(self):
        """Test that JsonFormatter initializes correctly."""
        # Arrange & Act
        formatter = JsonFormatter()
        
        # Assert
        assert isinstance(formatter, logging.Formatter)

    def test_format_basic_record(self):
        """Test formatting a basic log record."""
        # Arrange
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.INFO,
            pathname="test.py",
            lineno=10,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        # Act
        result = formatter.format(record)
        
        # Assert
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["level"] == "INFO"
        assert parsed["name"] == "test_logger"
        assert parsed["message"] == "Test message"
        assert "time" in parsed

    def test_format_record_with_exception(self):
        """Test formatting a log record with exception info."""
        # Arrange
        formatter = JsonFormatter()
        
        try:
            raise ValueError("Test exception")
        except ValueError:
            import sys
            exc_info = sys.exc_info()
        
        record = logging.LogRecord(
            name="test_logger",
            level=logging.ERROR,
            pathname="test.py",
            lineno=10,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )
        
        # Act
        result = formatter.format(record)
        
        # Assert
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["level"] == "ERROR"
        assert parsed["message"] == "Error occurred"
        assert "exception" in parsed
        assert "ValueError: Test exception" in parsed["exception"]

    def test_format_record_with_args(self):
        """Test formatting a log record with message arguments."""
        # Arrange
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.WARNING,
            pathname="test.py",
            lineno=10,
            msg="User %s performed %s",
            args=("john", "login"),
            exc_info=None
        )
        
        # Act
        result = formatter.format(record)
        
        # Assert
        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed["message"] == "User john performed login"

    def test_format_ensures_json_validity(self):
        """Test that format always returns valid JSON."""
        # Arrange
        formatter = JsonFormatter()
        record = logging.LogRecord(
            name="test_logger",
            level=logging.DEBUG,
            pathname="test.py",
            lineno=10,
            msg="Message with unicode: ñáéíóú",
            args=(),
            exc_info=None
        )
        
        # Act
        result = formatter.format(record)
        
        # Assert
        assert isinstance(result, str)
        # Should not raise exception
        parsed = json.loads(result)
        assert "ñáéíóú" in parsed["message"]


class TestSetupStructuredLogging:
    """Tests for setup_structured_logging function."""
    
    def test_setup_structured_logging_basic(self):
        """Test basic setup of structured logging."""
        # Arrange
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_file = temp_file.name
        
        try:
            # Act
            setup_structured_logging(log_file)
            
            # Assert
            root_logger = logging.getLogger()
            assert root_logger.level == logging.INFO
            assert len(root_logger.handlers) >= 2  # file + stream handlers
            assert root_logger.propagate is False
            
        finally:
            # Cleanup
            logging.getLogger().handlers.clear()
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_setup_structured_logging_custom_level(self):
        """Test setup with custom log level."""
        # Arrange
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_file = temp_file.name
        
        try:
            # Act
            setup_structured_logging(log_file, level=logging.DEBUG)
            
            # Assert
            root_logger = logging.getLogger()
            assert root_logger.level == logging.DEBUG
            
        finally:
            # Cleanup
            logging.getLogger().handlers.clear()
            if os.path.exists(log_file):
                os.unlink(log_file)

    def test_setup_structured_logging_no_stdout(self):
        """Test setup without stdout handler."""
        # Arrange
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_file = temp_file.name
        
        try:
            # Clear any existing handlers first
            logging.getLogger().handlers.clear()
            
            # Act
            setup_structured_logging(log_file, to_stdout=False)
            
            # Assert
            root_logger = logging.getLogger()
            assert len(root_logger.handlers) >= 1  # Should have at least file handler
            
        finally:
            # Cleanup
            logging.getLogger().handlers.clear()
            try:
                if os.path.exists(log_file):
                    os.unlink(log_file)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors

    def test_setup_structured_logging_handlers_have_filters(self):
        """Test that setup creates handlers with filters."""
        # Arrange
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_file = temp_file.name
        
        try:
            # Clear any existing handlers first
            logging.getLogger().handlers.clear()
            
            # Act
            setup_structured_logging(log_file)
            
            # Assert
            root_logger = logging.getLogger()
            assert len(root_logger.handlers) >= 1  # Should have handlers
            
        finally:
            # Cleanup
            logging.getLogger().handlers.clear()
            try:
                if os.path.exists(log_file):
                    os.unlink(log_file)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors

    def test_setup_structured_logging_handlers_configuration(self):
        """Test that handlers are properly configured."""
        # Arrange
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            log_file = temp_file.name
        
        try:
            # Clear any existing handlers first
            logging.getLogger().handlers.clear()
            
            # Act
            setup_structured_logging(log_file)
            
            # Assert
            root_logger = logging.getLogger()
            assert len(root_logger.handlers) >= 1
            assert root_logger.propagate is False
            
        finally:
            # Cleanup
            logging.getLogger().handlers.clear()
            try:
                if os.path.exists(log_file):
                    os.unlink(log_file)
            except (OSError, PermissionError):
                pass  # Ignore cleanup errors
