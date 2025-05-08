from django.contrib import admin
from .models import HealthCard, Vote

@admin.register(HealthCard)
class HealthCardAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name', 'description')

@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ('user', 'card', 'team', 'session', 'status', 'progress', 'updated_at')
    list_filter = ('status', 'progress', 'team', 'session')
    search_fields = ('user__username', 'card__name')
