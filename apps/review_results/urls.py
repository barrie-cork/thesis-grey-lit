from django.urls import path
from . import views

app_name = 'review_results'

urlpatterns = [
    path('overview/<uuid:session_id>/', views.overview, name='overview'),
]
