# Placeholder URLs for search_strategy app
from django.urls import path
from django.http import HttpResponse

app_name = 'search_strategy'

def placeholder_view(request, session_id=None):
    return HttpResponse("Search Strategy app coming soon!")

urlpatterns = [
    path('define/<uuid:session_id>/', placeholder_view, name='define'),
]