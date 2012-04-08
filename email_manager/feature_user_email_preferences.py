# -*- coding: utf-8 -*-
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.http import HttpResponseForbidden
from django.shortcuts import render_to_response, redirect

from email_manager.models import EmailType, UserEmailPreferences


def define_email_preferences(request, user_id):
    if request.user.id != int(user_id) and not request.user.is_superuser:
        return HttpResponseForbidden()
    try:
        user = User.objects.get(id=user_id) # super user can update another user too
        email_types = EmailType.objects.all_types_that_users_can_disable()
        prefs = UserEmailPreferences.objects.filter(user=user).values_list('email_type', flat=True)
        return render_to_response('email_manager/define_email_preferences.html', {'user': request.user,
                                                                                  'email_types': email_types,
                                                                                  'prefs': prefs})
    except User.DoesNotExist:
        messages.warning(request, 'User does not exist. Editing your user.')
        return redirect('/')


def disable_email_type(request, user_id, email_type_id):
    if request.user.id != int(user_id) and not request.user.is_superuser:
        return HttpResponseForbidden()
    try:
        user = User.objects.get(id=user_id) # super user can update another user too
        email_type = EmailType.objects.get(id=email_type_id)
        pref = UserEmailPreferences(user=user, email_type=email_type, enabled=False)
        pref.save()
        messages.success(request, 'Emails %s disabled.' % email_type.name)
        return redirect(reverse('email_manager:define_email_preferences', kwargs={'user_id': user_id}))
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
    except EmailType.DoesNotExist:
        messages.error(request, 'Email type does not exist.')
    except ValidationError as e:
        messages.warning(request, str(e))
    return define_email_preferences(request, user_id)


def enable_email_type(request, user_id, email_type_id):
    if request.user.id != int(user_id) and not request.user.is_superuser:
        return HttpResponseForbidden()
    try:
        user = User.objects.get(id=user_id) # super user can update another user too
        email_type = EmailType.objects.get(id=email_type_id)
        UserEmailPreferences.objects.filter(user=user, email_type=email_type).delete()
        messages.success(request, 'Emails %s enabled.' % email_type.name)
        return redirect(reverse('email_manager:define_email_preferences', kwargs={'user_id': user_id}))
    except User.DoesNotExist:
        messages.error(request, 'User does not exist.')
    except EmailType.DoesNotExist:
        messages.error(request, 'Email type does not exist.')
    except ValidationError as e:
        messages.warning(request, str(e))
    return define_email_preferences(request, user_id)
