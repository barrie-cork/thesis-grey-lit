# Review Manager API Documentation

**Version:** 1.0.0  
**Base URL:** `/review/`  
**Authentication:** Django Session Authentication Required  

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Core HTTP Endpoints](#core-http-endpoints)
- [AJAX API Endpoints](#ajax-api-endpoints)
- [Real-time API Endpoints](#real-time-api-endpoints)
- [Security Features](#security-features)
- [Response Formats](#response-formats)
- [Error Handling](#error-handling)
- [Rate Limiting](#rate-limiting)
- [Examples](#examples)

## Overview

The Review Manager API provides comprehensive endpoints for managing systematic literature review sessions. All endpoints require authentication and implement ownership-based access control.

### API Categories

1. **Core HTTP Endpoints**: Traditional Django views for CRUD operations
2. **AJAX API Endpoints**: JSON-based endpoints for dynamic interactions
3. **Real-time API Endpoints**: Live status monitoring and notifications
4. **Security Endpoints**: Authentication and permission validation

## Authentication

All API endpoints require user authentication via Django's session authentication system.

### Authentication Headers

```http
Cookie: sessionid=your_session_id
X-CSRFToken: your_csrf_token  # Required for state-changing operations
```

### Permission Model

- **Ownership**: Users can only access sessions they created
- **Status-based**: Actions are restricted based on session status
- **Rate-limited**: Sensitive operations have configurable rate limits

## Core HTTP Endpoints

### Session Management

#### Dashboard View
```http
GET /review/
```

**Description**: Main dashboard showing user's sessions with filtering and pagination.

**Query Parameters**:
- `status` (string): Filter by session status
- `search` (string): Search in title and description
- `page` (integer): Page number for pagination

**Response**: HTML template with session data

**Security**: Login required, shows only user's sessions

---

#### Create Session
```http
GET /review/create/
POST /review/create/
```

**Description**: Create a new session with title and description.

**POST Request Body**:
```json
{
  "title": "Session Title (max 200 chars)",
  "description": "Optional description (max 1000 chars)"
}
```

**Response**: 
- GET: HTML form template
- POST: Redirect to session detail or form with errors

**Security**: Login required, CSRF protection

---

#### Session Detail
```http
GET /review/session/{session_id}/
```

**Description**: View detailed information about a specific session.

**URL Parameters**:
- `session_id` (UUID): Session identifier

**Response**: HTML template with session details, activities, and analytics

**Security**: Login required, ownership validation

---

#### Edit Session
```http
GET /review/session/{session_id}/edit/
POST /review/session/{session_id}/edit/
```

**Description**: Edit session title and description.

**POST Request Body**:
```json
{
  "title": "Updated Title",
  "description": "Updated description"
}
```

**Response**:
- GET: HTML form template
- POST: Redirect to session detail or form with errors

**Security**: Login required, ownership validation, status restrictions

---

#### Delete Session
```http
POST /review/session/{session_id}/delete/
```

**Description**: Delete a session (draft status only).

**Response**: Redirect to dashboard with success message

**Security**: Login required, ownership validation, draft status only

---

#### Duplicate Session
```http
POST /review/session/{session_id}/duplicate/
```

**Description**: Create a copy of an existing session.

**Response**: Redirect to new session detail

**Security**: Login required, ownership validation

### Advanced Features

#### Activity Timeline
```http
GET /review/session/{session_id}/activity-timeline/
```

**Description**: View chronological activity timeline for a session.

**Query Parameters**:
- `activity_type` (string): Filter by activity type
- `date_from` (date): Start date filter
- `date_to` (date): End date filter
- `page` (integer): Page number

**Response**: HTML template with paginated activity list

**Security**: Login required, ownership validation

---

#### Status History
```http
GET /review/session/{session_id}/status-history/
```

**Description**: View detailed status change history.

**Response**: HTML template with status transition timeline

**Security**: Login required, ownership validation

---

#### Archive Management
```http
GET /review/archive-management/
POST /review/session/{session_id}/archive/
POST /review/session/{session_id}/unarchive/
POST /review/bulk-archive/
```

**Description**: Archive and unarchive sessions.

**POST Request Body** (bulk-archive):
```json
{
  "session_ids": ["uuid1", "uuid2", "uuid3"]
}
```

**Response**: HTML template or redirect with status message

**Security**: Login required, ownership validation

---

#### Analytics Dashboard
```http
GET /review/analytics/
```

**Description**: User productivity analytics and statistics.

**Response**: HTML template with charts and metrics

**Security**: Login required, user-specific data only

## AJAX API Endpoints

### User Statistics

#### Get User Stats
```http
GET /review/ajax/user-stats/
```

**Description**: Get current user's session statistics.

**Response**:
```json
{
  "success": true,
  "data": {
    "total_sessions": 45,
    "active_sessions": 12,
    "completed_sessions": 30,
    "completion_rate": 85.7,
    "productivity_score": 92,
    "average_session_duration": "14 days",
    "sessions_this_month": 8,
    "recent_activity_count": 15
  },
  "timestamp": "2024-01-01T12:00:00Z"
}
```

**Security**: Login required, rate limited

---

#### Activity Timeline AJAX
```http
GET /review/ajax/activity-timeline/{session_id}/
```

**Description**: Get paginated activity timeline data.

**Query Parameters**:
- `page` (integer): Page number
- `activity_type` (string): Filter by type
- `limit` (integer): Items per page (max 50)

**Response**:
```json
{
  "success": true,
  "data": {
    "activities": [
      {
        "id": "uuid",
        "action": "CREATED",
        "description": "Session created",
        "timestamp": "2024-01-01T12:00:00Z",
        "user": "username",
        "details": {}
      }
    ],
    "pagination": {
      "page": 1,
      "total_pages": 5,
      "total_items": 47,
      "has_next": true,
      "has_previous": false
    }
  }
}
```

**Security**: Login required, ownership validation

---

#### Delete Activity
```http
DELETE /review/ajax/delete-activity/{activity_id}/
```

**Description**: Delete a specific activity (corrections only).

**Response**:
```json
{
  "success": true,
  "message": "Activity deleted successfully"
}
```

**Security**: Login required, ownership validation, audit logging

---

#### Export Session Data
```http
GET /review/ajax/export-session-data/{session_id}/
```

**Description**: Export session data in JSON format.

**Response**:
```json
{
  "success": true,
  "data": {
    "session": {
      "id": "uuid",
      "title": "Session Title",
      "status": "completed",
      "created_at": "2024-01-01T12:00:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    "activities": [...],
    "status_history": [...],
    "statistics": {...}
  },
  "export_timestamp": "2024-01-01T12:00:00Z"
}
```

**Security**: Login required, ownership validation

---

#### Productivity Chart Data
```http
GET /review/ajax/productivity-chart-data/
```

**Description**: Get data for productivity visualization charts.

**Query Parameters**:
- `period` (string): 'week', 'month', 'quarter', 'year'
- `chart_type` (string): 'activity', 'completion', 'status'

**Response**:
```json
{
  "success": true,
  "data": {
    "labels": ["Week 1", "Week 2", "Week 3", "Week 4"],
    "datasets": [
      {
        "label": "Sessions Created",
        "data": [3, 5, 2, 7],
        "backgroundColor": "#007bff"
      },
      {
        "label": "Sessions Completed", 
        "data": [2, 4, 3, 5],
        "backgroundColor": "#28a745"
      }
    ]
  }
}
```

**Security**: Login required, user-specific data

## Real-time API Endpoints

### Status Monitoring

#### Status Check API
```http
GET /review/api/status-check/
```

**Description**: Check real-time status of user's active sessions.

**Query Parameters**:
- `session_ids` (string): Comma-separated UUIDs (optional)
- `include_progress` (boolean): Include progress indicators

**Response**:
```json
{
  "success": true,
  "data": {
    "sessions": [
      {
        "id": "uuid",
        "status": "executing",
        "progress": 45,
        "estimated_completion": "2024-01-01T15:30:00Z",
        "last_activity": "2024-01-01T12:00:00Z"
      }
    ],
    "system_status": "healthy",
    "last_check": "2024-01-01T12:00:00Z"
  }
}
```

**Security**: Login required, ownership validation

---

#### System Health Check
```http
GET /review/api/system-health/
```

**Description**: Check overall system health and performance.

**Response**:
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "database": "connected",
    "cache": "available",
    "response_time_ms": 45,
    "active_sessions": 1247,
    "version": "1.0.0"
  }
}
```

**Security**: Login required

---

#### Simulate Progress Update
```http
POST /review/api/simulate-progress/
```

**Description**: Simulate progress updates for testing (development only).

**Request Body**:
```json
{
  "session_id": "uuid",
  "progress": 75,
  "status": "processing"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Progress updated"
}
```

**Security**: Development mode only

### Notifications

#### Notification Preferences
```http
GET /review/api/notification-preferences/
POST /review/api/notification-preferences/
```

**Description**: Get or update user notification preferences.

**POST Request Body**:
```json
{
  "email_notifications": true,
  "browser_notifications": true,
  "sound_enabled": false,
  "auto_dismiss_time": 5000,
  "notification_types": ["status_change", "error", "completion"]
}
```

**GET Response**:
```json
{
  "success": true,
  "data": {
    "email_notifications": true,
    "browser_notifications": true,
    "sound_enabled": false,
    "auto_dismiss_time": 5000,
    "notification_types": ["status_change", "error", "completion"]
  }
}
```

**Security**: Login required, user-specific settings

---

#### Get Notification Preferences
```http
GET /review/api/notification-preferences/get/
```

**Description**: Get current notification preferences.

**Response**: Same as GET notification-preferences

**Security**: Login required

### Error Recovery

#### Error Recovery API
```http
POST /review/api/error-recovery/
```

**Description**: Trigger error recovery for failed sessions.

**Request Body**:
```json
{
  "session_id": "uuid",
  "recovery_action": "retry_last_operation",
  "additional_params": {}
}
```

**Response**:
```json
{
  "success": true,
  "data": {
    "recovery_id": "uuid",
    "action_taken": "retry_last_operation",
    "estimated_completion": "2024-01-01T12:15:00Z"
  }
}
```

**Security**: Login required, ownership validation

---

#### Get Recovery Options
```http
GET /review/session/{session_id}/recovery-options/
```

**Description**: Get available recovery options for a failed session.

**Response**:
```json
{
  "success": true,
  "data": {
    "available_actions": [
      {
        "action": "retry_last_operation",
        "description": "Retry the last failed operation",
        "estimated_duration": "5 minutes"
      },
      {
        "action": "reset_to_previous_status",
        "description": "Reset session to previous working status",
        "estimated_duration": "1 minute"
      }
    ],
    "session_status": "failed",
    "last_error": "Connection timeout during search execution"
  }
}
```

**Security**: Login required, ownership validation

## Security Features

### CSRF Protection

All POST, PUT, DELETE requests require CSRF token:

```http
X-CSRFToken: your_csrf_token
```

### Rate Limiting

Default limits (configurable):
- General API calls: 60 requests/hour
- Sensitive operations: 10 requests/hour
- Status checks: 240 requests/hour

Rate limit headers:
```http
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1641024000
```

### Security Headers

All responses include:
```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

### Audit Logging

All API calls are logged with:
- User ID and session
- IP address and user agent
- Request method and endpoint
- Request/response data (sanitized)
- Timestamp and duration

## Response Formats

### Success Response

```json
{
  "success": true,
  "data": { ... },
  "messages": ["Optional success messages"],
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "unique_request_id"
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": { ... },
    "retry_after": 60  // Optional: seconds to wait before retry
  },
  "timestamp": "2024-01-01T12:00:00Z",
  "request_id": "unique_request_id"
}
```

### Common Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `AUTHENTICATION_REQUIRED` | 401 | User not authenticated |
| `PERMISSION_DENIED` | 403 | Insufficient permissions |
| `NOT_FOUND` | 404 | Resource not found |
| `VALIDATION_ERROR` | 400 | Invalid request data |
| `RATE_LIMITED` | 429 | Too many requests |
| `SESSION_NOT_FOUND` | 404 | Session doesn't exist |
| `INVALID_STATUS` | 400 | Invalid status transition |
| `OPERATION_FAILED` | 500 | Internal server error |

## Error Handling

### Validation Errors

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "title": ["This field is required"],
      "description": ["Ensure this value has at most 1000 characters"]
    }
  }
}
```

### Permission Errors

```json
{
  "success": false,
  "error": {
    "code": "PERMISSION_DENIED",
    "message": "You don't have permission to access this session",
    "details": {
      "session_id": "uuid",
      "required_permission": "owner"
    }
  }
}
```

### Rate Limit Errors

```json
{
  "success": false,
  "error": {
    "code": "RATE_LIMITED",
    "message": "Too many requests. Please try again later.",
    "details": {
      "limit": 60,
      "window": 3600,
      "retry_after": 300
    }
  }
}
```

## Examples

### Create a Session

```bash
curl -X POST http://localhost:8000/review/create/ \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -H "X-CSRFToken: your_csrf_token" \
  -d "title=My New Review&description=A systematic review of..."
```

### Get User Statistics

```bash
curl -X GET http://localhost:8000/review/ajax/user-stats/ \
  -H "X-Requested-With: XMLHttpRequest" \
  -b "sessionid=your_session_id"
```

### Check Session Status

```bash
curl -X GET "http://localhost:8000/review/api/status-check/?session_ids=uuid1,uuid2" \
  -H "Accept: application/json" \
  -b "sessionid=your_session_id"
```

### Update Notification Preferences

```bash
curl -X POST http://localhost:8000/review/api/notification-preferences/ \
  -H "Content-Type: application/json" \
  -H "X-CSRFToken: your_csrf_token" \
  -d '{"email_notifications": true, "auto_dismiss_time": 3000}'
```

### Export Session Data

```bash
curl -X GET http://localhost:8000/review/ajax/export-session-data/uuid/ \
  -H "Accept: application/json" \
  -b "sessionid=your_session_id" \
  -o session_export.json
```

## Integration Examples

### JavaScript Integration

```javascript
// Check session status
async function checkSessionStatus(sessionIds) {
  const response = await fetch('/review/api/status-check/', {
    method: 'GET',
    headers: {
      'X-Requested-With': 'XMLHttpRequest',
    },
    credentials: 'include'
  });
  
  if (response.ok) {
    const data = await response.json();
    return data.data.sessions;
  }
  throw new Error('Failed to check status');
}

// Create session
async function createSession(title, description) {
  const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
  
  const response = await fetch('/review/create/', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrfToken,
    },
    body: new URLSearchParams({
      title: title,
      description: description
    }),
    credentials: 'include'
  });
  
  return response.ok;
}
```

### Python Integration

```python
import requests

class ReviewManagerAPI:
    def __init__(self, base_url, session_id):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.cookies.set('sessionid', session_id)
    
    def get_user_stats(self):
        response = self.session.get(f'{self.base_url}/ajax/user-stats/')
        response.raise_for_status()
        return response.json()['data']
    
    def create_session(self, title, description):
        # First get CSRF token
        csrf_response = self.session.get(f'{self.base_url}/create/')
        csrf_token = csrf_response.cookies.get('csrftoken')
        
        response = self.session.post(
            f'{self.base_url}/create/',
            data={'title': title, 'description': description},
            headers={'X-CSRFToken': csrf_token}
        )
        return response.status_code == 302  # Redirect on success
```

---

**Last Updated:** 2025-05-30  
**API Version:** 1.0.0  
**Documentation Status:** ✅ Complete