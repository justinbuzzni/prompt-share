"""
Security utilities for detecting and redacting sensitive information
"""
import re
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)

# Common patterns for sensitive information
SENSITIVE_PATTERNS = {
    # API Keys and Tokens
    'api_key': [
        (r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([a-zA-Z0-9\-_]{20,})["\']?', 'API_KEY'),
        (r'(?i)(token|access[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9\-_.]{20,})["\']?', 'ACCESS_TOKEN'),
        (r'(?i)bearer\s+([a-zA-Z0-9\-_.]{20,})', 'BEARER_TOKEN'),
        (r'sk-[a-zA-Z0-9]{48}', 'OPENAI_API_KEY'),
        (r'AIza[0-9A-Za-z\-_]{35}', 'GOOGLE_API_KEY'),
        (r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', 'UUID_TOKEN'),
    ],
    
    # AWS Credentials
    'aws': [
        (r'AKIA[0-9A-Z]{16}', 'AWS_ACCESS_KEY'),
        (r'(?i)(aws[_-]?secret[_-]?access[_-]?key|aws[_-]?secret)\s*[:=]\s*["\']?([a-zA-Z0-9/+=]{40})["\']?', 'AWS_SECRET'),
    ],
    
    # Database Credentials
    'database': [
        (r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^"\'\s]{8,})["\']?', 'PASSWORD'),
        (r'(?i)mysql://[^:]+:([^@]+)@', 'MYSQL_PASSWORD'),
        (r'(?i)postgres://[^:]+:([^@]+)@', 'POSTGRES_PASSWORD'),
        (r'(?i)mongodb://[^:]+:([^@]+)@', 'MONGODB_PASSWORD'),
        (r'(?i)(db[_-]?pass|database[_-]?password)\s*[:=]\s*["\']?([^"\'\s]+)["\']?', 'DB_PASSWORD'),
    ],
    
    # Private Keys
    'private_key': [
        (r'-----BEGIN (?:RSA |EC )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC )?PRIVATE KEY-----', 'PRIVATE_KEY'),
        (r'-----BEGIN OPENSSH PRIVATE KEY-----[\s\S]+?-----END OPENSSH PRIVATE KEY-----', 'SSH_PRIVATE_KEY'),
    ],
    
    # OAuth and Social Media
    'oauth': [
        (r'(?i)(client[_-]?secret)\s*[:=]\s*["\']?([a-zA-Z0-9\-_]{20,})["\']?', 'CLIENT_SECRET'),
        (r'(?i)(client[_-]?id)\s*[:=]\s*["\']?([a-zA-Z0-9\-_]{20,})["\']?', 'CLIENT_ID'),
    ],
    
    # Environment Variables
    'env': [
        (r'(?i)(secret[_-]?key)\s*[:=]\s*["\']?([^"\'\s]{16,})["\']?', 'SECRET_KEY'),
        (r'(?i)(auth[_-]?token)\s*[:=]\s*["\']?([a-zA-Z0-9\-_]{20,})["\']?', 'AUTH_TOKEN'),
    ],
    
    # Credit Card (basic pattern - be careful with false positives)
    'financial': [
        (r'\b(?:4[0-9]{12}(?:[0-9]{3})?|5[1-5][0-9]{14}|3[47][0-9]{13}|3(?:0[0-5]|[68][0-9])[0-9]{11}|6(?:011|5[0-9]{2})[0-9]{12})\b', 'CREDIT_CARD'),
    ],
    
    # JWT Tokens
    'jwt': [
        (r'eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*', 'JWT_TOKEN'),
    ],
}

# Whitelist patterns that should not be redacted
WHITELIST_PATTERNS = [
    r'(?i)example\.com',
    r'(?i)localhost',
    r'(?i)127\.0\.0\.1',
    r'(?i)test',
    r'(?i)demo',
    r'(?i)sample',
    r'(?i)placeholder',
    r'\*{3,}',  # Already redacted
    r'xxx+',    # Already redacted
]


def is_whitelisted(text: str) -> bool:
    """Check if text matches any whitelist pattern"""
    for pattern in WHITELIST_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False


def detect_secrets(text: str) -> List[Tuple[str, str, str]]:
    """
    Detect potential secrets in text
    
    Returns:
        List of tuples: (matched_text, secret_type, category)
    """
    if not text:
        return []
    
    secrets = []
    
    for category, patterns in SENSITIVE_PATTERNS.items():
        for pattern, secret_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.MULTILINE)
            for match in matches:
                # Get the full match or the captured group
                if match.groups():
                    # If there are capture groups, use the last one (usually the secret)
                    secret_text = match.group(len(match.groups()))
                else:
                    secret_text = match.group(0)
                
                # Skip if whitelisted
                if is_whitelisted(secret_text):
                    continue
                
                # Skip if too short (likely false positive)
                if len(secret_text) < 8:
                    continue
                
                secrets.append((secret_text, secret_type, category))
    
    return secrets


def redact_text(text: str, placeholder: str = "[REDACTED]") -> Tuple[str, Dict[str, int]]:
    """
    Redact sensitive information from text
    
    Returns:
        Tuple of (redacted_text, statistics)
    """
    if not text:
        return text, {}
    
    redacted = text
    stats = {}
    
    # Detect all secrets
    secrets = detect_secrets(text)
    
    # Sort by length (longest first) to avoid partial replacements
    secrets.sort(key=lambda x: len(x[0]), reverse=True)
    
    # Redact each secret
    for secret_text, secret_type, category in secrets:
        # Create a type-specific placeholder
        typed_placeholder = f"[REDACTED_{secret_type}]"
        
        # Replace all occurrences
        count = len(re.findall(re.escape(secret_text), redacted))
        redacted = redacted.replace(secret_text, typed_placeholder)
        
        # Update statistics
        stats[secret_type] = stats.get(secret_type, 0) + count
    
    return redacted, stats


def redact_message_content(content: any) -> Tuple[any, Dict[str, int]]:
    """
    Redact sensitive information from message content
    Handles both string and list content formats
    """
    stats = {}
    
    if isinstance(content, str):
        return redact_text(content)
    
    elif isinstance(content, list):
        redacted_content = []
        for item in content:
            if isinstance(item, dict):
                redacted_item = item.copy()
                
                # Redact text fields
                if 'text' in redacted_item and isinstance(redacted_item['text'], str):
                    redacted_item['text'], item_stats = redact_text(redacted_item['text'])
                    for key, val in item_stats.items():
                        stats[key] = stats.get(key, 0) + val
                
                # Redact content fields
                if 'content' in redacted_item and isinstance(redacted_item['content'], str):
                    redacted_item['content'], item_stats = redact_text(redacted_item['content'])
                    for key, val in item_stats.items():
                        stats[key] = stats.get(key, 0) + val
                
                redacted_content.append(redacted_item)
            else:
                redacted_content.append(item)
        
        return redacted_content, stats
    
    # Return original if not string or list
    return content, stats


def scan_and_report(text: str) -> Dict[str, any]:
    """
    Scan text for secrets and return a detailed report
    """
    secrets = detect_secrets(text)
    
    report = {
        'has_secrets': len(secrets) > 0,
        'total_secrets': len(secrets),
        'secrets_by_type': {},
        'secrets_by_category': {},
        'samples': []
    }
    
    for secret_text, secret_type, category in secrets:
        # Count by type
        report['secrets_by_type'][secret_type] = report['secrets_by_type'].get(secret_type, 0) + 1
        
        # Count by category
        report['secrets_by_category'][category] = report['secrets_by_category'].get(category, 0) + 1
        
        # Add sample (first few characters only)
        sample = f"{secret_text[:8]}..." if len(secret_text) > 8 else secret_text
        report['samples'].append({
            'type': secret_type,
            'category': category,
            'sample': sample,
            'length': len(secret_text)
        })
    
    return report