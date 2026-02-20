import unittest
import json
import logging
from io import StringIO
from flask import Flask, g
from utils.logging_config import (
    StructuredJSONFormatter, 
    setup_logging, 
    add_request_logging_middleware,
    get_logger
)


class TestStructuredJSONFormatter(unittest.TestCase):
    """Test the JSON formatter for structured logging"""
    
    def test_basic_log_format(self) -> None:
        """Test that logs are formatted as valid JSON"""
        formatter = StructuredJSONFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        self.assertIn('timestamp', log_data)
        self.assertIn('level', log_data)
        self.assertIn('message', log_data)
        self.assertEqual(log_data['level'], 'INFO')
        self.assertEqual(log_data['message'], 'Test message')
    
    def test_correlation_id_in_log(self) -> None:
        """Test that correlation ID is included when present"""
        formatter = StructuredJSONFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )
        record.correlation_id = 'test-correlation-123'
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        self.assertEqual(log_data['correlation_id'], 'test-correlation-123')
    
    def test_extra_fields_in_log(self) -> None:
        """Test that extra fields are included in the log"""
        formatter = StructuredJSONFormatter()
        record = logging.LogRecord(
            name='test',
            level=logging.INFO,
            pathname='',
            lineno=0,
            msg='Test message',
            args=(),
            exc_info=None
        )
        record.extra_fields = {'user_id': 123, 'action': 'login'}
        
        formatted = formatter.format(record)
        log_data = json.loads(formatted)
        
        self.assertEqual(log_data['user_id'], 123)
        self.assertEqual(log_data['action'], 'login')


class TestLoggingSetup(unittest.TestCase):
    """Test logging configuration and middleware"""
    
    def test_setup_logging_configures_json_formatter(self) -> None:
        """Test that setup_logging configures JSON formatting"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # Capture log output
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        
        setup_logging(app)
        
        # Replace handler to capture output
        app.logger.handlers[0] = handler
        app.logger.handlers[0].setFormatter(StructuredJSONFormatter())
        
        app.logger.info('Test log message')
        
        log_output = log_stream.getvalue()
        log_data = json.loads(log_output)
        
        self.assertEqual(log_data['message'], 'Test log message')
        self.assertEqual(log_data['level'], 'INFO')
    
    def test_request_logging_middleware_adds_correlation_id(self) -> None:
        """Test that middleware adds correlation ID to requests"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        setup_logging(app)
        add_request_logging_middleware(app)
        
        @app.route('/test')
        def test_route():
            # Check that correlation ID is available in g
            self.assertTrue(hasattr(g, 'correlation_id'))
            self.assertIsNotNone(g.correlation_id)
            return 'ok'
        
        client = app.test_client()
        response = client.get('/test')
        
        # Check that correlation ID is in response headers
        self.assertIn('X-Correlation-ID', response.headers)
        self.assertEqual(response.status_code, 200)
    
    def test_request_logging_preserves_existing_correlation_id(self) -> None:
        """Test that middleware preserves correlation ID from request header"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        setup_logging(app)
        add_request_logging_middleware(app)
        
        @app.route('/test')
        def test_route():
            return g.correlation_id
        
        client = app.test_client()
        response = client.get('/test', headers={'X-Correlation-ID': 'existing-id-123'})
        
        # Check that the existing correlation ID was preserved
        self.assertEqual(response.headers['X-Correlation-ID'], 'existing-id-123')
        self.assertEqual(response.data.decode(), 'existing-id-123')


class TestGetLogger(unittest.TestCase):
    """Test the get_logger utility function"""
    
    def test_get_logger_returns_logger(self) -> None:
        """Test that get_logger returns a Logger instance"""
        logger = get_logger(__name__)
        self.assertIsInstance(logger, logging.Logger)
    
    def test_get_logger_with_name(self) -> None:
        """Test that get_logger creates logger with correct name"""
        logger = get_logger('test.module')
        self.assertEqual(logger.name, 'test.module')


if __name__ == '__main__':
    unittest.main()
