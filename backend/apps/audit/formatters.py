"""
Custom logging formatters for structured logging.
"""

import json
import logging
import traceback
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging.
    Outputs logs in JSON format with consistent structure.
    """
    
    def format(self, record):
        log_data = {
            'timestamp': datetime.utcfromtimestamp(record.created).isoformat() + 'Z',
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
            'request_id': getattr(record, 'request_id', 'no-request-id'),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = {
                'type': record.exc_info[0].__name__,
                'message': str(record.exc_info[1]),
                'traceback': traceback.format_exception(*record.exc_info)
            }
        
        # Add extra fields if present
        if hasattr(record, 'extra_data'):
            log_data['extra'] = record.extra_data
        
        # Add user info if present
        if hasattr(record, 'user_id'):
            log_data['user_id'] = record.user_id
        
        if hasattr(record, 'user_email'):
            log_data['user_email'] = record.user_email
        
        # Add request info if present
        if hasattr(record, 'request_method'):
            log_data['request'] = {
                'method': record.request_method,
                'path': getattr(record, 'request_path', None),
                'ip': getattr(record, 'request_ip', None),
            }
        
        return json.dumps(log_data)


class ColoredConsoleFormatter(logging.Formatter):
    """
    Colored console formatter for development environment.
    Makes logs easier to read in the console.
    """
    
    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m',       # Reset
    }
    
    def format(self, record):
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            colored_levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"
            record.levelname = colored_levelname
        
        # Add request ID if present
        request_id = getattr(record, 'request_id', None)
        if request_id and request_id != 'no-request-id':
            record.msg = f"[{request_id[:8]}] {record.msg}"
        
        # Format the message
        formatted = super().format(record)
        
        # Reset levelname for next use
        record.levelname = levelname
        
        return formatted
