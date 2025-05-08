from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Team(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Session(models.Model):
    name = models.CharField(max_length=100)
    date = models.DateField()
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.name} - {self.date}"

class UserProfile(models.Model):
    ROLE_CHOICES = (
        ('engineer', 'Engineer'),
        ('team_leader', 'Team Leader'),
        ('department_leader', 'Department Leader'),
        ('senior_manager', 'Senior Manager'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='engineer')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='members')
    favorite_place = models.CharField(max_length=100, blank=True, null=True, help_text="Your favorite place (used for password recovery)")
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
