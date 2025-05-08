from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HealthCard, Vote
from accounts.models import Session, Team
from django.db.models import Count

# Create your views here.

@login_required
def session_selection(request):
    if not request.user.profile.team:
        messages.warning(request, 'Please update your profile with your team.')
        return redirect('profile')
    
    active_sessions = Session.objects.filter(active=True).order_by('-date')
    
    context = {
        'active_sessions': active_sessions,
    }
    
    return render(request, 'health_cards/session_selection.html', context)

@login_required
def health_check(request, session_id):
    session = get_object_or_404(Session, id=session_id, active=True)
    team = request.user.profile.team
    
    if not team:
        messages.warning(request, 'Please update your profile with your team.')
        return redirect('profile')
    
    health_cards = HealthCard.objects.all()
    
    # Get existing votes for this user
    user_votes = {}
    for card in health_cards:
        try:
            vote = Vote.objects.get(user=request.user, card=card, session=session)
            user_votes[card.id] = {
                'status': vote.status,
                'progress': vote.progress
            }
        except Vote.DoesNotExist:
            user_votes[card.id] = {
                'status': '',
                'progress': ''
            }
    
    if request.method == 'POST':
        for card in health_cards:
            status = request.POST.get(f'status_{card.id}')
            progress = request.POST.get(f'progress_{card.id}')
            
            if status and progress:
                vote, created = Vote.objects.update_or_create(
                    user=request.user,
                    card=card,
                    session=session,
                    defaults={
                        'team': team,
                        'status': status,
                        'progress': progress
                    }
                )
        
        messages.success(request, 'Your votes have been saved!')
        return redirect('dashboard')
    
    context = {
        'session': session,
        'team': team,
        'health_cards': health_cards,
        'user_votes': user_votes,
    }
    
    return render(request, 'health_cards/health_check.html', context)

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Team, Session, HealthCard, Vote
from django.db.models import Count

@login_required
def team_summary(request, team_id):
    user_profile = request.user.profile

    if user_profile.role not in ['team_leader', 'department_leader', 'senior_manager']:
        messages.error(request, 'You do not have permission to view team summaries.')
        return redirect('dashboard')

    selected_team_id = request.GET.get('team_id')
    selected_session_id = request.GET.get('session_id')

    # Get team list based on role
    if user_profile.role == 'team_leader':
        teams = Team.objects.filter(department=user_profile.team.department)
    else:
        teams = Team.objects.all()

    # Get the team object
    if selected_team_id:
        team = get_object_or_404(Team, id=selected_team_id)
    else:
        team = get_object_or_404(Team, id=team_id)

    if user_profile.role == 'department_leader' and team.department != user_profile.team.department:
        messages.error(request, 'You do not have permission to view this team.')
        return redirect('dashboard')

    sessions = Session.objects.all().order_by('date')

    # Build session_list based on selected session
    if selected_session_id:
        try:
            selected_session_id = int(selected_session_id)
            selected_session = Session.objects.get(id=selected_session_id)
            session_list = [s for s in sessions if s.id == selected_session.id or s.date < selected_session.date][-2:]
        except (Session.DoesNotExist, ValueError):
            session_list = list(sessions)
    else:
        session_list = list(sessions)

    summary_data = {}

    for i, session in enumerate(session_list):
        session_summary = {}
        for card in HealthCard.objects.all():
            votes = Vote.objects.filter(session=session, team=team, card=card).values('status').annotate(count=Count('status'))

            comments = list(
                Vote.objects.filter(session=session, team=team, card=card)
                .exclude(comment__isnull=True)
                .exclude(comment__exact='')
                .values_list('comment', flat=True)
            )

            current = {
                'green': next((v['count'] for v in votes if v['status'] == 'green'), 0),
                'amber': next((v['count'] for v in votes if v['status'] == 'amber'), 0),
                'red': next((v['count'] for v in votes if v['status'] == 'red'), 0),
                'comments': comments,
            }

            previous = None
            if i > 0 and card in summary_data.get(session_list[i - 1], {}):
                previous = summary_data[session_list[i - 1]][card]

            if not previous:
                trend = "N/A"
            elif current['green'] > previous['green']:
                trend = "Improving"
            elif current['red'] > previous['red']:
                trend = "Declining"
            else:
                trend = "Stable"

            current['trend'] = trend
            session_summary[card] = current

        summary_data[session] = session_summary

    # If session is filtered, show only the last session from session_list
    if selected_session_id and session_list:
        summary_data = {session_list[-1]: summary_data[session_list[-1]]}

    context = {
        'team': team,
        'teams': teams,
        'sessions': Session.objects.all().order_by('-date'),
        'selected_team_id': selected_team_id,
        'selected_session_id': selected_session_id,
        'summary_data': summary_data,
    }

    return render(request, 'health_cards/team_summary.html', context)

from accounts.models import Department  # Make sure this import is added
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from accounts.models import Department, Team, Session
from .models import HealthCard, Vote

@login_required
def department_summary(request, department_id, session_id=None):
    user_profile = request.user.profile
    
    # Check if user is authorized to view department summary
    if user_profile.role not in ['department_leader', 'senior_manager']:
        messages.error(request, 'You do not have permission to view department summaries.')
        return redirect('dashboard')
    
    department = get_object_or_404(Department, id=department_id)
    teams = Team.objects.filter(department=department)
    
    sessions = Session.objects.all().order_by('-date')
    
    if session_id:
        session = get_object_or_404(Session, id=session_id)
        sessions_to_display = [session]
    else:
        sessions_to_display = sessions
    
    # Get votes for each team, card and session
    summary_data = {}
    for session in sessions_to_display:
        summary_data[session] = {}
        for team in teams:
            summary_data[session][team] = {}
            for card in HealthCard.objects.all():
                vote_counts = Vote.objects.filter(
                    session=session,
                    team=team,
                    card=card
                ).values('status').annotate(count=Count('status'))
                
                summary_data[session][team][card] = {
                    'green': next((item['count'] for item in vote_counts if item['status'] == 'green'), 0),
                    'amber': next((item['count'] for item in vote_counts if item['status'] == 'amber'), 0),
                    'red': next((item['count'] for item in vote_counts if item['status'] == 'red'), 0),
                }
    
    context = {
        'department': department,
        'teams': teams,
        'sessions': sessions,
        'selected_session_id': session_id,
        'summary_data': summary_data,
    }
    
    return render(request, 'health_cards/department_summary.html', context)
