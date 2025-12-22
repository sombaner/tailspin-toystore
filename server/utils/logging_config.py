import logging
import json
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from flask import Flask, request, g
import time

class StructuredJSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    Formats log records as JSON with required fields per Constitution Principle V.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record as a JSON string.
        
        Args:
            record: The log record to format
            
        Returns:
            JSON formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
            "level": record.levelname,
            "message": record.getMessage(),
            "service": "tailspin-toystore-api",
            "environment": getattr(record, 'environment', 'development')
        }
        
        # Add correlation ID if available
        correlation_id = getattr(record, 'correlation_id', None)
        if correlation_id:
            log_data["correlation_id"] = correlation_id
            
        # Add any extra fields directly to log_data
        # Skip standard record attributes and our custom ones
        standard_attrs = {
            'name', 'msg', 'args', 'created', 'filename', 'funcName', 'levelname', 
            'levelno', 'lineno', 'module', 'msecs', 'message', 'pathname', 'process', 
            'processName', 'relativeCreated', 'thread', 'threadName', 'exc_info', 
            'exc_text', 'stack_info', 'correlation_id', 'environment', 'extra_fields',
            'taskName'  # Filter out asyncio task name
        }
        
        for key, value in record.__dict__.items():
            if key not in standard_attrs and not key.startswith('_'):
                log_data[key] = value
            
        # Also support extra_fields for backward compatibility
        if hasattr(record, 'extra_fields'):
            log_data.update(record.extra_fields)
            
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_data)


def setup_logging(app: Flask) -> None:
    """
    Configure structured logging for the Flask application.
    Sets up JSON formatted logging with appropriate log levels.
    
    Args:
        app: The Flask application instance
    """
    # Create JSON formatter
    json_formatter = StructuredJSONFormatter()
    
    # Configure root logger
    root_logger = logging.getLogger()
    
    # Set log level based on environment (DEBUG for dev, INFO for prod)
    if app.debug:
        root_logger.setLevel(logging.DEBUG)
    else:
        root_logger.setLevel(logging.INFO)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(json_formatter)
    
    # Clear existing handlers and add our JSON handler
    root_logger.handlers.clear()
    root_logger.addHandler(console_handler)
    
    # Also configure Flask's logger
    app.logger.handlers.clear()
    app.logger.addHandler(console_handler)
    app.logger.setLevel(root_logger.level)
    
    app.logger.info("Structured logging initialized")


def add_request_logging_middleware(app: Flask) -> None:
    """
    Add middleware to log HTTP requests and responses.
    Generates correlation IDs for tracking requests across services.
    
    Args:
        app: The Flask application instance
    """
    
    @app.before_request
    def before_request() -> None:
        """Generate correlation ID and start request timer"""
        # Generate or extract correlation ID
        correlation_id = request.headers.get('X-Correlation-ID', str(uuid.uuid4()))
        g.correlation_id = correlation_id
        g.start_time = time.time()
        
        # Log incoming request
        log_record = logging.LogRecord(
            name=app.logger.name,
            level=logging.INFO,
            pathname="",
            lineno=0,
            msg=f"Incoming request: {request.method} {request.path}",
            args=(),
            exc_info=None
        )
        log_record.correlation_id = correlation_id
        log_record.method = request.method
        log_record.path = request.path
        log_record.remote_addr = request.remote_addr
        log_record.user_agent = request.headers.get('User-Agent', '')
        log_record.environment = 'production' if not app.debug else 'development'
        
        app.logger.handle(log_record)
    
    @app.after_request
    def after_request(response):
        """Log response and calculate request duration"""
        if hasattr(g, 'correlation_id'):
            # Calculate request duration
            duration_ms = (time.time() - g.start_time) * 1000 if hasattr(g, 'start_time') else 0
            
            # Add correlation ID to response headers
            response.headers['X-Correlation-ID'] = g.correlation_id
            
            # Log response
            log_record = logging.LogRecord(
                name=app.logger.name,
                level=logging.INFO,
                pathname="",
                lineno=0,
                msg=f"Request completed: {request.method} {request.path} - {response.status_code}",
                args=(),
                exc_info=None
            )
            log_record.correlation_id = g.correlation_id
            log_record.method = request.method
            log_record.path = request.path
            log_record.status_code = response.status_code
            log_record.duration_ms = round(duration_ms, 2)
            log_record.environment = 'production' if not app.debug else 'development'
            
            app.logger.handle(log_record)
        
        return response


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name.
    
    Args:
        name: The logger name (typically __name__)
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
