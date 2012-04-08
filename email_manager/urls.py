from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('email_manager',
    url('^send-email-to-groups', 'feature_send_email.send_email_to_groups', name='send_email_to_groups'),
    url('^send-email-to-users', 'feature_send_email.send_email_to_users', name='send_email_to_users'),
    
    url('^update-statistics', 'feature_update_statistics.update_statistics', name='update_statistics'),
    
    url('^email-preferences/(?P<user_id>\d+)/$', 
        'feature_user_email_preferences.define_email_preferences', name='define_email_preferences'),
    # ajax
    url('^email-preferences/(?P<user_id>\d+)/disable-email-type/(?P<email_type_id>\d+)/$', 
        'feature_user_email_preferences.disable_email_type', name='disable_email_type'),
    url('^email-preferences/(?P<user_id>\d+)/enable-email-type/(?P<email_type_id>\d+)/$', 
        'feature_user_email_preferences.enable_email_type', name='enable_email_type'),
)
