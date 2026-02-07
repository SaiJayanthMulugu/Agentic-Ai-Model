"""
Input Sanitizer
===============

Sanitizes and validates user inputs for security.

Features:
- SQL injection prevention
- XSS prevention
- Input length validation
- Special character handling
- Code injection prevention

Author: AI Ops Team
Version: 1.0.0
"""

import re
from typing import Optional, List
from src.utils.logger import get_logger

logger = get_logger(__name__)


class InputSanitizer:
    """
    Sanitizes user inputs to prevent security vulnerabilities.
    """
    
    # Dangerous SQL keywords
    SQL_KEYWORDS = [
        "DROP", "DELETE", "TRUNCATE", "ALTER", "CREATE", "INSERT", "UPDATE",
        "EXEC", "EXECUTE", "GRANT", "REVOKE", "SHUTDOWN", "KILL"
    ]
    
    # Dangerous patterns
    DANGEROUS_PATTERNS = [
        r"<script[^>]*>.*?</script>",  # XSS scripts
        r"javascript:",  # JavaScript protocol
        r"on\w+\s*=",  # Event handlers
        r"eval\s*\(",  # eval() calls
        r"exec\s*\(",  # exec() calls
    ]
    
    def __init__(self, max_length: int = 10000):
        """
        Initialize InputSanitizer.
        
        Args:
            max_length: Maximum input length
        """
        self.max_length = max_length
    
    def sanitize(self, input_text: str, allow_sql: bool = False) -> str:
        """
        Sanitize input text.
        
        Args:
            input_text: Input text to sanitize
            allow_sql: Whether to allow SQL keywords (for code generation)
        
        Returns:
            Sanitized text
        
        Raises:
            ValueError: If input is invalid or dangerous
        """
        if not isinstance(input_text, str):
            raise ValueError("Input must be a string")
        
        # Check length
        if len(input_text) > self.max_length:
            raise ValueError(f"Input exceeds maximum length of {self.max_length} characters")
        
        # Remove null bytes
        sanitized = input_text.replace("\x00", "")
        
        # Check for dangerous patterns
        if not allow_sql:
            sanitized = self._remove_sql_keywords(sanitized)
        
        sanitized = self._remove_dangerous_patterns(sanitized)
        
        # Trim whitespace
        sanitized = sanitized.strip()
        
        if len(sanitized) == 0:
            raise ValueError("Input is empty after sanitization")
        
        return sanitized
    
    def _remove_sql_keywords(self, text: str) -> str:
        """
        Remove or flag dangerous SQL keywords.
        
        Args:
            text: Input text
        
        Returns:
            Text with SQL keywords removed
        """
        words = text.split()
        sanitized_words = []
        
        for word in words:
            # Remove SQL comment syntax
            if word.startswith("--") or word.startswith("/*"):
                continue
            
            # Check for SQL keywords (case-insensitive)
            if word.upper() in self.SQL_KEYWORDS:
                logger.warning(f"Potentially dangerous SQL keyword detected: {word}")
                continue
            
            sanitized_words.append(word)
        
        return " ".join(sanitized_words)
    
    def _remove_dangerous_patterns(self, text: str) -> str:
        """
        Remove dangerous patterns (XSS, code injection, etc.).
        
        Args:
            text: Input text
        
        Returns:
            Text with dangerous patterns removed
        """
        sanitized = text
        
        for pattern in self.DANGEROUS_PATTERNS:
            matches = re.findall(pattern, sanitized, re.IGNORECASE | re.DOTALL)
            if matches:
                logger.warning(f"Dangerous pattern detected: {pattern}")
                sanitized = re.sub(pattern, "", sanitized, flags=re.IGNORECASE | re.DOTALL)
        
        return sanitized
    
    def validate_user_id(self, user_id: str) -> bool:
        """
        Validate user ID format.
        
        Args:
            user_id: User ID to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not user_id or not isinstance(user_id, str):
            return False
        
        # Allow alphanumeric, dash, underscore, @, dot
        pattern = r"^[a-zA-Z0-9_\-@.]+$"
        return bool(re.match(pattern, user_id))
    
    def validate_agent_name(self, agent_name: str) -> bool:
        """
        Validate agent name format.
        
        Args:
            agent_name: Agent name to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not agent_name or not isinstance(agent_name, str):
            return False
        
        # Allow alphanumeric and underscore
        pattern = r"^[a-zA-Z0-9_]+$"
        return bool(re.match(pattern, agent_name))

