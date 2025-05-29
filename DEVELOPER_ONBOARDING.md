# 🚀 Developer Onboarding Checklist

## 📋 **Pre-Development Setup**

### **Step 1: Critical Architecture Awareness**
- [ ] **READ:** `CUSTOM_USER_ALERT.md` - **MANDATORY** before any coding
- [ ] **READ:** `apps/accounts/README.md` - Understand the custom User model
- [ ] **READ:** `docs/PRD.md` - Understand overall project architecture
- [ ] **UNDERSTAND:** This project uses `accounts.User`, NOT `auth.User`

### **Step 2: Environment Setup**
- [ ] Python 3.12+ installed
- [ ] Virtual environment created and activated
- [ ] Dependencies installed: `pip install -r requirements.txt`
- [ ] Database configured and migrated: `python manage.py migrate`
- [ ] Admin user created: `python manage.py createsuperuser`

### **Step 3: Architecture Understanding**
- [ ] **Review Manager app:** Session management and dashboard
- [ ] **Accounts app:** Custom User model with UUID primary keys
- [ ] **Future apps:** Search Strategy, SERP Execution, Results Management
- [ ] **Django 4.2:** Framework version and best practices

### **Step 4: Working Example Review**
- [ ] Examine `apps/review_manager/` as reference implementation
- [ ] Study `apps/review_manager/tests.py` for correct User model usage
- [ ] Run tests: `python manage.py test apps.review_manager`
- [ ] Create sample data: `python manage.py create_sample_sessions --count 10`

### **Step 5: Development Verification**
- [ ] Access admin panel: http://localhost:8000/admin/
- [ ] Access dashboard: http://localhost:8000/review/
- [ ] Create a test session through the UI
- [ ] Verify all functionality works correctly

---

## 🚨 **Critical "DO NOT" List**

### **❌ NEVER Do These:**
- [ ] Import `from django.contrib.auth.models import User`
- [ ] Use `User` directly in models without `settings.AUTH_USER_MODEL`
- [ ] Hardcode `auth.User` anywhere in the codebase
- [ ] Create migrations without considering the custom User model
- [ ] Skip reading the `CUSTOM_USER_ALERT.md` document

### **✅ ALWAYS Do These:**
- [ ] Use `from django.contrib.auth import get_user_model`
- [ ] Use `settings.AUTH_USER_MODEL` in model ForeignKeys
- [ ] Test with the actual custom User model
- [ ] Follow patterns from `apps/review_manager/`
- [ ] Ask questions if uncertain about User model usage

---

## 📚 **Required Reading Order**

1. **`CUSTOM_USER_ALERT.md`** - Critical architecture alert
2. **`apps/accounts/README.md`** - Custom User model details
3. **`docs/PRD.md`** - Project overview and architecture
4. **`apps/review_manager/README.md`** - Working example implementation
5. **`docs/features/review-manager/review-manager-prd.md`** - Detailed specifications

---

## 🧪 **Verification Commands**

Run these commands to verify correct setup:

```bash
# Check Django installation
python manage.py check

# Run existing tests (should all pass)
python manage.py test apps.review_manager

# Create sample data
python manage.py create_sample_sessions --count 5 --username developer

# Start development server
python manage.py runserver
```

---

## 🔍 **Code Review Checklist**

Before submitting any PR, ensure:

- [ ] No `from django.contrib.auth.models import User` imports
- [ ] All User references use `get_user_model()`
- [ ] ForeignKeys to User use `settings.AUTH_USER_MODEL`
- [ ] Tests create users with `User = get_user_model()`
- [ ] All tests pass: `python manage.py test`
- [ ] No hardcoded references to `auth.User`

---

## 🆘 **Common Issues & Solutions**

### **Error: "Manager isn't available; 'auth.User' has been swapped"**
**Solution:** Replace `User` import with `get_user_model()`

### **Error: "Cannot assign User instance"**
**Solution:** Use `settings.AUTH_USER_MODEL` in model ForeignKeys

### **Tests failing with User model errors**
**Solution:** Check test setup uses `get_user_model()`

---

## 👥 **Team Communication**

- **Questions?** Ask in the development channel
- **Found issues?** Create tickets with "User Model" label
- **Need examples?** Reference `apps/review_manager/`
- **Architecture changes?** Discuss with team lead first

---

**🎯 Goal:** Ensure every developer understands and correctly implements the custom User model from day one!
