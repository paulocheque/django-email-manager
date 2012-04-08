# -*- coding: utf-8 -*-
from django.core.exceptions import ValidationError
from django.contrib.auth.models import Group, User

from django.test import TestCase
from django_dynamic_fixture import G

from email_manager.feature_send_email import EmailSender, SendEmailAbstractForm, SendEmailToUsersForm
from email_manager.models import EmailType, UserEmailPreferences


class EmailSenderUsersOfGroupsTest(TestCase):
    def setUp(self):
        self.sender = EmailSender()
    
    def test_user_without_groups_must_consider_only_active_users(self):
        u1 = G(User, is_active=True)
        u2 = G(User, is_active=False)
        self.assertTrue(u1 in self.sender.users_of_groups(None))
        self.assertTrue(u2 not in self.sender.users_of_groups(None))
    
    def test_user_without_groups_must_not_be_selected(self):
        g1 = G(Group)
        u1 = G(User)
        self.assertTrue(u1 not in self.sender.users_of_groups([g1]))
        
    def test_user_must_have_at_least_one_group(self):
        g1, g2, g3 = G(Group, n=3)
        u1 = G(User, groups=[g1, g2])
        u2 = G(User, groups=[g1])
        u3 = G(User, groups=[g3])
        groups = [g1, g2]
        self.assertTrue(u1 in self.sender.users_of_groups(groups))
        self.assertTrue(u2 in self.sender.users_of_groups(groups))
        self.assertTrue(u3 not in self.sender.users_of_groups(groups))
        
    def test_user_without_at_least_one_of_the_selected_group_must_not_be_selected(self):
        g1, g2 = G(Group, n=2)
        u1 = G(User, groups=2)
        self.assertTrue(u1 not in self.sender.users_of_groups([g1, g2]))


class EmailSenderSendEmailToGroupsTest(TestCase):
    def setUp(self):
        self.sender = EmailSender()
        
    def test_empty_groups_must_do_nothing(self):
        groups = G(Group, n=2)
        total = self.sender.send_email_to_groups(groups, [], 'x', 'y', 'z')
        self.assertEquals(0, total)
        
    def test_it_must_consider_all_active_users_in_all_groups(self):
        groups = [G(Group, n=1)]
        G(User, groups=groups, is_active=True)
        G(User, groups=groups, is_active=False)
        
        total = self.sender.send_email_to_groups(groups, [], 'x', 'y', 'z')
        
        self.assertEquals(1, total)
        
    def test_it_must_not_send_the_same_email_more_than_once_to_a_user_that_belongs_to_many_groups(self):
        groups = G(Group, n=2)
        G(User, groups=groups)
        
        total = self.sender.send_email_to_groups(groups, [], 'x', 'y', 'z')
        
        self.assertEquals(1, total)
        
    def test_additional_emails_must_be_considered(self):
        groups = []
        total = self.sender.send_email_to_groups(groups, ['x@x.net'], 'x', 'y', 'z')
        self.assertEquals(1, total)
        
    def test_only_users_that_did_not_disable_email_type_must_be_considered(self):
        email_type = G(EmailType, can_be_disabled=True)
        groups = G(Group, n=2)
        users = G(User, n=2, groups=groups)
        G(UserEmailPreferences, user=users[0], email_type=email_type, enabled=False)
        G(UserEmailPreferences, user=users[1], email_type=email_type, enabled=True)

        total = self.sender.send_email_to_groups(groups, [], 'x', 'y', 'z', email_type)
        
        self.assertEquals(1, total)
        
        
class EmailSenderSendEmailToUsersTest(TestCase):
    def setUp(self):
        self.sender = EmailSender()
        
    def test_default_usage(self):
        users = G(User, n=2)
        total = self.sender.send_email_to_users(users, [], 'x', 'y', 'z')
        self.assertEquals(2, total)
        
    def test_additional_emails_must_be_considered(self):
        users = []
        total = self.sender.send_email_to_users(users, ['x@x.net'], 'x', 'y', 'z')
        self.assertEquals(1, total)
        
    def test_only_users_that_did_not_disable_email_type_must_be_considered(self):
        email_type = G(EmailType, can_be_disabled=True)
        users = G(User, n=2)
        G(UserEmailPreferences, user=users[0], email_type=email_type, enabled=False)
        G(UserEmailPreferences, user=users[1], email_type=email_type, enabled=True)
        
        total = self.sender.send_email_to_users(users, [], 'x', 'y', 'z', email_type)
        
        self.assertEquals(1, total)
        
        
class SendEmailAbstractFormTest(TestCase):
    def setUp(self):
        self.form = SendEmailAbstractForm()

    def test_to_must_accept_one_email(self):
        self.form.cleaned_data = {'to': 'a@a.com'}
        self.assertEquals(['a@a.com',], self.form.clean_to())
        
    def test_to_must_accept_a_list_of_emails_separated_by_commads(self):
        self.form.cleaned_data = {'to': 'a@a.com,b@b.com'}
        self.assertEquals(['a@a.com', 'b@b.com'], self.form.clean_to())
        
    def test_to_must_reject_bad_formatted_email(self):
        self.form.cleaned_data = {'to': 'a'}
        self.assertRaises(ValidationError, self.form.clean_to)
        
        self.form.cleaned_data = {'to': 'a@a.com,x@'}
        self.assertRaises(ValidationError, self.form.clean_to)
        
        
class SendEmailToUsersFormTest(TestCase):
    def setUp(self):
        self.form = SendEmailToUsersForm()
        
    def test_to_must_verify_if_user_exist(self):
        self.form.cleaned_data = {'users': 'x'}
        self.assertRaises(ValidationError, self.form.clean_users)
        
    def test_to_must_verify_if_user_is_active(self):
        G(User, username='x', is_active=False)
        self.form.cleaned_data = {'users': 'x'}
        self.assertRaises(ValidationError, self.form.clean_users)
        
    def test_to_must_verify_if_user_has_email(self):
        G(User, username='x', is_active=True, email='')
        self.form.cleaned_data = {'users': 'x'}
        self.assertRaises(ValidationError, self.form.clean_users)
        
    def test_success_scenario(self):
        G(User, username='x', is_active=True, email='x@x.net')
        self.form.cleaned_data = {'users': 'x'}
        self.form.clean_users()
        