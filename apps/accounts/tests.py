from django.test import TestCase
from django.contrib.auth import get_user_model
from apps.accounts.forms import SignUpForm, ProfileForm
from django.db import IntegrityError
import uuid
from django.urls import reverse_lazy
from django.conf import settings
from apps.accounts.forms import CustomAuthenticationForm
from django.core import mail
import re
from django.utils.html import escape

User = get_user_model()

class SignUpFormTests(TestCase):
    """Test suite for the SignUpForm."""

    def test_form_valid_with_all_fields(self):
        """Test that the form is valid with all required and optional fields provided correctly."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexP@ssw0rd!',
            'password2': 'complexP@ssw0rd!'
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=f"Form should be valid. Errors: {form.errors.as_json()}")

    def test_form_valid_without_optional_email(self):
        """Test that the form is valid when the optional email field is not provided."""
        form_data = {
            'username': 'testuser_no_email',
            'password1': 'complexP@ssw0rd!',
            'password2': 'complexP@ssw0rd!'
        }
        form = SignUpForm(data=form_data)
        self.assertTrue(form.is_valid(), msg=f"Form should be valid without email. Errors: {form.errors.as_json()}")

    def test_form_invalid_if_username_missing(self):
        """Test that the form is invalid if the username is missing."""
        form_data = {
            'email': 'test@example.com',
            'password1': 'complexP@ssw0rd!',
            'password2': 'complexP@ssw0rd!'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid if username is missing.")
        self.assertIn('username', form.errors, msg="'username' should be a key in form errors.")

    def test_form_invalid_if_password1_missing(self):
        """Test that the form is invalid if password1 is missing."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password2': 'complexP@ssw0rd!'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid if password1 is missing.")
        self.assertIn('password1', form.errors, msg="'password1' should be a key in form errors.")

    def test_form_invalid_if_password2_missing(self):
        """Test that the form is invalid if password2 is missing."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexP@ssw0rd!'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid if password2 is missing.")
        self.assertIn('password2', form.errors, msg="'password2' should be a key in form errors.")

    def test_form_invalid_if_passwords_mismatch(self):
        """Test that the form is invalid if password1 and password2 do not match."""
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'complexP@ssw0rd!',
            'password2': 'WrongP@ssw0rd!'  # Mismatch
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid if passwords mismatch.")
        self.assertIn('password2', form.errors, msg="Mismatch error should be associated with 'password2'.")
            
        # More resilient check for the password mismatch error
        self.assertTrue(
            any("the two password fields" in e.lower() and "match" in e.lower() for e in form.errors['password2']),
            msg="Error message for password mismatch not found."
        )

    def test_form_invalid_if_username_exists(self):
        """Test that the form is invalid if the username already exists."""
        # Create a user first
        User.objects.create_user(username='existinguser', password='password')
        form_data = {
            'username': 'existinguser',  # Duplicate username
            'email': 'unique@example.com',
            'password1': 'complexP@ssw0rd!',
            'password2': 'complexP@ssw0rd!'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid if username already exists.")
        self.assertIn('username', form.errors, msg="Error should be associated with 'username'.")
        self.assertTrue(
            any('A user with that username already exists.' in error for error in form.errors['username']),
            msg="Error message for duplicate username not found."
        )

    def test_form_invalid_if_email_exists(self):
        """Test that the form is invalid if the provided email already exists."""
        # Create a user with an email first
        User.objects.create_user(username='user_with_email', email='existing@example.com', password='password')
        form_data = {
            'username': 'newuser',
            'email': 'existing@example.com',  # Duplicate email
            'password1': 'complexP@ssw0rd!',
            'password2': 'complexP@ssw0rd!'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid(), msg="Form should be invalid if email already exists.")
        self.assertIn('email', form.errors, msg="Error should be associated with 'email'.")
        self.assertTrue(
            any('A user with this email already exists.' in error for error in form.errors['email']),
            msg="Error message for duplicate email not found."
        )

    def test_form_password_strength_validation_too_short(self):
        """Test password strength validation: too short."""
        form_data = {
            'username': 'testuser',
            'password1': 'short',
            'password2': 'short'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors) # Django's UserCreationForm associates this with password2
        # Default Django message check might be too brittle if customized. Let's check for *an* error.
        self.assertTrue(len(form.errors['password2']) > 0, "Password validation error expected for short password.")

    def test_form_password_strength_validation_too_common(self):
        """Test password strength validation: too common."""
        form_data = {
            'username': 'testuser',
            'password1': 'password',
            'password2': 'password'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertTrue(len(form.errors['password2']) > 0, "Password validation error expected for common password.")

    def test_form_password_strength_validation_entirely_numeric(self):
        """Test password strength validation: entirely numeric."""
        form_data = {
            'username': 'testuser',
            'password1': '123456789',
            'password2': '123456789'
        }
        form = SignUpForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertTrue(len(form.errors['password2']) > 0, "Password validation error expected for numeric password.")


class ProfileFormTests(TestCase):
    """Test suite for the ProfileForm."""

    @classmethod
    def setUpTestData(cls):
        """Set up non-modified objects used by all test methods."""
        cls.user1 = User.objects.create_user(
            username='user1', 
            email='user1@example.com', 
            password='password123',
            first_name='UserA',
            last_name='One'
        )
        cls.user2 = User.objects.create_user(
            username='user2', 
            email='user2@example.com', 
            password='password123',
            first_name='UserB',
            last_name='Two'
        )

    def test_form_valid_with_all_fields_changed(self):
        """Test form is valid when all editable fields are changed correctly."""
        form_data = {
            'username': 'user1_updated',
            'email': 'user1_updated@example.com',
            'first_name': 'UserAUpdated',
            'last_name': 'OneUpdated'
        }
        form = ProfileForm(data=form_data, instance=self.user1)
        self.assertTrue(form.is_valid(), msg=f"Form should be valid. Errors: {form.errors.as_json()}")
        
        # Test saving the form
        form.save()
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.username, 'user1_updated')
        self.assertEqual(self.user1.email, 'user1_updated@example.com')
        self.assertEqual(self.user1.first_name, 'UserAUpdated')
        self.assertEqual(self.user1.last_name, 'OneUpdated')

    def test_form_valid_with_no_changes(self):
        """Test form is valid if submitted with no changes to the data."""
        form_data = {
            'username': self.user1.username,
            'email': self.user1.email,
            'first_name': self.user1.first_name,
            'last_name': self.user1.last_name
        }
        form = ProfileForm(data=form_data, instance=self.user1)
        self.assertTrue(form.is_valid(), msg=f"Form should be valid with no changes. Errors: {form.errors.as_json()}")

    def test_form_valid_email_unchanged(self):
        """Test form is valid if email is not changed, even if it exists for this user."""
        form_data = {
            'username': 'user1_new_username',
            'email': self.user1.email,  # Email unchanged
            'first_name': 'UpdatedFirst',
            'last_name': 'UpdatedLast'
        }
        form = ProfileForm(data=form_data, instance=self.user1)
        self.assertTrue(form.is_valid(), msg=f"Form should be valid when email is unchanged. Errors: {form.errors.as_json()}")
        form.save()
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, 'user1@example.com') # Ensure it's the same
        self.assertEqual(self.user1.username, 'user1_new_username')


    def test_form_invalid_if_email_changed_to_existing_email_of_another_user(self):
        """Test form is invalid if email is changed to an email already used by another user."""
        form_data = {
            'username': self.user1.username,
            'email': self.user2.email,  # Attempt to use user2's email
            'first_name': self.user1.first_name,
            'last_name': self.user1.last_name
        }
        form = ProfileForm(data=form_data, instance=self.user1)
        self.assertFalse(form.is_valid(), msg="Form should be invalid if email is changed to an existing one.")
        self.assertIn('email', form.errors, msg="Error should be associated with 'email'.")
        self.assertTrue(
            any('A user with this email already exists.' in error for error in form.errors['email']),
            msg="Error message for duplicate email not found."
        )

    def test_form_valid_if_email_changed_to_new_unique_email(self):
        """Test form is valid if email is changed to a new, unique email."""
        form_data = {
            'username': self.user1.username,
            'email': 'new_unique_email@example.com',
            'first_name': self.user1.first_name,
            'last_name': self.user1.last_name
        }
        form = ProfileForm(data=form_data, instance=self.user1)
        self.assertTrue(form.is_valid(), msg=f"Form should be valid with a new unique email. Errors: {form.errors.as_json()}")
        form.save()
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.email, 'new_unique_email@example.com')

    def test_form_valid_if_email_set_to_blank_when_previously_set(self):
        """Test form is valid if email is set to blank (since it's optional)."""
        self.assertTrue(self.user1.email is not None and self.user1.email != '', "Pre-condition: user1 must have a non-blank email.")
        form_data = {
            'username': self.user1.username,
            'email': '',  # Set to blank
            'first_name': self.user1.first_name,
            'last_name': self.user1.last_name
        }
        form = ProfileForm(data=form_data, instance=self.user1)
        self.assertTrue(form.is_valid(), msg=f"Form should be valid when email is cleared. Errors: {form.errors.as_json()}")
        
        form.save()
        self.user1.refresh_from_db()
        
        self.assertIsNone(self.user1.email, "Email should be None after being cleared.")

    def test_form_invalid_if_username_is_blank(self):
        """Test form is invalid if username is set to blank (it's required)."""
        form_data = {
            'username': '',  # Blank username
            'email': self.user1.email,
            'first_name': self.user1.first_name,
            'last_name': self.user1.last_name
        }
        form = ProfileForm(data=form_data, instance=self.user1)
        self.assertFalse(form.is_valid(), msg="Form should be invalid if username is blank.")
        self.assertIn('username', form.errors, msg="Error should be associated with 'username'.")
        self.assertTrue(
            any('This field is required.' in error for error in form.errors['username']),
            msg="Error message for blank username not found."
        )
    
    def test_form_invalid_if_username_changed_to_existing_username_of_another_user(self):
        """Test form is invalid if username is changed to one already used by another user."""
        form_data = {
            'username': self.user2.username, # Attempt to use user2's username
            'email': self.user1.email,
            'first_name': self.user1.first_name,
            'last_name': self.user1.last_name
        }
        form = ProfileForm(data=form_data, instance=self.user1)
        self.assertFalse(form.is_valid(), msg="Form should be invalid if username is changed to an existing one of another user.")
        self.assertIn('username', form.errors, msg="Error should be associated with 'username'.")
        self.assertTrue(
            any('A user with that username already exists.' in error for error in form.errors['username']),
            msg="Error message for duplicate username not found."
        )
        
    def test_form_valid_first_name_and_last_name_can_be_blank(self):
        """Test form is valid if first_name and last_name are blank (they are optional)."""
        form_data = {
            'username': self.user1.username,
            'email': self.user1.email,
            'first_name': '',
            'last_name': ''
        }
        form = ProfileForm(data=form_data, instance=self.user1)
        self.assertTrue(form.is_valid(), msg=f"Form should be valid with blank first/last names. Errors: {form.errors.as_json()}")
        form.save()
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.first_name, '')
        self.assertEqual(self.user1.last_name, '')

