from django.urls import path
from . import views

app_name = 'reporting'

urlpatterns = [
    path('summary/<uuid:session_id>/', views.summary, name='summary'),
]
