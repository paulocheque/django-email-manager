# -*- coding: utf-8 -*-
from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError


class EmailLog(models.Model):
    email = models.EmailField()
    subject = models.CharField(max_length=100, null=True, blank=True) # max_length=100 to store just the beginning of the subject
    date = models.DateField(auto_now_add=True)
    success = models.BooleanField(default=True)
    error = models.CharField(max_length=255, null=True, blank=True)
    
    def __unicode__(self):
        return u'%s: %s' % (self.email, self.subject)

    @staticmethod
    def create_log(email, subject, success=True, error=None):
        if error:
            if success:
                error = None # to avoid inconsistent data caused by bad use of this method
            else:
                error = error[0:255]
        return EmailLog.objects.create(email=email, subject=subject[0:100], success=success, error=error)
    

class EmailStatistics(models.Model):
    date = models.DateField(unique=True)
    quantity = models.PositiveIntegerField()

    def __unicode__(self):
        return u'%s' % self.date.strftime('%Y/%m/%d')


class EmailTypeManager(models.Manager):
    def all_types_that_users_can_disable(self):
        return self.filter(can_be_disabled=True).order_by('name')
    

class EmailType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    can_be_disabled = models.BooleanField(default=True)
    
    objects = EmailTypeManager()
    
    def __unicode__(self):
        return self.name
    
    def save(self, **kwargs):
        if not self.can_be_disabled:
            UserEmailPreferences.objects.filter(email_type=self).delete()
        super(EmailType, self).save(**kwargs)


class UserEmailPreferences(models.Model):
    user = models.ForeignKey(User)
    email_type = models.ForeignKey(EmailType)
    enabled = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('user', 'email_type')
        
    def save(self, **kwargs):
        if not self.enabled and not self.email_type.can_be_disabled: # precaution to avoid inconsistent data
            raise ValidationError('This type of e-mail can not be disabled.')
        try:
            super(UserEmailPreferences, self).save(**kwargs)
        except IntegrityError:
            raise ValidationError('This type of e-mail has already been disabled.')
        

class EmailDatabase(models.Model):
    email = models.EmailField(unique=True)

    
def update_email_database(sender, instance, **kargs):
    if instance.email:
        EmailDatabase.objects.get_or_create(email=instance.email)


EMAIL_DATABASE_ACTIVATED = settings.ACTIVATE_EMAIL_DATABASE if hasattr(settings, 'ACTIVATE_EMAIL_DATABASE') else False
if EMAIL_DATABASE_ACTIVATED:
    post_save.connect(update_email_database,
                      sender=User,
                      dispatch_uid='email_manager.update_email_database')