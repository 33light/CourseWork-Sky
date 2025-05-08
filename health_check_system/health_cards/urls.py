from django.urls import path
from . import views

urlpatterns = [
    path('sessions/', views.session_selection, name='session_selection'),
    path('health-check/<int:session_id>/', views.health_check, name='health_check'),
    path('team-summary/<int:team_id>/', views.team_summary, name='team_summary'),
    path('team-summary/<int:team_id>/<int:session_id>/', views.team_summary, name='team_summary_with_session'),
    path('department-summary/<int:department_id>/', views.department_summary, name='department_summary'),
    path('department-summary/<int:department_id>/<int:session_id>/', views.department_summary, name='department_summary_with_session'),
] 