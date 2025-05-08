from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.models import UserProfile, Department, Team, Session
from health_cards.models import HealthCard, Vote
from django.db.models import Count

@login_required
def dashboard(request):
    user_profile = request.user.profile
    
    if user_profile.role == 'engineer':
        return engineer_dashboard(request)
    elif user_profile.role == 'team_leader':
        return team_leader_dashboard(request)
    elif user_profile.role == 'department_leader':
        return department_leader_dashboard(request)
    elif user_profile.role == 'senior_manager':
        return senior_manager_dashboard(request)
    else:
        messages.warning(request, 'Please select your role first.')
        return redirect('role_selection')

@login_required
def engineer_dashboard(request):
    user_profile = request.user.profile
    
    if not user_profile.team:
        messages.warning(request, 'Please update your profile with your team.')
        return redirect('profile')
    
    active_sessions = Session.objects.filter(active=True).order_by('-date')
    cards = HealthCard.objects.all()
    
    context = {
        'user_profile': user_profile,
        'active_sessions': active_sessions,
        'cards': cards,
    }
    
    return render(request, 'dashboard/engineer_dashboard.html', context)

@login_required
def team_leader_dashboard(request):
    user_profile = request.user.profile
    
    if user_profile.role != 'team_leader':
        messages.error(request, 'Access denied. You are not a team leader.')
        return redirect('dashboard')
    
    if not user_profile.team:
        messages.warning(request, 'Please update your profile with your team.')
        return redirect('profile')
    
    team = user_profile.team
    team_votes = Vote.objects.filter(team=team)
    
    # Group votes by session and card
    team_summary = {}
    sessions = Session.objects.filter(votes__team=team).distinct()
    
    for session in sessions:
        team_summary[session] = {}
        for card in HealthCard.objects.all():
            vote_counts = team_votes.filter(
                session=session, 
                card=card
            ).values('status').annotate(count=Count('status'))
            
            team_summary[session][card] = {
                'green': next((item['count'] for item in vote_counts if item['status'] == 'green'), 0),
                'amber': next((item['count'] for item in vote_counts if item['status'] == 'amber'), 0),
                'red': next((item['count'] for item in vote_counts if item['status'] == 'red'), 0),
            }
    
    context = {
        'user_profile': user_profile,
        'team': team,
        'team_summary': team_summary,
        'sessions': sessions,
    }
    
    return render(request, 'dashboard/team_leader_dashboard.html', context)

@login_required
def department_leader_dashboard(request):
    user_profile = request.user.profile
    
    if user_profile.role != 'department_leader':
        messages.error(request, 'Access denied. You are not a department leader.')
        return redirect('dashboard')
    
    if not user_profile.team:
        messages.warning(request, 'Please update your profile with your team.')
        return redirect('profile')
    
    department = user_profile.team.department
    teams = Team.objects.filter(department=department)
    
    # Summary data for all teams in the department
    department_summary = {}
    sessions = Session.objects.all().order_by('-date')
    
    for session in sessions:
        department_summary[session] = {}
        for team in teams:
            department_summary[session][team] = {}
            for card in HealthCard.objects.all():
                vote_counts = Vote.objects.filter(
                    session=session, 
                    team=team,
                    card=card
                ).values('status').annotate(count=Count('status'))
                
                department_summary[session][team][card] = {
                    'green': next((item['count'] for item in vote_counts if item['status'] == 'green'), 0),
                    'amber': next((item['count'] for item in vote_counts if item['status'] == 'amber'), 0),
                    'red': next((item['count'] for item in vote_counts if item['status'] == 'red'), 0),
                }
    
    context = {
        'user_profile': user_profile,
        'department': department,
        'teams': teams,
        'department_summary': department_summary,
        'sessions': sessions,
    }
    
    return render(request, 'dashboard/department_leader_dashboard.html', context)

@login_required
def senior_manager_dashboard(request):
    user_profile = request.user.profile
    
    if user_profile.role != 'senior_manager':
        messages.error(request, 'Access denied. You are not a senior manager.')
        return redirect('dashboard')
    
    departments = Department.objects.all()
    sessions = Session.objects.all().order_by('-date')
    
    # Summary data for all departments
    organization_summary = {}
    
    for session in sessions:
        organization_summary[session] = {}
        for department in departments:
            organization_summary[session][department] = {}
            teams = Team.objects.filter(department=department)
            
            for card in HealthCard.objects.all():
                vote_counts = Vote.objects.filter(
                    session=session, 
                    team__in=teams,
                    card=card
                ).values('status').annotate(count=Count('status'))
                
                organization_summary[session][department][card] = {
                    'green': next((item['count'] for item in vote_counts if item['status'] == 'green'), 0),
                    'amber': next((item['count'] for item in vote_counts if item['status'] == 'amber'), 0),
                    'red': next((item['count'] for item in vote_counts if item['status'] == 'red'), 0),
                }
    
    context = {
        'user_profile': user_profile,
        'departments': departments,
        'organization_summary': organization_summary,
        'sessions': sessions,
    }
    
    return render(request, 'dashboard/senior_manager_dashboard.html', context)
