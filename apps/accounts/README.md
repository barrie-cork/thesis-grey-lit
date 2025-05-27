# Accounts App

Part of the Thesis Grey Django project.

## 📦 Purpose
The `accounts` app provides the authentication system for Thesis Grey, allowing researchers to register, log in, manage their profiles, and reset passwords. It implements a custom User model with UUID primary keys for compatibility with the Prisma schema reference.

## 📁 Key Files
- `models.py`: Custom User model extending Django's AbstractUser with UUID primary key
- `views.py`: Authentication views (SignUpView, ProfileView)
- `forms.py`: Custom forms for registration and profile management
- `urls.py`: App-level URL routing for authentication endpoints
- `admin.py`: Custom UserAdmin configuration for Django admin
- `templates/accounts/`: Authentication-specific templates

## ✅ Setup Notes
This app is included in `INSTALLED_APPS` as `apps.accounts`.

The custom User model is configured as `AUTH_USER_MODEL = 'accounts.User'` in settings.

## 🛠 Development Tasks
- [x] Create custom User model with UUID primary key
- [x] Configure AUTH_USER_MODEL in settings
- [x] Set up UserAdmin for Django admin
- [ ] Implement forms (SignUpForm, ProfileForm)
- [ ] Create authentication views
- [ ] Design templates for login, signup, profile
- [ ] Configure URL routing
- [ ] Write unit and integration tests

## 🔗 Related Apps
- `review_manager`: Users' review sessions are displayed on the dashboard after login
- All other apps depend on this app for user authentication and authorization

## 📝 Model Structure
```python
User
├── id (UUID, primary key)
├── username (required, unique)
├── email (optional, unique if provided)
├── password (hashed)
├── first_name (optional)
├── last_name (optional)
├── is_active (default: True)
├── is_staff (default: False)
├── is_superuser (default: False)
├── created_at (auto, maps to 'createdAt' in DB)
├── updated_at (auto, maps to 'updatedAt' in DB)
└── last_login (nullable)
```

## 🔒 Security Features
- Password minimum 8 characters
- Django's built-in password validators
- CSRF protection on all forms
- Session-based authentication
- Optional email field with uniqueness constraint 