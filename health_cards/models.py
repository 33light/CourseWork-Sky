from django.db import models
from django.contrib.auth.models import User
from accounts.models import Team, Session

class HealthCard(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name

class Vote(models.Model):
    STATUS_CHOICES = (
        ('green', 'Green'),
        ('amber', 'Amber'),
        ('red', 'Red'),
    )
    
    PROGRESS_CHOICES = (
        ('better', 'Getting Better'),
        ('same', 'Same'),
        ('worse', 'Getting Worse'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    card = models.ForeignKey(HealthCard, on_delete=models.CASCADE, related_name='votes')
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='votes')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='votes')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    progress = models.CharField(max_length=10, choices=PROGRESS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField(blank=True, null=True)
    
    class Meta:
        unique_together = ('user', 'card', 'session')
    
    def __str__(self):
        return f"{self.user.username} - {self.card.name} - {self.status}"
