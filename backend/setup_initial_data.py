#!/usr/bin/env python
"""
Script to create initial data for the Smart Attendance System.
Creates institution, roles, and admin user.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.accounts.models import User, Institution, Role

def setup_initial_data():
    """Create initial institution, roles, and admin user."""
    
    # Create institution if it doesn't exist
    institution, created = Institution.objects.get_or_create(
        name='Test University',
        defaults={'timezone': 'UTC'}
    )
    if created:
        print(f"✓ Created institution: {institution.name}")
    else:
        print(f"✓ Institution already exists: {institution.name}")
    
    # Create roles if they don't exist
    roles_data = [
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    
    for role_name, role_display in roles_data:
        role, created = Role.objects.get_or_create(name=role_name)
        if created:
            print(f"✓ Created role: {role_display}")
        else:
            print(f"✓ Role already exists: {role_display}")
    
    # Create admin user if it doesn't exist
    admin_role = Role.objects.get(name='admin')
    
    if not User.objects.filter(email='admin@example.com').exists():
        admin_user = User.objects.create_superuser(
            email='admin@example.com',
            password='admin123',
            full_name='Admin User',
            role=admin_role,
            institution=institution
        )
        print(f"✓ Created admin user: {admin_user.email}")
        print(f"  Email: admin@example.com")
        print(f"  Password: admin123")
    else:
        print(f"✓ Admin user already exists: admin@example.com")
    
    print("\n✅ Initial data setup complete!")
    print("\nYou can now access:")
    print("  - Frontend: http://localhost:3000")
    print("  - Backend API: http://localhost:8000/api")
    print("  - Django Admin: http://localhost:8000/admin")
    print("\nLogin credentials:")
    print("  Email: admin@example.com")
    print("  Password: admin123")

if __name__ == '__main__':
    setup_initial_data()
