# Student QR Scanning Interface Implementation

## Overview

This document describes the implementation of the student QR scanning interface (Task 17) for the Smart Attendance Web System. The interface allows students to mark their attendance by scanning QR codes or entering 6-digit codes, with geolocation verification.

## Components Implemented

### 1. QRScanner Component (`src/components/student/QRScanner.jsx`)

**Purpose**: Camera-based QR code scanner using html5-qrcode library

**Features**:
- Initializes Html5QrcodeScanner with optimized settings (10 fps, 250x250 scan box)
- Requests camera permission automatically
- Displays camera preview with scan overlay
- Shows torch (flashlight) button if device supports it
- Shows zoom slider if device supports it
- Emits scanned token to parent component via `onScanSuccess` callback
- Handles camera errors and permission denial with user-friendly messages
- Automatically stops scanning after successful scan
- Proper cleanup on component unmount

**Error Handling**:
- NotAllowedError: Camera permission denied
- NotFoundError: No camera found on device
- NotReadableError: Camera already in use by another application

**Props**:
- `onScanSuccess(decodedText, decodedResult)`: Callback when QR code is successfully scanned
- `onScanError(error)`: Callback when critical camera error occurs

### 2. ManualCodeEntry Component (`src/components/student/ManualCodeEntry.jsx`)

**Purpose**: Fallback 6-digit code entry for when QR scanning is not available

**Features**:
- Input field that only accepts numeric characters
- Automatically limits input to 6 digits
- Real-time character count display (X/6 digits)
- Validates that exactly 6 digits are entered before submission
- Handles paste events to extract only digits from pasted content
- Loading state during submission
- Disabled state when loading
- User-friendly instructions

**Validation**:
- Only numeric input allowed
- Exactly 6 digits required
- Shows error message if validation fails

**Props**:
- `onSubmit(code)`: Callback when valid 6-digit code is submitted
- `loading`: Boolean to show loading state during submission

### 3. ScanPage Component (`src/components/student/ScanPage.jsx`)

**Purpose**: Main attendance marking interface with tabs for QR scan and manual entry

**Features**:
- Two tabs: "Scan QR Code" and "Enter Code"
- Automatic geolocation capture on page load
- Location status banner showing:
  - Loading state while getting location
  - Success state with accuracy information
  - Error state with retry button
- Prevents attendance submission without valid location
- Calls attendance marking API with token and location data
- Displays detailed result after submission:
  - Success: Shows status, distance, and timestamp
  - Failure: Shows error message and reason
- "Try Again" button to reset and mark another attendance
- Includes device information in API request (user agent, platform, timestamp)

**Location Requirements**:
- High accuracy location required
- 10 second timeout
- No cached location (maximumAge: 0)

**API Integration**:
- Uses `attendanceAPI.markAttendance()` from services
- Sends: token, student_location (lat/lon/accuracy), device_info
- Receives: status, message, distance_meters, marked_at, reason (if rejected)

**States**:
- activeTab: 'qr' or 'manual'
- submitting: Boolean for API call in progress
- result: Object with success, message, and data
- location: From useGeolocation hook
- locationError: From useGeolocation hook
- locationLoading: From useGeolocation hook

### 4. AttendanceHistory Component (`src/components/student/AttendanceHistory.jsx`)

**Purpose**: Display student's attendance records with filtering capabilities

**Features**:
- Fetches attendance history from API on mount
- Displays records in responsive table (desktop) and cards (mobile)
- Shows: course name/code, date, time, status badge, distance
- Filtering by:
  - From date
  - To date
  - Course ID (prepared for future implementation)
- Clear filters button
- Loading state with spinner
- Error state with retry button
- Empty state when no records found
- Record count display
- Color-coded status badges:
  - Present: Green
  - Absent: Red
  - Rejected: Yellow
  - Pending: Gray

**API Integration**:
- Uses `attendanceAPI.getAttendanceHistory(params)` from services
- Supports query parameters: from_date, to_date, course_id
- Handles both paginated and non-paginated responses

**Responsive Design**:
- Desktop: Full table with all columns
- Mobile: Card layout with stacked information

## StudentDashboard Integration

Updated `src/pages/StudentDashboard.jsx` to include:
- Tab navigation between "Mark Attendance" and "Attendance History"
- Renders ScanPage component in "Mark Attendance" tab
- Renders AttendanceHistory component in "Attendance History" tab
- Maintains existing header with user info and logout button

## Dependencies Used

- `html5-qrcode`: QR code scanning library
- `react-router-dom`: Navigation
- `axios`: HTTP client (via api service)
- Existing hooks: `useAuth`, `useGeolocation`
- Existing services: `attendanceAPI`

## File Structure

```
frontend/src/
├── components/
│   └── student/
│       ├── QRScanner.jsx
│       ├── ManualCodeEntry.jsx
│       ├── ScanPage.jsx
│       ├── AttendanceHistory.jsx
│       └── index.js
├── pages/
│   └── StudentDashboard.jsx
├── hooks/
│   └── useGeolocation.js (existing)
└── services/
    └── api.js (existing)
```

## API Endpoints Used

### Mark Attendance
- **Endpoint**: `POST /api/student/attendance/scan/`
- **Request Body**:
  ```json
  {
    "token": "string (JWT or 6-digit code)",
    "student_location": {
      "latitude": number,
      "longitude": number,
      "accuracy": number
    },
    "device_info": {
      "user_agent": "string",
      "platform": "string",
      "timestamp": "ISO 8601 string"
    }
  }
  ```
- **Response** (Success):
  ```json
  {
    "status": "present",
    "message": "Attendance marked successfully",
    "distance_meters": 45.3,
    "marked_at": "2025-11-15T14:30:00Z"
  }
  ```
