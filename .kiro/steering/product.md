# Product Overview

Smart Attendance System is a web-based attendance management platform for educational institutions that uses QR codes and geolocation verification to ensure accurate attendance tracking.

## Core Features

- **QR Code Attendance**: Teachers generate time-limited QR codes for attendance sessions
- **Geolocation Verification**: Validates student physical presence within configurable radius using PostGIS
- **Multi-Role System**: Admin, Teacher, and Student roles with role-based permissions
- **Fraud Prevention**: Rate limiting and anti-spoofing measures to prevent attendance fraud
- **Audit Trail**: Comprehensive logging of all system operations
- **Reporting**: CSV export with filtering options for attendance data

## Key Domains

- **Accounts**: User authentication, authorization, and profile management
- **Academics**: Course and enrollment management
- **Attendance**: Session creation, QR token generation, and attendance marking
- **Geo**: Geolocation utilities and distance validation
- **Audit**: System-wide audit logging
- **Reports**: Data export and analytics
