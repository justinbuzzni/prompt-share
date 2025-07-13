"""
Test script for security redaction functionality
"""
from security_utils import detect_secrets, redact_text, scan_and_report

# Test cases with various types of sensitive information
test_cases = [
    # API Keys
    """
    Here's my API configuration:
    API_KEY=sk-1234567890abcdefghijklmnopqrstuvwxyz12345678
    GOOGLE_API_KEY=AIzaSyD1234567890abcdefghijklmnopqrstu
    """,
    
    # Database credentials
    """
    Database connection:
    mongodb://admin:SuperSecret123!@localhost:27017/mydb
    password: MyP@ssw0rd123
    DB_PASSWORD=production_password_2024
    """,
    
    # AWS credentials
    """
    AWS Configuration:
    AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
    AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    """,
    
    # JWT and OAuth
    """
    Authentication tokens:
    Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiaWF0IjoxNTE2MjM5MDIyfQ.SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
    client_secret: 1234567890abcdefghijklmnopqrstuvwxyz
    """,
    
    # Private keys (shortened for demo)
    """
    SSH Key:
    -----BEGIN RSA PRIVATE KEY-----
    MIIEpAIBAAKCAQEA1234567890abcdefghijklmnop
    -----END RSA PRIVATE KEY-----
    """,
]

def main():
    print("Security Redaction Test")
    print("=" * 60)
    
    for i, test_text in enumerate(test_cases, 1):
        print(f"\nTest Case {i}:")
        print("-" * 40)
        
        # Detect secrets
        secrets = detect_secrets(test_text)
        if secrets:
            print(f"Found {len(secrets)} secret(s):")
            for secret_text, secret_type, category in secrets:
                # Show only first 8 chars for demo
                sample = f"{secret_text[:8]}..." if len(secret_text) > 8 else secret_text
                print(f"  - {secret_type} ({category}): {sample}")
        
        # Redact text
        redacted, stats = redact_text(test_text)
        print(f"\nRedacted text preview:")
        print(redacted.strip()[:200] + "..." if len(redacted) > 200 else redacted.strip())
        
        print(f"\nRedaction statistics:")
        for secret_type, count in stats.items():
            print(f"  - {secret_type}: {count}")

if __name__ == "__main__":
    main()