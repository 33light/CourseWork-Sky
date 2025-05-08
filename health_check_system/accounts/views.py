from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import (
    LoginView, LogoutView, PasswordResetView, 
    PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
)
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth.forms import SetPasswordForm
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, RoleSelectionForm, DirectPasswordResetForm
from .models import UserProfile

def landing_page(request):
    return render(request, 'accounts/landing.html')

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password. Please try again.')
        return super().form_invalid(form)

def custom_logout(request):
    # Log the user out
    logout(request)
    
    # Create response and delete session cookies
    response = HttpResponseRedirect(reverse('landing'))
    response.delete_cookie('sessionid')
    response.delete_cookie('csrftoken')
    
    # Clear all other cookies to ensure no admin sessions persist
    for cookie in request.COOKIES:
        response.delete_cookie(cookie)
    
    return response

@login_required
def role_selection(request):
    if request.method == 'POST':
        form = RoleSelectionForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            try:
                profile = form.save()
                messages.success(request, f'Your role has been updated to {profile.get_role_display()}!')
                return redirect('dashboard')
            except Exception as e:
                messages.error(request, f'Error updating role: {str(e)}')
        else:
            messages.error(request, 'Please select a valid role.')
    else:
        form = RoleSelectionForm(instance=request.user.profile)
    
    return render(request, 'accounts/role_selection.html', {'form': form})

@login_required
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/profile.html', context)

class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    success_url = '/password-reset/done/'
    
    def form_valid(self, form):
        """Override to add email success notification."""
        try:
            # Check if the email exists in the database
            email = form.cleaned_data.get('email')
            if not User.objects.filter(email=email).exists():
                messages.error(self.request, f"There is no user with email {email}")
                return self.form_invalid(form)
                
            response = super().form_valid(form)
            messages.success(self.request, f"Password reset email has been sent to {email}")
            return response
        except Exception as e:
            messages.error(self.request, f"Error sending password reset email: {str(e)}")
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        """Add error messages on invalid form submission."""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = '/password-reset/complete/'
    
    def form_valid(self, form):
        try:
            response = super().form_valid(form)
            messages.success(self.request, "Your password has been reset successfully!")
            return response
        except Exception as e:
            messages.error(self.request, f"Error resetting password: {str(e)}")
            return self.form_invalid(form)
    
    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{field}: {error}")
        return super().form_invalid(form)

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'

def direct_password_reset(request):
    if request.method == 'POST':
        form = DirectPasswordResetForm(request.POST)
        if form.is_valid():
            favorite_place = form.cleaned_data.get('favorite_place')
            new_password = form.cleaned_data.get('new_password')
            
            try:
                # Find the profile with the given favorite place
                profile = UserProfile.objects.get(favorite_place=favorite_place)
                user = profile.user
                
                # Set the new password
                user.set_password(new_password)
                user.save()
                
                messages.success(request, "Password has been reset successfully. You can now login with your new password.")
                return redirect('login')
            except UserProfile.DoesNotExist:
                messages.error(request, "No account found with this favorite place.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = DirectPasswordResetForm()
    
    return render(request, 'accounts/direct_password_reset.html', {'form': form})
