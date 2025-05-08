from django.contrib import admin
from .models import Department, Team, Session, UserProfile

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'created_at')
    list_filter = ('department',)
    search_fields = ('name',)

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'active')
    list_filter = ('active',)
    search_fields = ('name',)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'team')
    list_filter = ('role', 'team')
    search_fields = ('user__username', 'user__email')
