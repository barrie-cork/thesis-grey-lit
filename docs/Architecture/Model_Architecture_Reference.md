# 🏗️ Django Grey Literature Review Platform - Architecture Reference

## 📋 **Model Architecture & Field Definitions**

> **Critical Note**: Always use the **NEW FIELD NAMES** (marked with ✅). Old field names have been deprecated and will cause errors.

---

## 🔑 **Core Models Overview**

| Model | App | Purpose | Key Relationships |
|-------|-----|---------|-------------------|
| `User` | accounts | Custom authentication | Base for all user relationships |
| `SearchSession` | review_manager | Literature review sessions | Created by User |
| `SessionActivity` | review_manager | Activity audit trail | Links Session + User |
| `SessionStatusHistory` | review_manager | Status change tracking | Links Session + User |
| `SessionArchive` | review_manager | Archive management | Links Session + User |
| `UserSessionStats` | review_manager | User productivity metrics | OneToOne with User |

---

## 👤 **User Model (accounts.User)**

### **Field Definitions**
| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `id` | UUIDField | PK, auto-generated | Unique identifier |
| `username` | CharField | unique, max_length=150 | Login username |
| `email` | EmailField | unique, nullable | Optional email |
| `first_name` | CharField | max_length=150, blank | User's first name |
| `last_name` | CharField | max_length=150, blank | User's last name |
| `is_active` | BooleanField | default=True | Account status |
| `is_staff` | BooleanField | default=False | Admin access |
| `is_superuser` | BooleanField | default=False | Full permissions |
| `created_at` ✅ | DateTimeField | auto_now_add | Account creation |
| `updated_at` ✅ | DateTimeField | auto_now | Last update |

### **Development Rules**
```python
# ✅ CORRECT - Always use this
from django.contrib.auth import get_user_model
User = get_user_model()

# ❌ NEVER DO THIS
from django.contrib.auth.models import User  # Will break!

# ✅ CORRECT - Foreign keys
created_by = models.ForeignKey(settings.AUTH_USER_MODEL, ...)
```

---

## 📝 **SearchSession Model (review_manager.SearchSession)**

### **Field Definitions**
| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `id` | UUIDField | PK, auto-generated | Unique identifier |
| `title` | CharField | max_length=200, required | Session title |
| `description` | TextField | blank=True | Optional description |
| `status` | CharField | choices=Status, default='draft' | Workflow status |
| `visibility` | CharField | choices=Visibility, default='private' | Access control |
| `permissions` | JSONField | default=dict | Permission settings |
| `created_by` | ForeignKey | → User, CASCADE | Session owner |
| `updated_by` | ForeignKey | → User, SET_NULL, nullable | Last editor |
| `created_at` ✅ | DateTimeField | auto_now_add | Creation time |
| `updated_at` ✅ | DateTimeField | auto_now | Last update |
| `start_date` | DateTimeField | nullable | When started |
| `completed_date` | DateTimeField | nullable | When completed |

### **Status Workflow**
| Status | Next Allowed | Description |
|--------|--------------|-------------|
| `draft` | strategy_ready | Initial creation |
| `strategy_ready` | executing, draft | Ready for search execution |
| `executing` | processing, failed | Searches running |
| `processing` | ready_for_review, failed | Processing results |
| `ready_for_review` | in_review | Results ready |
| `in_review` | completed, ready_for_review | Under review |
| `completed` | archived, in_review | Review complete |
| `failed` | draft, strategy_ready | Error state |
| `archived` | completed | Long-term storage |

### **Key Methods**
```python
session.can_transition_to('new_status')  # Validate transitions
session.can_be_deleted()                 # Only draft sessions
session.can_be_archived()                # Only completed sessions
session.can_be_duplicated()              # Any non-draft status
```

---

## 📊 **SessionActivity Model (review_manager.SessionActivity)**

