"""
URL configuration for thesis_grey_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

def home_redirect(request):
    """Smart redirect based on authentication status"""
    if request.user.is_authenticated:
        return redirect('review_manager:dashboard')
    else:
        return redirect('accounts:login')

urlpatterns = [
    path('', home_redirect, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('review/', include('apps.review_manager.urls')),
    path('strategy/', include('apps.search_strategy.urls')),  # Re-enabled
    path('serp/', include('apps.serp_execution.urls')),      # Added
    path('results/', include('apps.review_results.urls')),   # Added
    path('reporting/', include('apps.reporting.urls')),      # Added
]