class UserModelTests(TestCase):
    def test_user_creation_with_valid_data(self):
        """Test creating a user with valid data."""
        user = User.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='password123'
        )
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('password123'))
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)

    def test_uuid_primary_key_generation(self):
        """Test that the user ID is a UUID."""
        user = User.objects.create_user(username='uuidtestuser', password='password123')
        self.assertIsInstance(user.id, uuid.UUID)

    def test_email_uniqueness_constraint(self):
        """Test that email addresses must be unique if provided."""
        User.objects.create_user(username='user1', email='unique@example.com', password='password123')
        with self.assertRaises(IntegrityError):
            User.objects.create_user(username='user2', email='unique@example.com', password='password123')

    def test_email_can_be_null(self):
        """Test that a user can be created with a null email."""
        user1 = User.objects.create_user(username='user_null_email1', email=None, password='password123')
        user2 = User.objects.create_user(username='user_null_email2', email=None, password='password123')
        self.assertIsNone(user1.email)
        self.assertIsNone(user2.email)
        # Ensure that multiple users can have null emails (unique constraint only applies if email is not null)
        self.assertNotEqual(user1.username, user2.username)


    def test_timestamp_auto_population(self):
        """Test that created_at and updated_at are auto-populated."""
        user = User.objects.create_user(username='timestamptest', password='password123')
        self.assertIsNotNone(user.created_at)
        self.assertIsNotNone(user.updated_at)
        
        # Check that updated_at changes on save
        old_updated_at = user.updated_at
        user.first_name = 'Test'
        user.save()
        user.refresh_from_db()
        self.assertGreater(user.updated_at, old_updated_at)

    def test_user_string_representation(self):
        """Test the string representation of the User model."""
        user = User.objects.create_user(username='str_repr_user', password='password123')
        self.assertEqual(str(user), 'str_repr_user')

    def test_get_full_name_method(self):
        """Test the get_full_name method."""
        user = User.objects.create_user(username='fullnameuser', first_name='Test', last_name='User', password='password123')
        self.assertEqual(user.get_full_name(), 'Test User')
        
        user_no_name = User.objects.create_user(username='nousername', password='password123')
        self.assertEqual(user_no_name.get_full_name(), 'nousername')

    # Note: date_joined is set to None in the model, so no specific test for it.
    # created_at serves this purpose.


