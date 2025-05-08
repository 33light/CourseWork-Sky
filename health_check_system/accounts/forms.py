from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from .models import UserProfile

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    favorite_place = forms.CharField(required=True, max_length=100, help_text="Enter your favorite place (will be used for password recovery)")
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            # Save favorite place to profile
            favorite_place = self.cleaned_data.get('favorite_place')
            user.profile.favorite_place = favorite_place
            user.profile.save()
        return user

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['team', 'favorite_place']
        
class RoleSelectionForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['role']
        widgets = {
            'role': forms.RadioSelect()
        }

class DirectPasswordResetForm(forms.Form):
    favorite_place = forms.CharField(max_length=100, required=True, label="Your Favorite Place")
    new_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True,
        label="New Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(),
        required=True,
        label="Confirm Password"
    )
    
    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError("Passwords don't match")
                
        favorite_place = cleaned_data.get('favorite_place')
        if favorite_place:
            # Check if any profile has this favorite place
            profile_exists = UserProfile.objects.filter(favorite_place=favorite_place).exists()
            if not profile_exists:
                raise forms.ValidationError("No account found with this favorite place")
                
        return cleaned_data 