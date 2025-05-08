from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import HealthCard, Vote
from accounts.models import Session, Team
from django.db.models import Count
from django.contrib.auth.models import User

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
            comment = request.POST.get(f'comment_{card.id}')

            if status and progress:
                vote, created = Vote.objects.update_or_create(
                    user=request.user,
                    card=card,
                    session=session,
                    defaults={
                        'team': team,
                        'status': status,
                        'progress': progress,
                        'comment': comment
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

@login_required
def team_summary(request, team_id):
    user_profile = request.user.profile

    if user_profile.role not in ['team_leader', 'department_leader', 'senior_manager']:
        messages.error(request, 'You do not have permission to view team summaries.')
        return redirect('dashboard')

    selected_team_id = request.GET.get('team_id')
    selected_session_id = request.GET.get('session_id')

    if user_profile.role == 'team_leader':
        teams = Team.objects.filter(department=user_profile.team.department)
    else:
        teams = Team.objects.all()

    if selected_team_id:
        team = get_object_or_404(Team, id=selected_team_id)
    else:
        team = user_profile.team

    if user_profile.role == 'department_leader' and team.department != user_profile.team.department:
        messages.error(request, 'You do not have permission to view this team.')
        return redirect('dashboard')

    sessions = Session.objects.all().order_by('-date')
    if selected_session_id:
        sessions = Session.objects.order_by('date')
        selected_session = Session.objects.get(id=selected_session_id)
        session_list = [s for s in sessions if s.id == selected_session.id or s.date < selected_session.date][-2:]
    else:
        sessions = sessions.order_by('date')
        session_list = list(sessions)


    summary_data = {}

    ordered_sessions = sessions.order_by('date')
    # session_list = list(ordered_sessions)

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
                'comments': comments,  # ✅ Add this line
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

    # If a specific session was selected, keep only the latest (the filtered one)
    if selected_session_id:
        latest_session = session_list[-1]
        summary_data = {latest_session: summary_data[latest_session]}

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

    if user_profile.role not in ['department_leader', 'senior_manager']:
        messages.error(request, 'You do not have permission to view department summaries.')
        return redirect('dashboard')

    department = get_object_or_404(Department, id=department_id)
    teams = Team.objects.filter(department=department)
    sessions = Session.objects.order_by('-date')

    # ✅ Get session_id from GET or URL parameter
    session_id = request.GET.get('session_id') or session_id

    if session_id:
        try:
            session = Session.objects.get(id=session_id)
            sessions_to_display = [session]
        except Session.DoesNotExist:
            sessions_to_display = []
    else:
        sessions_to_display = sessions

    summary_data = {}
    chart_labels = []
    chart_data = []
    trend_map = {
        "Improve": 2,
        "Stable": 1,
        "Decline": 0,
        "N/A": None
    }

    for session in sessions_to_display:
        summary_data[session] = {}
        for team in teams:
            total_green = total_red = total_amber = 0
            for card in HealthCard.objects.all():
                vote_counts = Vote.objects.filter(
                    session=session,
                    team=team,
                    card=card
                ).values('status').annotate(count=Count('status'))

                green = next((v['count'] for v in vote_counts if v['status'] == 'green'), 0)
                amber = next((v['count'] for v in vote_counts if v['status'] == 'amber'), 0)
                red = next((v['count'] for v in vote_counts if v['status'] == 'red'), 0)

                total_green += green
                total_amber += amber
                total_red += red

            if total_green > max(total_amber, total_red):
                trend = "Improve"
            elif total_red > max(total_green, total_amber):
                trend = "Decline"
            elif total_green == total_amber == total_red == 0:
                trend = "N/A"
            else:
                trend = "Stable"

            summary_data[session][team] = {'trend': trend}

            # ✅ Add to chart data
            numeric = trend_map.get(trend)
            if numeric is not None:
                chart_labels.append(team.name)
                chart_data.append(numeric)

    context = {
        'department': department,
        'teams': teams,
        'sessions': sessions,
        'selected_session_id': session_id,
        'summary_data': summary_data,
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }

    return render(request, 'health_cards/department_summary.html', context)

@login_required
def user_progress(request):
    user = request.user

    # Allow both engineers and team leaders to access
    if request.user.profile.role not in ['engineer', 'team_leader']:
        messages.error(request, "You do not have permission to view this page.")
        return redirect('dashboard')

    cards = HealthCard.objects.all()
    sessions = Session.objects.order_by('date')
    progress_data = {}

    for card in cards:
        votes = Vote.objects.filter(user=user, card=card).order_by('session__date')
        progress_data[card] = votes

    context = {
        'progress_data': progress_data,
        'sessions': sessions,
    }

    return render(request, 'health_cards/user_progress.html', context)




from accounts.models import Team
from django.contrib.auth.decorators import login_required

@login_required
def team_selection(request):
    if request.method == 'POST':
        team_id = request.POST.get('team_id')
        team = get_object_or_404(Team, id=team_id)
        request.user.profile.team = team
        request.user.profile.save()
        messages.success(request, f"Team '{team.name}' selected.")
        return redirect('session_selection')  # or any appropriate next step
    
    teams = Team.objects.all()
    return render(request, 'health_cards/team_selection.html', {'teams': teams})


@login_required
def team_leader_summary(request):
    user = request.user
    if user.profile.role != 'team_leader':
        messages.error(request, "Only team leaders can access this summary.")
        return redirect('dashboard')

    team = user.profile.team
    sessions = Session.objects.all().order_by('-date')
    selected_session_id = request.GET.get('session')
    selected_session = None
    summary_data = []

    if selected_session_id:
        selected_session = get_object_or_404(Session, id=selected_session_id)
        for card in HealthCard.objects.all():
            votes = Vote.objects.filter(team=team, session=selected_session, card=card)
            green = votes.filter(status='green').count()
            amber = votes.filter(status='amber').count()
            red = votes.filter(status='red').count()

            # Determine trend
            trend = "Amber"
            if green > max(amber, red):
                trend = "Improve"
            elif red > max(green, amber):
                trend = "Decline"

            summary_data.append({
                'card': card.name,
                'green': green,
                'amber': amber,
                'red': red,
                'trend': trend
            })

    context = {
        'team': team,
        'sessions': sessions,
        'selected_session_id': selected_session_id,
        'summary_data': summary_data,
    }

    return render(request, 'health_cards/team_leader_summary.html', context)

from django.contrib.auth.models import User
from accounts.models import Team

@login_required
def team_members(request):
    user_profile = request.user.profile

    # Only show teams in the department if department leader, else all
    if user_profile.role == 'department_leader':
        teams = Team.objects.filter(department=user_profile.team.department)
    else:
        teams = Team.objects.all()

    selected_team_id = request.GET.get('team_id')
    selected_team = None
    members = []

    if selected_team_id:
        selected_team = get_object_or_404(Team, id=selected_team_id)
        members = User.objects.filter(profile__team=selected_team).select_related('profile')
    
    context = {
        'teams': teams,
        'selected_team_id': selected_team_id,
        'selected_team': selected_team,
        'members': members,
    }

    return render(request, 'health_cards/team_members.html', context)
