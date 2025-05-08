from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('engineer/', views.engineer_dashboard, name='engineer_dashboard'),
    path('team-leader/', views.team_leader_dashboard, name='team_leader_dashboard'),
    path('department-leader/', views.department_leader_dashboard, name='department_leader_dashboard'),
    path('senior-manager/', views.senior_manager_dashboard, name='senior_manager_dashboard'),
] 