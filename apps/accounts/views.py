from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, LogoutView, 
    PasswordResetView, PasswordResetDoneView, 
    PasswordResetConfirmView, PasswordResetCompleteView
)
from django.views.generic import CreateView, UpdateView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import SignUpForm, ProfileForm, CustomAuthenticationForm
from django.conf import settings
from django.http import HttpResponseRedirect

# Create your views here.

class SignUpView(CreateView):
    form_class = SignUpForm
    template_name = 'accounts/signup.html'
    success_url = reverse_lazy('accounts:profile')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)  # Log the user in after signup
        messages.success(self.request, 'Welcome! Your account has been created successfully.')
        return response

class ProfileView(LoginRequiredMixin, UpdateView):
    form_class = ProfileForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('accounts:profile')
    
    def get_object(self, queryset=None):
        return self.request.user
    
    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully.')
        return super().form_valid(form)

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = CustomAuthenticationForm

    def form_valid(self, form):
        """Security check complete. Log the user in and handle 'remember me'."""
        remember_me = form.cleaned_data.get('remember_me')
        
        # Log the user in first
        login(self.request, form.get_user())
        
        # Then set session expiry
        if remember_me is True:
            self.request.session.set_expiry(settings.SESSION_COOKIE_AGE)
        else:
            self.request.session.set_expiry(0)
            
        # Force session save to ensure expiry is persisted
        # This is necessary because login() creates a new session cycle
        self.request.session.save()
            
        return HttpResponseRedirect(self.get_success_url())

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('accounts:login') # Redirect to login page after logout

# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html' # You'll need to create this template
    subject_template_name = 'accounts/password_reset_subject.txt' # And this one
    success_url = reverse_lazy('accounts:password_reset_done')
    # You can add a custom form here if needed: form_class = YourPasswordResetForm

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('accounts:password_reset_complete')
    # You can add a custom form here if needed: form_class = YourSetPasswordForm

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'
