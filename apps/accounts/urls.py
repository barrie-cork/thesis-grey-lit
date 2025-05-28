from django.urls import path
# We will use our custom views from views.py
# from django.contrib.auth import views as auth_views 
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    # Use CustomLoginView from views.py
    path('login/', views.CustomLoginView.as_view(), name='login'), 
    # Use CustomLogoutView from views.py
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),

    # Password reset URLs
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
] 