from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model, authenticate
from django.core.exceptions import ValidationError

User = get_user_model()

class SignUpForm(UserCreationForm):
    """
    Form for user registration. Extends UserCreationForm to include email field
    and custom validation.
    """
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email (optional)'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def clean_email(self):
        """
        Validate that the email is unique if provided.
        """
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                raise ValidationError('A user with this email already exists.')
        return email

class ProfileForm(UserChangeForm):
    """
    Form for updating user profile. Extends UserChangeForm but removes
    the password field and adds custom validation.
    """
    password = None  # Remove the password field

    # Explicitly define the email field to set empty_value=None
    # This ensures that if the field is submitted empty, cleaned_data['email'] will be None,
    # which then gets saved as NULL in the database because User.email has null=True.
    email = forms.EmailField(
        required=False,  # Consistent with model's blank=True
        empty_value=None, # Ensure empty input becomes None in cleaned_data
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email (optional)'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            # email widget is handled by the explicit field definition above
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'})
        }
    
    def clean_email(self):
        """
        Validate that the email is unique if provided, excluding the current user.
        """
        email = self.cleaned_data.get('email') # Will be None if submitted blank due to empty_value=None
        
        if email: # Only validate if email is not None (i.e., not blank)
            existing_users = User.objects.filter(email=email).exclude(pk=self.instance.pk)
            if existing_users.exists():
                raise ValidationError('A user with this email already exists.')
        return email # Return None or the valid email string

    # The temporary debugging save() method is now removed.
    # The default ModelForm.save() will handle saving.
    # If cleaned_data['email'] is None (from empty_value=None), 
    # Django's default ModelForm behavior for a CharField/EmailField 
    # is to save it as an empty string ('') in the database, even if model field has null=True.
    # This now aligns with the updated test expectation. 

class CustomAuthenticationForm(AuthenticationForm):
    # Override the username field to change its label
    username = forms.CharField(
        label="Username or Email",
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'})
    )

    remember_me = forms.BooleanField(
        required=False, 
        initial=False, 
        label="Keep me logged in",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    ) 

    def clean(self):
        username_or_email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')

        if username_or_email and password:
            # Try to authenticate with the input as username first
            self.user_cache = authenticate(self.request, username=username_or_email, password=password)
            
            if self.user_cache is None:
                # If username auth fails, try to find user by email and then authenticate
                try:
                    user_by_email = User.objects.get(email__iexact=username_or_email)
                    self.user_cache = authenticate(self.request, username=user_by_email.username, password=password)
                except User.DoesNotExist:
                    self.user_cache = None # Explicitly set to None if no user found by email
            
            if self.user_cache is None:
                raise self.get_invalid_login_error()
            else:
                self.confirm_login_allowed(self.user_cache)

        return self.cleaned_data 