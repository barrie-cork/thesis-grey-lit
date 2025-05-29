from django.urls import path
from . import views

app_name = 'search_strategy'

urlpatterns = [
    path('define/<int:session_id>/', views.define_strategy_view, name='define'),
]
