from django.urls import path
from . import views

app_name = 'serp_execution'

urlpatterns = [
    path('execute/<uuid:session_id>/', views.execute_search, name='execute'),
    path('status/<uuid:session_id>/', views.view_status, name='status'),
]
