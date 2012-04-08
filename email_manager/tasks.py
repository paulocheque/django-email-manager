# -*- coding: utf-8 -*-
from celery.decorators import task
from django.conf import settings

from email_manager.feature_send_email import EmailSender
from email_manager.feature_update_statistics import EmailStatisticsManager


@task(queue=settings.EMAIL_MANAGER_TASK if hasattr(settings, 'EMAIL_MANAGER_TASK') else None)
def send_email(emails, subject, text_content=None, html_content=None, main_content=None):
    EmailSender().send_email(emails, subject, text_content, html_content, main_content)


@task(queue=settings.EMAIL_MANAGER_TASK if hasattr(settings, 'EMAIL_MANAGER_TASK') else None)
def send_email_to_groups(groups, additional_emails, subject, content, html_content):
    EmailSender().send_email_to_groups(groups, additional_emails, subject, content, html_content)
    
    
@task(queue=settings.EMAIL_MANAGER_TASK if hasattr(settings, 'EMAIL_MANAGER_TASK') else None)
def send_email_to_users(users, additional_emails, subject, content, html_content):
    EmailSender().send_email_to_users(users, additional_emails, subject, content, html_content)
    

@task(queue=settings.EMAIL_MANAGER_TASK if hasattr(settings, 'EMAIL_MANAGER_TASK') else None)
def update_statistics():
    EmailStatisticsManager().update_statistics()