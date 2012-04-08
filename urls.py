# -*- coding: utf-8 -*-
from django.conf.urls.defaults import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
     url(r'^admin/', include(admin.site.urls)),

     (r'^email-manager/', include('email_manager.urls', namespace='email_manager', app_name='email_manager')),
)