class SignUpViewTests(TestCase):
    def test_signup_view_get_request(self):
        """Test GET request to SignUpView renders the signup form."""
        response = self.client.get(reverse_lazy('accounts:signup'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/signup.html')
        self.assertIsInstance(response.context['form'], SignUpForm)

    def test_signup_view_successful_post_request(self):
        """Test POST request to SignUpView with valid data creates a user and logs them in."""
        initial_user_count = User.objects.count()
        form_data = {
            'username': 'newsignupuser',
            'email': 'newsignup@example.com',
            'password1': 'ValidP@ss123',
            'password2': 'ValidP@ss123',
        }
        response = self.client.post(reverse_lazy('accounts:signup'), data=form_data)
        
        self.assertEqual(User.objects.count(), initial_user_count + 1, "A new user should be created.")
        new_user = User.objects.get(username='newsignupuser')
        self.assertEqual(new_user.email, 'newsignup@example.com')
        
        # Check user is logged in
        self.assertTrue(response.wsgi_request.user.is_authenticated, "User should be logged in after signup.")
        self.assertEqual(response.wsgi_request.user.id, new_user.id)

        # Check for success message (requires messages middleware and context processor)
        # Note: To test messages, we need to fetch them from the response after a redirect.
        # For a CreateView, the success_url is typically a redirect.
        self.assertRedirects(response, reverse_lazy('accounts:profile'), msg_prefix="Should redirect to profile after successful signup.")
        
        # To properly test messages after a redirect, you often need to follow the redirect
        # and inspect the messages on the *next* response, or use a different approach
        # if the messages are not directly on the redirect response itself.
        # For now, we will check that the user is created and redirected.

    def test_signup_view_invalid_post_request(self):
        """Test POST request to SignUpView with invalid data re-renders the form with errors."""
        initial_user_count = User.objects.count()
        form_data = {
            'username': 'invaliduser',
            'email': 'invalidemail',  # Invalid email format
            'password1': 'short',
            'password2': 'short',
        }
        response = self.client.post(reverse_lazy('accounts:signup'), data=form_data, follow=False) # Don't follow redirect here
        
        self.assertEqual(User.objects.count(), initial_user_count, "No user should be created with invalid data.")
        self.assertEqual(response.status_code, 200, "Should re-render the page with the form and errors.")
        self.assertTemplateUsed(response, 'accounts/signup.html')
        self.assertIsInstance(response.context['form'], SignUpForm)
        self.assertTrue(response.context['form'].errors, "Form should contain errors.")
        self.assertIn('email', response.context['form'].errors)
        self.assertIn('password2', response.context['form'].errors) # UserCreationForm specific errors often on password2

class LoginLogoutViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user_username = 'testloginuser'
        cls.test_user_password = 'ValidP@ss123'
        cls.user = User.objects.create_user(username=cls.test_user_username, password=cls.test_user_password)

    def test_login_view_get_request(self):
        """Test GET request to CustomLoginView renders the login form."""
        response = self.client.get(reverse_lazy('accounts:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertIsInstance(response.context['form'], CustomAuthenticationForm) # Check for CustomAuthenticationForm

    def test_login_view_successful_post_request(self):
        """Test POST request to CustomLoginView with valid credentials logs the user in."""
        form_data = {
            'username': self.test_user_username,
            'password': self.test_user_password,
        }
        response = self.client.post(reverse_lazy('accounts:login'), data=form_data)
        self.assertRedirects(response, reverse_lazy('accounts:profile'))
        # Check user is logged in by checking request.user in a subsequent request if needed, or check session
        self.assertTrue('_auth_user_id' in self.client.session, "User ID should be in session after login.")
        self.assertEqual(str(self.client.session['_auth_user_id']), str(self.user.id))

    def test_login_view_successful_post_request_with_remember_me(self):
        """Test POST request with 'remember me' checked sets session expiry correctly."""
        form_data = {
            'username': self.test_user_username,
            'password': self.test_user_password,
            'remember_me': True,
        }
        self.client.post(reverse_lazy('accounts:login'), data=form_data)
        # Assuming settings.SESSION_COOKIE_AGE is the default (2 weeks)
        self.assertEqual(self.client.session.get_expiry_age(), settings.SESSION_COOKIE_AGE)

    def test_login_view_successful_post_request_without_remember_me(self):
        """Test POST request without 'remember me' sets session to expire on browser close."""
        form_data = {
            'username': self.test_user_username,
            'password': self.test_user_password,
            # 'remember_me': False or not present
        }
        response = self.client.post(reverse_lazy('accounts:login'), data=form_data)
        
        # Check if session cookie expires at browser close
        # When set_expiry(0) is called, Django sets the cookie to be a session cookie
        session_cookie = self.client.cookies.get(settings.SESSION_COOKIE_NAME)
        self.assertIsNotNone(session_cookie, "Session cookie should exist")
        
        # For browser-session cookies, max-age should be None or empty string
        # and expires should also not be set
        max_age = session_cookie.get('max-age')
        expires = session_cookie.get('expires')
        
        # Browser session cookies have no max-age (None or '') and no expires
        self.assertIn(max_age, [None, '', 0], 
                     f"Session cookie max-age should indicate browser session (got: {max_age!r})")
        
        # Alternative: check the session itself
        # After login, the session should be configured to expire at browser close
        # We can verify this by checking the session's expiry setting
        self.assertTrue(self.client.session.get_expire_at_browser_close(),
                       "Session should be set to expire at browser close")

    def test_login_view_invalid_credentials_post_request(self):
        """Test POST request to CustomLoginView with invalid credentials shows errors."""
        form_data = {
            'username': self.test_user_username,
            'password': 'wrongpassword',
        }
        response = self.client.post(reverse_lazy('accounts:login'), data=form_data)
        self.assertEqual(response.status_code, 200) # Should re-render the login page
        self.assertTemplateUsed(response, 'accounts/login.html')
        self.assertIsInstance(response.context['form'], CustomAuthenticationForm)
        self.assertTrue(response.context['form'].errors, "Form should contain errors for invalid login.")
        self.assertFalse('_auth_user_id' in self.client.session, "User should not be logged in.")

    def test_logout_view(self):
        """Test CustomLogoutView logs the user out and redirects."""
        # Log the user in first
        self.client.login(username=self.test_user_username, password=self.test_user_password)
        self.assertTrue('_auth_user_id' in self.client.session, "User should be logged in before logout.")
        
        response = self.client.get(reverse_lazy('accounts:logout'))
        self.assertRedirects(response, reverse_lazy('accounts:login'))
        self.assertFalse('_auth_user_id' in self.client.session, "User should be logged out.")

class ProfileViewTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.test_user_username = 'profiletestuser'
        cls.test_user_password = 'ValidP@ss123'
        cls.user = User.objects.create_user(
            username=cls.test_user_username, 
            password=cls.test_user_password,
            email='profile@example.com',
            first_name='InitialFirst',
            last_name='InitialLast'
        )

    def setUp(self):
        # Log in the user for each test method
        self.client.login(username=self.test_user_username, password=self.test_user_password)

    def test_profile_view_get_request(self):
        """Test GET request to ProfileView renders the profile form with user data."""
        response = self.client.get(reverse_lazy('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertIsInstance(response.context['form'], ProfileForm)
        self.assertEqual(response.context['form'].instance, self.user)
        self.assertEqual(response.context['user'], self.user) # Check user is in context

    def test_profile_view_successful_post_request(self):
        """Test POST to ProfileView with valid data updates the user and redirects."""
        new_email = 'updated_profile@example.com'
        new_first_name = 'UpdatedFirst'
        form_data = {
            'username': self.test_user_username, # Username is usually read-only in ProfileForm
            'email': new_email,
            'first_name': new_first_name,
            'last_name': 'UpdatedLast',
        }
        
        # Perform the POST request that should trigger the message and redirect
        response = self.client.post(reverse_lazy('accounts:profile'), data=form_data, follow=True)
        
        # Check the redirect happened
        self.assertEqual(response.redirect_chain[0][0], reverse_lazy('accounts:profile'))
        
        # Refresh user from DB and check updated fields
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, new_email)
        self.assertEqual(self.user.first_name, new_first_name)
        self.assertEqual(self.user.last_name, 'UpdatedLast')

        # Check for messages using Django's message framework
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Your profile has been updated successfully.')

    def test_profile_view_invalid_post_request(self):
        """Test POST to ProfileView with invalid data re-renders form with errors."""
        # Create another user to cause an email conflict
        User.objects.create_user(username='otheruser', email='other@example.com', password='password')
        
        original_email = self.user.email
        form_data = {
            'username': self.test_user_username,
            'email': 'other@example.com',  # Email that will cause a conflict
            'first_name': 'AttemptFirst',
            'last_name': 'AttemptLast',
        }
        response = self.client.post(reverse_lazy('accounts:profile'), data=form_data)
        self.assertEqual(response.status_code, 200) # Should re-render the page
        self.assertTemplateUsed(response, 'accounts/profile.html')
        self.assertIsInstance(response.context['form'], ProfileForm)
        self.assertTrue(response.context['form'].errors, "Form should contain errors.")
        self.assertIn('email', response.context['form'].errors)
        
        self.user.refresh_from_db()
        self.assertEqual(self.user.email, original_email, "User email should not have changed on invalid form submission.")

    def test_profile_view_requires_login(self):
        """Test that ProfileView redirects to login if user is not authenticated."""
        self.client.logout() # Ensure user is logged out
        response = self.client.get(reverse_lazy('accounts:profile'))
        expected_redirect_url = f"{reverse_lazy('accounts:login')}?next={reverse_lazy('accounts:profile')}"
        self.assertRedirects(response, expected_redirect_url, status_code=302, target_status_code=200)

class PasswordResetFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user_email = 'resettest@example.com'
        cls.user_username = 'resettestuser'
        cls.user = User.objects.create_user(username=cls.user_username, email=cls.user_email, password='oldpassword123')

    def test_password_reset_flow(self):
        """Test the complete password reset flow."""
        # 1. Request password reset
        response = self.client.post(reverse_lazy('accounts:password_reset'), {'email': self.user_email})
        self.assertRedirects(response, reverse_lazy('accounts:password_reset_done'))
        
        # 2. Check email was sent and extract link
        self.assertEqual(len(mail.outbox), 1)
        email_message = mail.outbox[0]
        self.assertEqual(email_message.to[0], self.user_email)
        self.assertIn('Password Reset Request', email_message.subject) # Or match subject_template_name content
        
        # Extract the token and uidb64 from the email body
        # This regex looks for a path like /reset/uidb64/token/
        match = re.search(r'(/accounts/reset/[^/]+/[^/]+/)', email_message.body)
        self.assertIsNotNone(match, "Password reset link not found in email body.")
        reset_link = match.group(1)
        self.assertTrue(reset_link.startswith('/accounts/reset/'))

        # 3. Visit the reset confirmation link
        response = self.client.get(reset_link)
        # Django redirects valid tokens to add /set-password/
        if response.status_code == 302:
            response = self.client.get(response.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/password_reset_confirm.html')
        self.assertTrue(response.context['validlink'], "Reset link should be valid.")
        self.assertIn('form', response.context)

        # 4. Submit the new password form
        new_password = 'newP@ssw0rd123'
        # Use the current path after any redirects
        form_action = response.wsgi_request.path
        response = self.client.post(form_action, {
            'new_password1': new_password,
            'new_password2': new_password,
        })
        self.assertRedirects(response, reverse_lazy('accounts:password_reset_complete'))

        # 5. Try logging in with the new password
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password), "Password should be updated.")
        
        # Attempt login via the login view
        login_response = self.client.post(reverse_lazy('accounts:login'), {
            'username': self.user_username,
            'password': new_password,
        })
        self.assertRedirects(login_response, reverse_lazy('accounts:profile'))
        self.assertTrue('_auth_user_id' in self.client.session, "User should be logged in after password reset and login.")

class SecurityTests(TestCase):
    def test_password_hashing(self):
        """Test that passwords are not stored in plain text and check_password works."""
        raw_password = 'SecureP@ssw0rd!AB'
        user = User.objects.create_user(username='sectestuser', password=raw_password)
        self.assertNotEqual(user.password, raw_password, "Password should be hashed, not stored as plain text.")
        self.assertTrue(user.check_password(raw_password), "check_password should validate the correct raw password.")
        self.assertFalse(user.check_password('incorrectpassword'), "check_password should reject an incorrect password.")

    def test_xss_prevention_in_profile_update(self):
        """Test basic XSS prevention: data submitted to profile should be escaped in template if rendered.
           This is an indirect test; Django's autoescaping is the primary defense.
        """
        user = User.objects.create_user(username='xssuser', password='password123')
        self.client.login(username='xssuser', password='password123')
        
        xss_string = '<script>alert("xss")</script>'
        malicious_first_name = f'FirstName{xss_string}'
        
        # Update profile with potentially malicious string
        self.client.post(reverse_lazy('accounts:profile'), data={
            'username': 'xssuser',
            'email': 'xss@example.com',
            'first_name': malicious_first_name,
            'last_name': 'LastName',
        })
        
        user.refresh_from_db()
        self.assertEqual(user.first_name, malicious_first_name, "Data should be saved as is in the DB.")

        # Now, if we were to render this field in a template that doesn't incorrectly use `|safe`,
        # Django's autoescaping should handle it.
        # Let's simulate rendering it by checking the escaped version.
        # This doesn't directly test the template rendering but checks the principle.
        # A more robust test would fetch the profile page and check the HTML content.
        
        # For example, if displaying user.first_name directly in a template:
        # Expected escaped string: FirstName&lt;script&gt;alert(&quot;xss&quot;)&lt;/script&gt;
        # Note: escape() behavior can vary slightly. Django's template escape is more comprehensive.
        
        # For a more direct test of template rendering:
        response = self.client.get(reverse_lazy('accounts:profile'))
        self.assertEqual(response.status_code, 200)
        # We expect the XSS string to be escaped in the form field value
        # Input fields display raw value but it would be escaped if rendered outside form
        # For profile.html, it's rendered inside a form input, so it will appear as the raw string.
        # The real test is that it's not *executed*.
        # A better test would be to have a display-only field or check a custom display page.
        # For now, we confirm the data is stored and rely on Django default XSS protection for display.
        # We can also check that the malicious string is not found *unescaped* in the response content
        # if it were to be displayed directly (not in a form input).
        
        # A simple check: ensure the raw script tag isn't directly in the response body unless it's within an input value
        # This is not a perfect XSS test but a basic check.
        # A proper XSS test might involve more specialized tools or selenium for browser execution check.
        # Check if the script tag is escaped if it appeared as raw text somewhere.
        # self.assertNotContains(response, xss_string) # This would fail if it's an input value
        # A better check is that if it's rendered, it should be escaped.
        # For ProfileForm, the 'first_name' is an input field. Its value attribute will contain the raw string.
        # If we rendered {{ user.first_name }} directly, it would be escaped.
        self.assertContains(response, f'value="{escape(malicious_first_name)}"' , html=False, 
                          msg_prefix="Malicious string should be escaped if rendered in a value attribute, or raw if template uses `safe` (which it shouldn't for user input)")
        # This assertion is tricky because form inputs *do* render the value raw inside the attribute.
        # The key is that Django's autoescape protects direct rendering: {{ user.first_name }}
        # The browser itself prevents <input value="<script>..."> from executing the script from the value attr.
        # So, for this test, we confirm it's stored, and rely on default Django XSS for general rendering.
