"""
Tests for QRToken model and manager.
"""

from datetime import datetime, timedelta
from django.test import TestCase
from django.utils import timezone
from django.contrib.gis.geos import Point
from apps.accounts.models import User, Role, Institution
from apps.academics.models import Course
from apps.attendance.models import AttendanceSession, QRToken
from apps.attendance.services import generate_qr_token, generate_6digit_code


class QRTokenManagerTests(TestCase):
    """Test QRToken custom manager methods."""
    
    def setUp(self):
        """Set up test data."""
        # Create institution
        self.institution = Institution.objects.create(
            name="Test University",
            timezone="UTC"
        )
        
        # Create role
        self.teacher_role = Role.objects.create(name="teacher")
        
        # Create teacher user
        self.teacher = User.objects.create_user(
            email="teacher@test.com",
            password="testpass123",
            full_name="Test Teacher",
            role=self.teacher_role,
            institution=self.institution
        )
        
        # Create course
        self.course = Course.objects.create(
            institution=self.institution,
            code="CS101",
            title="Intro to CS",
            instructor=self.teacher
        )
        
        # Create attendance session
        self.session = AttendanceSession.objects.create(
            course=self.course,
            created_by=self.teacher,
            start_at=timezone.now(),
            end_at=timezone.now() + timedelta(hours=2),
            teacher_location=Point(0.0, 0.0),
            radius_meters=50
        )
    
    def test_create_token(self):
        """Test creating a token using manager method."""
        token_str, nonce = generate_qr_token(self.session.id, self.session.end_at)
        code6 = generate_6digit_code()
        
        qr_token = QRToken.objects.create_token(
            session=self.session,
            token=token_str,
            code6=code6,
            expires_at=self.session.end_at
        )
        
        self.assertIsNotNone(qr_token.id)
        self.assertEqual(qr_token.session, self.session)
        self.assertEqual(qr_token.token, token_str)
        self.assertEqual(qr_token.code6, code6)
        self.assertFalse(qr_token.is_revoked)
    
    def test_get_by_token(self):
        """Test retrieving token by token string."""
        token_str, nonce = generate_qr_token(self.session.id, self.session.end_at)
        code6 = generate_6digit_code()
        
        created_token = QRToken.objects.create_token(
            session=self.session,
            token=token_str,
            code6=code6,
            expires_at=self.session.end_at
        )
        
        retrieved_token = QRToken.objects.get_by_token(token_str)
        
        self.assertIsNotNone(retrieved_token)
        self.assertEqual(retrieved_token.id, created_token.id)
    
    def test_get_by_token_not_found(self):
        """Test retrieving non-existent token returns None."""
        retrieved_token = QRToken.objects.get_by_token("nonexistent.token")
        
        self.assertIsNone(retrieved_token)
    
    def test_get_by_code6(self):
        """Test retrieving token by 6-digit code."""
        token_str, nonce = generate_qr_token(self.session.id, self.session.end_at)
        code6 = generate_6digit_code()
        
        created_token = QRToken.objects.create_token(
            session=self.session,
            token=token_str,
            code6=code6,
            expires_at=self.session.end_at
        )
        
        retrieved_token = QRToken.objects.get_by_code6(code6)
        
        self.assertIsNotNone(retrieved_token)
        self.assertEqual(retrieved_token.id, created_token.id)
    
    def test_get_by_code6_not_found(self):
        """Test retrieving non-existent code returns None."""
        retrieved_token = QRToken.objects.get_by_code6("999999")
        
        self.assertIsNone(retrieved_token)
    
    def test_revoke_token(self):
        """Test revoking a token."""
        token_str, nonce = generate_qr_token(self.session.id, self.session.end_at)
        code6 = generate_6digit_code()
        
        qr_token = QRToken.objects.create_token(
            session=self.session,
            token=token_str,
            code6=code6,
            expires_at=self.session.end_at
        )
        
        self.assertFalse(qr_token.is_revoked)
        
        qr_token.revoke()
        
        self.assertTrue(qr_token.is_revoked)
        
        # Verify revoked token is not returned by manager methods
        retrieved_token = QRToken.objects.get_by_token(token_str)
        self.assertIsNone(retrieved_token)
    
    def test_unique_constraint_on_token(self):
        """Test that duplicate tokens are not allowed."""
        token_str, nonce = generate_qr_token(self.session.id, self.session.end_at)
        code6 = generate_6digit_code()
        
        QRToken.objects.create_token(
            session=self.session,
            token=token_str,
            code6=code6,
            expires_at=self.session.end_at
        )
        
        # Try to create another token with same token string
        with self.assertRaises(Exception):  # Will raise IntegrityError
            QRToken.objects.create_token(
                session=self.session,
                token=token_str,
                code6=generate_6digit_code(),
                expires_at=self.session.end_at
            )
