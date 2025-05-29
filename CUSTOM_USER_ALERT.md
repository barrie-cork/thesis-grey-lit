# 🚨 CRITICAL: Custom User Model Alert

## ⚠️ **MUST READ BEFORE DEVELOPMENT**

This project uses a **CUSTOM USER MODEL** instead of Django's default `auth.User`. This is a **critical architectural decision** that affects **ALL** development work.

---

## 🎯 **Key Information**

### **Custom User Model Details:**
- **Model:** `accounts.User` (not `auth.User`)
- **Primary Key:** UUID (not integer)
- **Location:** `apps/accounts/models.py`
- **Setting:** `AUTH_USER_MODEL = 'accounts.User'`

### **Why This Matters:**
- ❌ **NEVER use** `from django.contrib.auth.models import User`
- ✅ **ALWAYS use** `from django.contrib.auth import get_user_model`
- ❌ **NEVER hardcode** `auth.User` in models or forms
- ✅ **ALWAYS use** `settings.AUTH_USER_MODEL` in ForeignKeys

---

## 🛠️ **Correct Implementation Patterns**

### **✅ Correct Way - Views & Tests:**
```python
from django.contrib.auth import get_user_model

User = get_user_model()

# In views
def my_view(request):
    user = User.objects.create_user(username='test', password='pass')

# In tests
class MyTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
```

### **✅ Correct Way - Models:**
```python
from django.conf import settings

class MyModel(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ✅ Correct
        on_delete=models.CASCADE
    )
```

### **❌ Wrong Way (Will Break):**
```python
from django.contrib.auth.models import User  # ❌ WRONG!

class MyModel(models.Model):
    user = models.ForeignKey(
        User,  # ❌ Will cause errors
        on_delete=models.CASCADE
    )
```

---

## 🔍 **Common Error Symptoms**

If you see these errors, you're likely using the wrong User model:

```
AttributeError: Manager isn't available; 'auth.User' has been swapped for 'accounts.User'
```

```
ValueError: Cannot assign "<User: username>": "MyModel.user" must be a "accounts.User" instance.
```

---

## ✅ **Quick Reference Checklist**

Before committing any code that involves users:

- [ ] Used `get_user_model()` instead of importing `User`
- [ ] Used `settings.AUTH_USER_MODEL` in model ForeignKeys
- [ ] Tested with the custom User model
- [ ] No hardcoded references to `auth.User`

---

## 🧪 **Testing Requirements**

All tests **MUST** use the custom User model:

```python
from django.contrib.auth import get_user_model

User = get_user_model()

class MyTestCase(TestCase):
    def setUp(self):
        # ✅ Correct - will work with custom User
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'  # Optional in our model
        )
```

---

## 📚 **References**

- **Accounts App README:** `apps/accounts/README.md`
- **Django Docs:** https://docs.djangoproject.com/en/4.2/topics/auth/customizing/#using-a-custom-user-model-when-starting-a-project
- **Settings File:** `thesis_grey_project/settings/base.py` (search for `AUTH_USER_MODEL`)

---

## 🆘 **Need Help?**

If you encounter User model issues:
1. Check this document first
2. Review the Review Manager app implementation (`apps/review_manager/`)
3. Look at working test examples in `apps/review_manager/tests.py`
4. Ask the team lead

---

**⚠️ Remember: Using the wrong User model will cause database errors and broken functionality!**
