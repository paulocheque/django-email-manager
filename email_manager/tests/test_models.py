# -*- coding: utf-8 -*-
from django.test import TestCase
from django_dynamic_fixture import G

from email_manager.models import EmailLog, EmailType, UserEmailPreferences
from django.core.exceptions import ValidationError


class EmailLogTest(TestCase):
    def test_must_truncate_long_subjects(self):
        log = EmailLog.create_log('x@x.net', 'x' * 101, success=True, error=None)
        self.assertEquals('x' * 100, log.subject)

    def test_must_ignore_error_in_case_of_success(self):
        log = EmailLog.create_log('x@x.net', 'x', success=True, error='x')
        self.assertEquals(None, log.error)
        
    def test_must_not_ignore_error_in_case_of_error(self):
        log = EmailLog.create_log('x@x.net', 'x', success=False, error='x')
        self.assertEquals('x', log.error)
        
    def test_must_truncate_long_error_messages(self):
        log = EmailLog.create_log('x@x.net', 'x', success=False, error='x' * 256)
        self.assertEquals('x' * 255, log.error)
        
        
class EmailTypeTest(TestCase):
    def test_create_email_type_does_not_raise_exceptions(self):
        G(EmailType, can_be_disabled=True)
        G(EmailType, can_be_disabled=False)
    
    def test_if_this_can_not_be_disabled_so_all_user_preferences_must_be_removed(self):
        email_type = G(EmailType, can_be_disabled=True)
        G(UserEmailPreferences, email_type=email_type)

        email_type.can_be_disabled = False
        email_type.save()
        
        self.assertEquals(0, UserEmailPreferences.objects.count())

    def test_if_this_can_be_disabled_so_it_does_not_need_to_worry_about_user_preferences(self):
        email_type = G(EmailType, can_be_disabled=True)
        G(UserEmailPreferences, email_type=email_type)

        email_type.save()
        
        self.assertEquals(1, UserEmailPreferences.objects.count())


class UserEmailPreferencesTest(TestCase):
    def test_user_can_not_disable_a_mandatory_type_of_email(self):
        email_type = G(EmailType, can_be_disabled=False)
        pref = G(UserEmailPreferences, email_type=email_type, enabled=True)
        pref.enabled = False
        self.assertRaises(ValidationError, pref.save)
        
    def test_user_can_not_disable_twice(self):
        email_type = G(EmailType, can_be_disabled=True)
        user = G(UserEmailPreferences, email_type=email_type).user
        self.assertRaises(ValidationError, UserEmailPreferences.objects.create, user=user, email_type=email_type)
        
        