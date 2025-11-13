# Requirements Document

## Introduction

The Smart Attendance Web System is a web-based platform that enables educational institutions to manage student attendance through QR code or 6-digit code scanning with geolocation verification. The system ensures physical presence validation by matching student locations with teacher locations within a configurable radius during time-limited attendance sessions. The system supports three user roles: Admin, Teacher, and Student, with comprehensive audit trails for all operations.

## Glossary

- **System**: The Smart Attendance Web System
- **Admin**: A user with administrative privileges who manages users, courses, schedules, and can override attendance records
- **Teacher**: A user who creates attendance sessions and monitors student attendance for assigned courses
- **Student**: A user who marks attendance by scanning QR codes or entering 6-digit codes
- **Attendance Session**: A time-limited period during which students can mark their attendance for a specific class
- **QR Token**: A cryptographically secure token encoded in a QR code or represented as a 6-digit code
- **Geolocation Verification**: The process of validating that a student's reported location is within the configured radius of the teacher's location
- **Audit Trail**: A chronological record of all system operations including who performed the action, what was changed, when it occurred, and why

## Requirements

### Requirement 1: User Authentication and Authorization

**User Story:** As a system user, I want to securely log in with my credentials and access features appropriate to my role, so that the system maintains proper access control and security.

#### Acceptance Criteria

1. WHEN a user submits valid credentials, THE System SHALL authenticate the user and issue a JWT access token and refresh token
2. WHEN a user attempts to access a protected resource, THE System SHALL verify the JWT token and authorize access based on the user's role
3. THE System SHALL hash all user passwords using bcrypt or argon2 before storing them in the database
4. WHEN a JWT access token expires, THE System SHALL allow the user to obtain a new access token using a valid refresh token
5. THE System SHALL enforce HTTPS for all authentication endpoints

### Requirement 2: Teacher Attendance Session Creation

**User Story:** As a Teacher, I want to create time-limited attendance sessions with QR codes for my assigned courses, so that students can mark their attendance during class.

#### Acceptance Criteria

1. WHEN a Teacher creates an attendance session, THE System SHALL verify that the Teacher is assigned to the specified course
2. WHEN a Teacher creates an attendance session, THE System SHALL capture the Teacher's geolocation coordinates at the time of creation
3. WHEN a Teacher creates an attendance session, THE System SHALL generate a cryptographically secure QR token and a 6-digit fallback code
4. THE System SHALL create attendance sessions with a configurable radius between 10 meters and 500 meters
5. WHEN an attendance session is created, THE System SHALL set the QR token expiration time to match the session end time
6. THE System SHALL store the Teacher's location coordinates with the attendance session record

### Requirement 3: Student Attendance Marking via QR Scan

**User Story:** As a Student, I want to mark my attendance by scanning a QR code or entering a 6-digit code, so that my presence is recorded for the class.

#### Acceptance Criteria

1. WHEN a Student scans a QR token, THE System SHALL verify that the token exists, is not expired, and is not revoked
2. WHEN a Student submits attendance, THE System SHALL capture the Student's geolocation coordinates at the time of submission
3. WHEN a Student submits attendance, THE System SHALL calculate the distance between the Student's location and the Teacher's session location using the Haversine formula
4. IF the calculated distance exceeds the session's configured radius, THEN THE System SHALL reject the attendance submission with status "rejected" and reason "Outside allowed radius"
5. IF the calculated distance is within the session's configured radius, THEN THE System SHALL create an attendance record with status "present"
6. WHEN a Student submits attendance, THE System SHALL verify that the current server time is within the session's start and end time window
7. THE System SHALL prevent duplicate attendance records by enforcing a unique constraint on session and student combination

### Requirement 4: Geolocation Validation

**User Story:** As an Admin, I want the system to validate student locations against teacher locations, so that only physically present students can mark attendance.

#### Acceptance Criteria

