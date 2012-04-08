# -*- coding: utf-8 -*-
from smtplib import SMTPException

from django import forms
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, BadHeaderError
from django.contrib import messages
from django.core.validators import validate_email
from django.contrib.auth.models import User, Group
from django.http import HttpResponse
from django.shortcuts import render_to_response

from email_manager.models import EmailLog, EmailType, UserEmailPreferences


USING_CELERY = settings.EMAIL_MANAGER_USING_CELERY if hasattr(settings, 'EMAIL_MANAGER_USING_CELERY') else None


class EmailSender(object):
    def send_email(self, emails, subject, text_content=None, html_content=None, main_content=None):
        """
        @subject, @text_content and @html_content are intuitive.
        @to must have be a string (email) or a list of strings (emails).
        @main_content must be 'text', 'html' or None. If None, it will be set to 'html' if html_content if provided, 'text' in other case.
        Returns True if success, False otherwise.
        """
        if USING_CELERY:
            from email_manager.tasks import send_email
            send_email.delay(emails, subject, text_content, html_content, main_content)
            return None
        try:
            if not emails:
                return None
            if isinstance(emails, str):
                emails = [emails]
            to = [emails[0]]
            bcc = emails[1:] # used for network optimization
            formatted_subject = '%s %s' % (settings.EMAIL_SUBJECT_PREFIX, subject)
            msg = EmailMultiAlternatives(formatted_subject, text_content, to=to, bcc=bcc)
            if html_content:
                msg.attach_alternative(html_content, "text/html")
                if main_content == 'html' or not main_content:
                    msg.content_subtype = "html"
                # else default is plain/text
            msg.send(fail_silently=False)
            for email in emails:
                EmailLog.create_log(email, subject)
            return True
        except SMTPException as e:
            EmailLog.create_log(email, subject, success=False, error=str(e))
            return False
    
    def users_of_groups(self, groups, email_type=None):
        qs = User.objects.filter(is_active=True, email__isnull=False)
        if email_type:
            qs = qs.exclude(useremailpreferences__email_type=email_type, useremailpreferences__enabled=False)
        if groups:
            # we can use IN parameter because a good system must not have 'infinite' groups
            return qs.filter(groups__in=groups).distinct()
        return qs
    
    def send_email_to_groups(self, groups, additional_emails, subject, content, html_content, email_type=None):
        emails = self.users_of_groups(groups, email_type).values_list('email', flat=True)
        emails = list(emails)
        emails.extend(additional_emails)
        self.send_email(emails, subject, content, html_content)
        return len(emails)
    
    def user_accept_to_receive_this_type_of_email(self, user, email_type):
        if not email_type: return True
        return not UserEmailPreferences.objects.filter(user=user, email_type=email_type, enabled=False).exists()

    def send_email_to_users(self, users, additional_emails, subject, content, html_content, email_type=None):
        emails = [user.email for user in users if user.is_active and user.email and self.user_accept_to_receive_this_type_of_email(user, email_type)]
        emails.extend(additional_emails)
        self.send_email(emails, subject, content, html_content)
        return len(emails)


class SendEmailAbstractForm(forms.Form):
    to = forms.CharField(max_length=500, required=False, help_text='Additional e-mails separated by comma')
    email_type = forms.ModelChoiceField(queryset=EmailType.objects.all(), required=False)

    def clean_to(self):
        if self.cleaned_data['to']:
            emails = self.cleaned_data['to'].split(',')
            map(validate_email, emails)
            return emails
        return self.cleaned_data['to']
    

class SendEmailToGroupsForm(SendEmailAbstractForm):
    groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all())
    subject = forms.CharField(max_length=300, required=True)
    content = forms.CharField(max_length=5000, required=False)
    html_content = forms.CharField(max_length=5000, required=False, help_text='For HTML e-mail')
    
    
def send_email_to_groups(request):
    form = SendEmailToGroupsForm(request.POST or None)
    if form.is_valid():
        try:
            sender = EmailSender()
            total_of_emails = sender.send_email_to_groups(form.cleaned_data.get('groups'), 
                                                          form.cleaned_data.get('to'), 
                                                          form.cleaned_data.get('subject'), 
                                                          form.cleaned_data.get('content'),
                                                          form.cleaned_data.get('html_content'),
                                                          form.cleaned_data.get('email_type'),)
            messages.info(request, 'Total of %s e-mails' % total_of_emails)
            return HttpResponse('Total of %s e-mails' % total_of_emails )
        except BadHeaderError: # Preventing header injection
            return HttpResponse('No donuts for you. This incident was reported.')
    return render_to_response('email_manager/send_email.html', {'form': form})


class SendEmailToUsersForm(SendEmailAbstractForm):
    users = forms.CharField(max_length=500, help_text='Usernames separated by comma.')
    subject = forms.CharField(max_length=300, required=True)
    content = forms.CharField(max_length=5000, required=False)
    html_content = forms.CharField(max_length=5000, required=False, help_text='For HTML e-mail')
    
    def clean_users(self):
        # we can not use IN parameter here to avoid bug in the SQL query.
        users = []
        if self.cleaned_data['users']:
            usernames = self.cleaned_data['users'].split(',')
            for username in usernames:
                try:
                    user = User.objects.get(username=username)
                    if not user.is_active:
                        raise forms.ValidationError('User %s is not active.' % username)
                    if not user.email:
                        raise forms.ValidationError('User %s does not have e-mail.' % username)
                    users.append(user)
                except User.DoesNotExist:
                    raise forms.ValidationError('User %s does not exist.' % username)
        return users
    

def send_email_to_users(request):
    form = SendEmailToUsersForm(request.POST or None)
    if form.is_valid():
        try:
            sender = EmailSender()
            total_of_emails = sender.send_email_to_users(form.cleaned_data.get('users'), 
                                                         form.cleaned_data.get('to'), 
                                                         form.cleaned_data.get('subject'), 
                                                         form.cleaned_data.get('content'),
                                                         form.cleaned_data.get('html_content'),
                                                         form.cleaned_data.get('email_type'),)
            messages.info(request, 'Total of %s e-mails' % total_of_emails)
            return HttpResponse('Total of %s e-mails' % total_of_emails )
        except BadHeaderError: # Preventing header injection
            return HttpResponse('No donuts for you. This incident was reported.')
    return render_to_response('email_manager/send_email.html', {'form': form})