### **Field Definitions** ⚠️ **CRITICAL: Use NEW field names**
| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `id` | UUIDField | PK, auto-generated | Unique identifier |
| `session` | ForeignKey | → SearchSession, CASCADE | Related session |
| `action` ✅ | CharField | max_length=50 | **NEW: Activity type** |
| `description` | TextField | blank=True | Activity details |
| `old_status` | CharField | choices=Status, nullable | Previous status |
| `new_status` | CharField | choices=Status, nullable | New status |
| `user` ✅ | ForeignKey | → User, PROTECT | **NEW: User who acted** |
| `timestamp` ✅ | DateTimeField | auto_now_add | **NEW: When occurred** |
| `details` ✅ | JSONField | default=dict | **NEW: Structured metadata** |

### **⚠️ DEPRECATED Fields (DO NOT USE)**
| ❌ Old Field | ✅ New Field | Migration Status |
|-------------|-------------|------------------|
| ~~`activity_type`~~ | `action` | **REMOVED** |
| ~~`performed_by`~~ | `user` | **REMOVED** |
| ~~`performed_at`~~ | `timestamp` | **REMOVED** |
| ~~`metadata`~~ | `details` | **REMOVED** |

### **Activity Types**
| Type | Purpose |
|------|---------|
| `CREATED` | Session created |
| `STATUS_CHANGED` | Status transition |
| `MODIFIED` | Session updated |
| `STRATEGY_DEFINED` | Search strategy set |
| `SEARCH_EXECUTED` | Search run |
| `RESULTS_PROCESSED` | Results processed |
| `REVIEW_STARTED` | Review begun |
| `REVIEW_COMPLETED` | Review finished |
| `ERROR` | Error occurred |
| `ERROR_RECOVERY` | Recovery attempt |

### **Usage Examples**
```python
# ✅ CORRECT - Use new field names
SessionActivity.objects.create(
    session=session,
    action='CREATED',               # NEW field name
    user=request.user,              # NEW field name
    description='Session created',
    timestamp=timezone.now()        # NEW field name (auto-set)
)

# ✅ CORRECT - Convenience method
SessionActivity.log_activity(
    session=session,
    action='STATUS_CHANGED',
    description='Status updated',
    user=request.user,
    old_status='draft',
    new_status='strategy_ready'
)

# ❌ NEVER USE OLD FIELDS
SessionActivity.objects.create(
    activity_type='CREATED',        # BROKEN!
    performed_by=request.user,      # BROKEN!
    performed_at=timezone.now()     # BROKEN!
)
```

---

## 📈 **SessionStatusHistory Model (review_manager.SessionStatusHistory)**

### **Field Definitions**
| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `id` | UUIDField | PK, auto-generated | Unique identifier |
| `session` | ForeignKey | → SearchSession, CASCADE | Related session |
| `from_status` | CharField | choices=Status, blank | Previous status |
| `to_status` | CharField | choices=Status | New status |
| `changed_by` | ForeignKey | → User, PROTECT | User who changed |
| `changed_at` | DateTimeField | auto_now_add | When changed |
| `reason` | TextField | blank=True | Optional reason |
| `metadata` | JSONField | default=dict | Additional context |
| `ip_address` | GenericIPAddressField | nullable | Source IP |
| `duration_in_previous_status` | DurationField | nullable | Time in previous |

---

## 🗄️ **SessionArchive Model (review_manager.SessionArchive)**

### **Field Definitions**
| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `id` | UUIDField | PK, auto-generated | Unique identifier |
| `session` | OneToOneField | → SearchSession, CASCADE | Archived session |
| `archived_by` | ForeignKey | → User, PROTECT | Who archived |
| `archived_at` | DateTimeField | auto_now_add | When archived |
| `archive_reason` | TextField | blank=True | Why archived |
| `stats_snapshot` | JSONField | default=dict | Stats at archive time |
| `restored_at` | DateTimeField | nullable | When restored |
| `restored_by` | ForeignKey | → User, SET_NULL | Who restored |

---

## 📊 **UserSessionStats Model (review_manager.UserSessionStats)**