1. WHEN calculating distance between two locations, THE System SHALL use the Haversine formula with Earth radius of 6371000 meters
2. WHEN a Student submits attendance, THE System SHALL store both the Teacher's location and Student's location in the attendance record
3. WHEN a Student submits attendance, THE System SHALL store the calculated distance in meters in the attendance record
4. IF a Student's geolocation accuracy exceeds 100 meters, THEN THE System SHALL reject the attendance submission with reason "Location accuracy insufficient"
5. IF a Student's geolocation coordinates are exactly 0.0 for both latitude and longitude, THEN THE System SHALL reject the attendance submission with reason "Invalid location data"

### Requirement 5: Admin User Management

**User Story:** As an Admin, I want to manage user accounts including creating, updating, and deactivating users, so that I can control system access.

#### Acceptance Criteria

1. WHEN an Admin creates a user account, THE System SHALL require email, password, full name, and role
2. WHEN an Admin creates a user account, THE System SHALL validate that the email is unique across all users
3. WHEN an Admin updates a user's role, THE System SHALL record the change in the audit log with the Admin's user ID and timestamp
4. WHEN an Admin deactivates a user account, THE System SHALL set the user's is_active flag to false without deleting the user record
5. THE System SHALL restrict user creation, update, and deactivation operations to users with Admin role only

### Requirement 6: Course and Enrollment Management

**User Story:** As an Admin, I want to manage courses and student enrollments, so that the system accurately reflects the institution's academic structure.

#### Acceptance Criteria

1. WHEN an Admin creates a course, THE System SHALL require course code, title, and instructor assignment
2. WHEN an Admin enrolls a Student in a course, THE System SHALL verify that the Student user has the Student role
3. THE System SHALL enforce a unique constraint preventing duplicate enrollments of the same Student in the same course
4. WHEN an Admin assigns a Teacher to a course, THE System SHALL verify that the user has the Teacher role
5. WHEN an Admin creates a schedule for a course, THE System SHALL require weekday, start time, duration, and location coordinates

### Requirement 7: Attendance Record Override

**User Story:** As an Admin, I want to override attendance records with a mandatory reason, so that I can correct errors or handle exceptional cases.

#### Acceptance Criteria

1. WHEN an Admin overrides an attendance record status, THE System SHALL require a textual reason for the override
2. WHEN an Admin overrides an attendance record, THE System SHALL create an audit log entry containing the Admin's user ID, old status, new status, reason, and timestamp
3. WHEN an Admin overrides an attendance record, THE System SHALL update the attendance record's status and reason fields
4. THE System SHALL allow Admins to change attendance status to "present", "absent", "rejected", or "pending"
5. THE System SHALL restrict attendance record override operations to users with Admin role only

### Requirement 8: QR Token Security

**User Story:** As a system administrator, I want QR tokens to be cryptographically secure and time-limited, so that attendance cannot be fraudulently marked.

#### Acceptance Criteria

1. WHEN generating a QR token, THE System SHALL create a signed JWT token or HMAC-based token containing session ID, nonce, issued-at timestamp, and expiration timestamp
2. WHEN generating a QR token, THE System SHALL create a unique 6-digit numeric code mapped to the token in the database
3. WHEN a Student submits a QR token, THE System SHALL verify the token signature using the server secret key
4. WHEN a QR token expires, THE System SHALL reject any attendance submissions using that token with reason "Token expired"
5. THE System SHALL store QR tokens with a unique constraint on the token string to prevent duplicates

### Requirement 9: Rate Limiting and Anti-Fraud

**User Story:** As a system administrator, I want the system to detect and prevent fraudulent attendance attempts, so that the integrity of attendance data is maintained.

#### Acceptance Criteria

1. WHEN a Student submits attendance, THE System SHALL enforce a rate limit of 10 requests per minute per student user ID
2. WHEN a Student submits attendance, THE System SHALL enforce a rate limit of 50 requests per minute per IP address
3. IF more than 5 Students submit identical geolocation coordinates for the same session, THEN THE System SHALL flag those attendance records for Admin review
4. WHEN a Student submits attendance with a device timestamp that differs from server time by more than 300 seconds, THE System SHALL flag the attendance record for Admin review
5. THE System SHALL reject attendance submissions that exceed the configured rate limits with HTTP status 429

### Requirement 10: Audit Logging