- **Response** (Failure):
  ```json
  {
    "status": "rejected",
    "message": "Outside allowed radius",
    "reason": "Outside allowed radius",
    "distance_meters": 150.5
  }
  ```

### Get Attendance History
- **Endpoint**: `GET /api/student/attendance/`
- **Query Parameters**:
  - `from_date`: ISO date string (optional)
  - `to_date`: ISO date string (optional)
  - `course_id`: Integer (optional)
- **Response**:
  ```json
  {
    "results": [
      {
        "id": 1,
        "session": {
          "course": {
            "title": "Introduction to Computer Science",
            "code": "CS101"
          },
          "start_at": "2025-11-15T14:00:00Z"
        },
        "status": "present",
        "marked_at": "2025-11-15T14:05:00Z",
        "distance_meters": 45.3
      }
    ]
  }
  ```

## Requirements Satisfied

### Requirement 3.1: Student Attendance Marking via QR Scan
✅ QR scanner component with camera access
✅ Manual 6-digit code entry as fallback
✅ Token verification (handled by backend)
✅ Geolocation capture at time of submission

### Requirement 3.2: Geolocation Capture
✅ High accuracy location request
✅ Location captured before attendance submission
✅ Location accuracy displayed to user
✅ Error handling for location denial

### Requirement 3.3: Distance Calculation
✅ Student and teacher locations sent to backend
✅ Distance displayed in result (handled by backend)

### Requirement 3.4: Radius Validation
✅ Validation performed by backend
✅ Rejection reason displayed to user

### Requirement 3.5: Time Window Validation
✅ Validation performed by backend
✅ Error message displayed if outside time window

## User Experience Flow

### Marking Attendance (QR Code)
1. Student navigates to "Mark Attendance" tab
2. System requests location permission
3. Location is captured and displayed with accuracy
4. Student selects "Scan QR Code" tab
5. Camera permission is requested
6. Camera preview appears with scan box
7. Student positions QR code in scan box
8. QR code is automatically detected and scanned
9. Attendance is submitted with location data
10. Result is displayed (success or failure with reason)
11. Student can click "Try Again" to mark another attendance

### Marking Attendance (Manual Code)
1. Student navigates to "Mark Attendance" tab
2. System requests location permission
3. Location is captured and displayed with accuracy
4. Student selects "Enter Code" tab
5. Student types 6-digit code
6. Character count updates in real-time
7. Submit button enables when 6 digits entered
8. Student clicks "Submit Code"
9. Attendance is submitted with location data
10. Result is displayed (success or failure with reason)
11. Student can click "Try Again" to mark another attendance

### Viewing Attendance History
1. Student navigates to "Attendance History" tab
2. System fetches attendance records
3. Records are displayed in table/card format
4. Student can filter by date range
5. Student can clear filters to see all records
6. Each record shows course, date, time, status, and distance

## Error Handling

### Location Errors
- Permission denied: Clear message with instructions to enable location
- Position unavailable: Message to check device settings
- Timeout: Message to try again
- Retry button available for all location errors

### Camera Errors
- Permission denied: Instructions to enable camera access
- No camera found: Message indicating no camera available
- Camera in use: Message indicating camera is being used by another app

### API Errors
- Network error: Generic network error message
- Validation error: Specific error from backend (e.g., "Outside allowed radius")
- Token expired: Message indicating token has expired
- Duplicate submission: Message indicating attendance already marked

## Styling

All components use Tailwind CSS utility classes for styling:
- Consistent color scheme (blue primary, red error, green success, yellow warning)
- Responsive design (mobile-first approach)
- Accessible focus states
- Loading spinners for async operations
- Status badges with appropriate colors
- Card-based layouts for better visual hierarchy

## Testing Recommendations

### Unit Tests
- QRScanner: Test camera initialization, scan success, error handling
- ManualCodeEntry: Test input validation, paste handling, submission
- ScanPage: Test tab switching, location capture, API calls
- AttendanceHistory: Test data fetching, filtering, empty states

### Integration Tests
- End-to-end flow: Login → Navigate to scan page → Scan QR → View result
- End-to-end flow: Login → Navigate to scan page → Enter code → View result
- End-to-end flow: Login → View attendance history → Apply filters

### Manual Testing Checklist
- [ ] QR scanner opens camera successfully
- [ ] QR code is detected and scanned
- [ ] Manual code entry accepts only digits
- [ ] Manual code entry validates 6 digits
- [ ] Location permission is requested
- [ ] Location is captured with accuracy
- [ ] Attendance submission works with valid token
- [ ] Error messages display for invalid token
- [ ] Error messages display for location issues
- [ ] Attendance history loads correctly
- [ ] Date filters work correctly
- [ ] Status badges display correct colors
- [ ] Mobile responsive design works
- [ ] Tab navigation works smoothly

## Future Enhancements

1. **Offline Support**: Cache attendance submissions when offline and sync when online
2. **Course Filter**: Add course dropdown in attendance history filters
3. **Statistics**: Show attendance percentage and trends
4. **Notifications**: Push notifications for upcoming classes
5. **QR Code History**: Show recently scanned QR codes
6. **Location History**: Show location accuracy trends
7. **Dark Mode**: Add dark mode support
8. **Accessibility**: Add ARIA labels and keyboard navigation
9. **Performance**: Implement virtual scrolling for large attendance history
10. **Analytics**: Track scan success rate and common errors

## Notes

- The html5-qrcode library is already included in package.json
- All components follow React functional component patterns with hooks
- Error handling is comprehensive with user-friendly messages
- The implementation is fully responsive and mobile-friendly
- Location accuracy is displayed to help users understand location quality
- Device information is captured for fraud detection purposes
- The interface prevents submission without valid location data
- All API calls include proper error handling and loading states
