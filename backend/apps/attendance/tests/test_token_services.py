"""
Tests for QR token generation and verification services.
"""

from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone
from apps.attendance.services import (
    generate_qr_token,
    generate_6digit_code,
    verify_qr_token
)


class TokenGenerationTests(TestCase):
    """Test token generation functions."""
    
    def test_generate_qr_token_structure(self):
        """Test that generate_qr_token returns valid JWT with correct payload."""
        session_id = 123
        expires_at = datetime.utcnow() + timedelta(hours=2)
        
        token, nonce = generate_qr_token(session_id, expires_at)
        
        # Verify token and nonce are returned
        self.assertIsNotNone(token)
        self.assertIsNotNone(nonce)
        self.assertIsInstance(token, str)
        self.assertIsInstance(nonce, str)
        
        # Verify token can be decoded
        is_valid, payload, error = verify_qr_token(token)
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        self.assertEqual(payload['session_id'], session_id)
        self.assertEqual(payload['nonce'], nonce)
        self.assertEqual(payload['type'], 'attendance_qr')
    
    def test_generate_6digit_code_format(self):
        """Test that generate_6digit_code returns valid 6-digit string."""
        code = generate_6digit_code()
        
        self.assertIsInstance(code, str)
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())
    
    def test_generate_6digit_code_uniqueness(self):
        """Test that multiple calls generate different codes (probabilistic)."""
        codes = set()
        for _ in range(100):
            codes.add(generate_6digit_code())
        
        # With 100 codes, we should have high probability of uniqueness
        self.assertGreater(len(codes), 90)
    
    def test_generate_6digit_code_leading_zeros(self):
        """Test that 6-digit codes can have leading zeros."""
        # Generate many codes to increase probability of getting one with leading zero
        codes = [generate_6digit_code() for _ in range(1000)]
        
        # Check that all codes are exactly 6 digits
        for code in codes:
            self.assertEqual(len(code), 6)
            self.assertTrue(code.isdigit())
        
        # At least some codes should start with '0' (probabilistically)
        codes_with_leading_zero = [c for c in codes if c.startswith('0')]
        self.assertGreater(len(codes_with_leading_zero), 0)
    
    def test_generate_qr_token_different_sessions(self):
        """Test that tokens for different sessions are unique."""
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        token1, nonce1 = generate_qr_token(1, expires_at)
        token2, nonce2 = generate_qr_token(2, expires_at)
        
        self.assertNotEqual(token1, token2)
        self.assertNotEqual(nonce1, nonce2)
    
    def test_generate_qr_token_nonce_uniqueness(self):
        """Test that nonces are unique across multiple token generations."""
        expires_at = datetime.utcnow() + timedelta(hours=1)
        nonces = set()
        
        for i in range(50):
            token, nonce = generate_qr_token(i, expires_at)
            nonces.add(nonce)
        
        # All nonces should be unique
        self.assertEqual(len(nonces), 50)


class TokenVerificationTests(TestCase):
    """Test token verification functions."""
    
    def test_verify_valid_token(self):
        """Test verification of valid token."""
        session_id = 456
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        token, nonce = generate_qr_token(session_id, expires_at)
        is_valid, payload, error = verify_qr_token(token)
        
        self.assertTrue(is_valid)
        self.assertIsNotNone(payload)
        self.assertIsNone(error)
        self.assertEqual(payload['session_id'], session_id)
    
    def test_verify_expired_token(self):
        """Test verification of expired token."""
        session_id = 789
        expires_at = datetime.utcnow() - timedelta(hours=1)  # Already expired
        
        token, nonce = generate_qr_token(session_id, expires_at)
        is_valid, payload, error = verify_qr_token(token)
        
        self.assertFalse(is_valid)
        self.assertIsNone(payload)
        self.assertEqual(error, "Token expired")
    
    def test_verify_invalid_token(self):
        """Test verification of malformed token."""
        invalid_token = "invalid.token.string"
        
        is_valid, payload, error = verify_qr_token(invalid_token)
        
        self.assertFalse(is_valid)
        self.assertIsNone(payload)
        self.assertEqual(error, "Invalid token")
    
    def test_verify_empty_token(self):
        """Test verification of empty token."""
        is_valid, payload, error = verify_qr_token("")
        
        self.assertFalse(is_valid)
        self.assertIsNone(payload)
        self.assertEqual(error, "Invalid token")
    
    def test_token_contains_all_required_fields(self):
        """Test that generated token contains all required fields."""
        session_id = 999
        expires_at = datetime.utcnow() + timedelta(hours=1)
        
        token, nonce = generate_qr_token(session_id, expires_at)
        is_valid, payload, error = verify_qr_token(token)
        
        self.assertTrue(is_valid)
        self.assertIn('session_id', payload)
        self.assertIn('nonce', payload)
        self.assertIn('iat', payload)
        self.assertIn('exp', payload)
        self.assertIn('type', payload)
        self.assertEqual(payload['type'], 'attendance_qr')