**User Story:** As an Admin, I want comprehensive audit logs of all system operations, so that I can track changes and investigate issues.

#### Acceptance Criteria

1. WHEN an Admin overrides an attendance record, THE System SHALL create an audit log entry with performed_by user ID, action description, target table name, target record ID, old data JSON, new data JSON, and timestamp
2. WHEN an Admin creates or modifies a user account, THE System SHALL create an audit log entry with the operation details
3. WHEN a Teacher creates an attendance session, THE System SHALL create an audit log entry with the session details
4. THE System SHALL store audit log entries with a timestamp precision of milliseconds
5. THE System SHALL allow Admins to query audit logs filtered by user, date range, action type, and target table

### Requirement 11: Attendance Reporting

**User Story:** As a Teacher, I want to export attendance reports for my courses, so that I can analyze attendance patterns and submit records to administration.

#### Acceptance Criteria

1. WHEN a Teacher requests an attendance report, THE System SHALL verify that the Teacher is assigned to the specified course
2. WHEN a Teacher exports attendance data, THE System SHALL generate a CSV file containing student name, email, session date, session time, status, and marked timestamp
3. WHEN a Teacher filters attendance reports by date range, THE System SHALL return only attendance records where the session start time falls within the specified range
4. THE System SHALL allow Teachers to export attendance reports for courses they are assigned to only
5. WHEN generating large reports exceeding 1000 records, THE System SHALL stream the CSV output to prevent memory exhaustion

### Requirement 12: Session Time Window Validation

**User Story:** As a Teacher, I want attendance sessions to enforce strict time windows, so that students can only mark attendance during the designated class period.

#### Acceptance Criteria

1. WHEN a Student submits attendance, THE System SHALL verify that the current server timestamp is greater than or equal to the session start time
2. WHEN a Student submits attendance, THE System SHALL verify that the current server timestamp is less than or equal to the session end time
3. IF the current server time is outside the session time window, THEN THE System SHALL reject the attendance submission with reason "Outside session time window"
4. WHEN a session end time is reached, THE System SHALL automatically set the session status to "expired"
5. THE System SHALL use server time as the authoritative time source for all time-based validations

### Requirement 13: Multi-Institution Support

**User Story:** As a system administrator, I want to support multiple institutions in a single deployment, so that the system can serve multiple organizations.

#### Acceptance Criteria

1. WHEN creating a user account, THE System SHALL associate the user with an institution ID
2. WHEN a user queries data, THE System SHALL filter results to include only records belonging to the user's institution
3. WHEN creating a course, THE System SHALL associate the course with an institution ID
4. THE System SHALL store each institution's timezone configuration and use it for time-based operations
5. THE System SHALL enforce data isolation between institutions to prevent cross-institution data access

### Requirement 14: Device Tracking

**User Story:** As an Admin, I want to track devices used for attendance marking, so that I can identify suspicious patterns and potential fraud.

#### Acceptance Criteria

1. WHEN a Student submits attendance, THE System SHALL capture the device user agent string and device identifier if available
2. WHEN a Student submits attendance from a new device, THE System SHALL create a device record associated with the Student's user ID
3. WHEN a Student submits attendance, THE System SHALL update the device's last_seen timestamp
4. THE System SHALL store device information in JSON format including user agent, platform, and device ID
5. THE System SHALL allow Admins to query attendance records filtered by device ID

### Requirement 15: Location Snapshot Logging

**User Story:** As an Admin, I want detailed location snapshots logged for both teachers and students, so that I can audit location data and investigate disputes.

#### Acceptance Criteria

1. WHEN a Teacher creates an attendance session, THE System SHALL create a location snapshot record with the Teacher's user ID, coordinates, timestamp, and source "browser_geolocation"
2. WHEN a Student submits attendance, THE System SHALL create a location snapshot record with the Student's user ID, coordinates, timestamp, and source indicating the capture method
3. THE System SHALL store location snapshots with latitude and longitude as double precision floating point numbers
4. THE System SHALL retain location snapshot records for a minimum of 180 days
5. THE System SHALL allow Admins to query location snapshots filtered by user ID and date range
