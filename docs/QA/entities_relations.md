You are a senior software engineer with deep expertise in Django and code analysis. Your task is to review two JSON files, `entities.json` and `relations.json`, which were generated to represent components and their relationships within a Django project's `accounts` application.

**Context of the Django `accounts` application:**

*   **Models (`apps/accounts/models.py`):** Contains a custom `User` model (`accounts.User`) extending `AbstractUser` with a UUID primary key, optional unique email, and custom `created_at`/`updated_at` timestamps.
*   **Forms (`apps/accounts/forms.py`):**
    *   `SignUpForm`: Extends `UserCreationForm`, includes email.
    *   `ProfileForm`: Extends `UserChangeForm`, for email, first_name, last_name updates.
    *   `CustomAuthenticationForm`: Extends `AuthenticationForm`, allows login with username or email, includes a "remember me" checkbox.
*   **Views (`apps/accounts/views.py`):**
    *   `SignUpView` (CreateView): Uses `SignUpForm`, template `accounts/signup.html`, redirects to `accounts:profile`.
    *   `ProfileView` (UpdateView, LoginRequiredMixin): Uses `ProfileForm`, model `User`, template `accounts/profile.html`, redirects to `accounts:profile`.
    *   `CustomLoginView` (LoginView): Uses `CustomAuthenticationForm`, template `accounts/login.html`. Handles "remember me" logic to set session expiry.
    *   `CustomLogoutView` (LogoutView): Redirects to `accounts:login`.
    *   Password Reset Views (`CustomPasswordResetView`, `CustomPasswordResetDoneView`, `CustomPasswordResetConfirmView`, `CustomPasswordResetCompleteView`): Extend corresponding Django auth views, use templates in `accounts/` (e.g., `password_reset.html`, `password_reset_email.html`, `password_reset_subject.txt`).
*   **URLs (`apps/accounts/urls.py`):** Standard named URLs for signup, login, logout, profile, and the full password reset flow, all pointing to the custom views.
*   **Templates (`apps/accounts/templates/accounts/`):** HTML templates for each view (e.g., `login.html`, `signup.html`, `profile.html`, `password_reset.html`, etc.) and text/HTML templates for password reset emails.
*   **Settings:**
    *   `AUTH_USER_MODEL = 'accounts.User'`
    *   `LOGIN_URL = 'accounts:login'`
    *   `LOGIN_REDIRECT_URL = 'accounts:profile'`
    *   `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'` (for dev)
    *   `STATIC_URL = 'static/'`

**File 1: `entities.json`**
```json
<CONTENTS_OF_YOUR_ENTITIES.JSON_FILE_HERE>
```

**File 2: `relations.json`**
```json
<CONTENTS_OF_YOUR_RELATIONS.JSON_FILE_HERE>
```

**Instructions for QA:**

Please review the provided `entities.json` and `relations.json` files for completion and accuracy based on the Django `accounts` app context described above.

**Specifically, check for the following:**

**For `entities.json`:**

1.  **Completeness of Entities:**
    *   Are all key Django components from the `accounts` app (models, views, forms, templates, URLs) represented as entities?
    *   Are relevant project-level settings (`AUTH_USER_MODEL`, `LOGIN_URL`, `LOGIN_REDIRECT_URL`, `EMAIL_BACKEND`, `STATIC_URL`) included?
    *   Are there any obvious omissions of major components within the described scope?
2.  **Accuracy of Entity Attributes:**
    *   Is the `type` field for each entity correct (e.g., "Model", "View", "Form", "Template", "URL", "Setting")?
    *   Are `name`, `app` (for app-specific components), and `path` (for templates) accurate?
    *   For **Models**: Are key `attributes` (fields like `id`, `email` and custom methods like `get_full_name`, `save`) correctly listed?
    *   For **Forms**: Is `parent_class`, `model` (if applicable), and `fields` list accurate? Are `custom_methods` (like `clean_email`, `clean`) noted?
    *   For **Views**: Is `parent_class`, `mixins` (if any), `form_class` (if any), `template_name`, `email_template_name`, `subject_template_name`, `model` (if applicable), and `success_url_name` or `next_page_url_name` accurate?
    *   For **URLs**: Is the `name` (e.g., `accounts:signup`) and `path_pattern` correct?
    *   For **Settings**: Is the `value` and `file` (source file of the setting) correct?
3.  **Consistency and Formatting:**
    *   Are IDs (`id` field) unique and follow a consistent, understandable naming convention (e.g., `type:app.Name`)?
    *   Is the JSON structure valid?

**For `relations.json`:**

1.  **Completeness of Relations:**
    *   Are all significant relationships between the identified entities captured?
    *   Examples:
        *   View `USES_FORM` Form
        *   View `RENDERS_TEMPLATE` Template
        *   View `USES_EMAIL_TEMPLATE` Email Template
        *   View `USES_SUBJECT_TEMPLATE` Subject Template
        *   URL `ROUTES_TO_VIEW` View
        *   Form `BASED_ON_MODEL` Model
        *   View `MANAGES_MODEL_INSTANCE` Model (e.g., `ProfileView` for `User`)
        *   Setting `DEFINES_MODEL_REFERENCE` Model (e.g., `AUTH_USER_MODEL`)
        *   Setting `DEFINES_URL_REFERENCE` URL (e.g., `LOGIN_URL`)
        *   View `REDIRECTS_TO_URL_NAME` View (via URL name, like `success_url` or `next_page`)
2.  **Accuracy of Relations:**
    *   Do the `source` and `target` entity IDs in each relation correctly correspond to IDs defined in `entities.json`?
    *   Is the `type` of relationship accurate and descriptive?
    *   For `REDIRECTS_TO_URL_NAME` relations, is the `via` attribute correctly capturing the URL name used for the redirect?
3.  **Directionality:**
    *   Is the direction of the relationship (source -> target) logical?
4.  **Consistency and Formatting:**
    *   Is the JSON structure valid?

**Output Requirements:**

Provide your feedback as a structured report:

1.  **Overall Assessment:** A brief summary of the perceived quality, completeness, and accuracy.
2.  **Issues Found in `entities.json`:** List any missing entities, inaccuracies in attributes, or inconsistencies. For each issue, specify the entity `id` (if applicable) and describe the problem.
3.  **Issues Found in `relations.json`:** List any missing relations, inaccuracies in source/target/type, or inconsistencies. For each issue, specify the source/target and describe the problem.
4.  **Suggestions for Improvement:** If any, provide recommendations for making these files more comprehensive or accurate for knowledge graph population within the given scope.

Focus on the explicitly mentioned components and relationships. Do not infer components beyond what's typically found in a Django `accounts` app as described.