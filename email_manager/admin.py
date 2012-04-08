# -*- coding: utf-8 -*-
from django.contrib import admin

from email_manager.models import EmailLog, EmailStatistics, EmailDatabase,\
    EmailType, UserEmailPreferences
from email_manager.feature_update_statistics import update_statistics


#Useful for development
#from django.conf import settings
#if settings.DEBUG: # precaution
#    from django.contrib.auth.models import Permission
#    admin.site.register(Permission)


class EmailLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'subject', 'date')
    list_filter = ('date',)
    search_fields = ('email', 'subject')
    ordering = ('date',)
    

def update_statistics(modeladmin, request, queryset):
    update_statistics()
update_statistics.short_description = "Update statistics"

    
class EmailStatisticsAdmin(admin.ModelAdmin):
    actions = [update_statistics]
    list_display = ('id', 'date', 'quantity',)
    search_fields = ('date',)
    ordering = ('date',)
    

class EmailTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'can_be_disabled',)
    list_filter = ('can_be_disabled',)
    search_fields = ('name',)
    ordering = ('name',)
    

class UserEmailPreferencesAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'email_type', 'enabled')
    list_filter = ('enabled', 'email_type')
    search_fields = ('user__username',)
    raw_id_fields = ('user',)
    ordering = ('email_type',)
    
        
class EmailDatabaseAdmin(admin.ModelAdmin):
    list_display = ('id', 'email')
    search_fields = ('email',)
    ordering = ('id',)
    
    
admin.site.register(EmailLog, EmailLogAdmin)
admin.site.register(EmailStatistics, EmailStatisticsAdmin)
admin.site.register(EmailType, EmailTypeAdmin)
admin.site.register(UserEmailPreferences, UserEmailPreferencesAdmin)
admin.site.register(EmailDatabase, EmailDatabaseAdmin)
    