### **Field Definitions**
| Field | Type | Constraints | Purpose |
|-------|------|-------------|---------|
| `id` | UUIDField | PK, auto-generated | Unique identifier |
| `user` | OneToOneField | → User, CASCADE | User these stats belong to |
| `total_sessions` | PositiveIntegerField | default=0 | Total sessions created |
| `completed_sessions` | PositiveIntegerField | default=0 | Sessions completed |
| `archived_sessions` | PositiveIntegerField | default=0 | Sessions archived |
| `failed_sessions` | PositiveIntegerField | default=0 | Sessions failed |
| `avg_completion_time` | DurationField | nullable | Average completion time |
| `fastest_completion` | DurationField | nullable | Fastest completion |
| `total_activities` | PositiveIntegerField | default=0 | Total activities |
| `last_activity_date` | DateTimeField | nullable | Last activity |
| `completion_rate` | FloatField | default=0.0 | Completion percentage |
| `productivity_score` | FloatField | default=0.0 | Productivity score (0-100) |
| `stats_calculated_at` | DateTimeField | auto_now | Last calculation |
| `notification_preferences` | JSONField | default=dict | User preferences |

---

## 🔗 **Relationship Map**

```
User (accounts.User)
├── created_sessions → SearchSession.created_by
├── updated_sessions → SearchSession.updated_by
├── session_activities → SessionActivity.user
├── status_changes → SessionStatusHistory.changed_by
├── archived_sessions → SessionArchive.archived_by
├── restored_sessions → SessionArchive.restored_by
└── session_stats → UserSessionStats.user

SearchSession (review_manager.SearchSession)
├── activities → SessionActivity.session
├── status_history → SessionStatusHistory.session
└── archive_info → SessionArchive.session
```

---

## ⚙️ **Database Indexes & Performance**

### **Strategic Indexing**
| Model | Index Fields | Purpose |
|-------|-------------|---------|
| SearchSession | `[created_by, status]` | User dashboard queries |
| SearchSession | `[created_at]`, `[updated_at]`, `[status]` | Sorting & filtering |
| SessionActivity | `[session, timestamp]` | Activity timeline |
| SessionActivity | `[action, timestamp]` | Activity type filtering |
| SessionActivity | `[user, timestamp]` | User activity history |
| SessionStatusHistory | `[session, -changed_at]` | Status timeline |
| SessionStatusHistory | `[from_status, to_status]` | Transition analysis |

---

## 🚨 **Development Guidelines**

### **✅ DO**
- Always use `get_user_model()` for User references
- Use `settings.AUTH_USER_MODEL` in ForeignKeys
- Use NEW field names: `action`, `user`, `timestamp`, `details`
- Test with the custom User model
- Follow UUID primary key pattern
- Use convenience methods like `SessionActivity.log_activity()`

### **❌ DON'T**
- Import `from django.contrib.auth.models import User`
- Use old field names: `activity_type`, `performed_by`, `performed_at`, `metadata`
- Hardcode `auth.User` anywhere
- Create migrations without considering custom User model
- Skip testing with actual User model

---

## 🧪 **Testing Patterns**

### **User Model Setup**
```python
from django.contrib.auth import get_user_model
User = get_user_model()

# Create test user
user = User.objects.create_user(
    username='testuser',
    email='test@example.com',
    password='testpass123'
)
```

### **Activity Logging Test**
```python
# Test new field names
activity = SessionActivity.objects.latest('timestamp')  # ✅ NEW
self.assertEqual(activity.action, 'CREATED')             # ✅ NEW
self.assertEqual(activity.user, self.user)               # ✅ NEW
```

---

## 📚 **Component Status**

| Component | Status | Test Coverage |
|-----------|--------|---------------|
| User Model | ✅ Production Ready | 100% |
| SearchSession | ✅ Production Ready | 100% |
| SessionActivity | ✅ Production Ready | 100% |
| SessionStatusHistory | ✅ Production Ready | 100% |
| SessionArchive | ✅ Production Ready | 100% |
| UserSessionStats | ✅ Production Ready | 100% |

---

**📅 Last Updated**: May 30, 2025  
**🔄 Migration Status**: Complete - All field migrations applied  
**🧪 Test Status**: All tests passing with new field names  
**🚀 Production Status**: Ready for deployment
