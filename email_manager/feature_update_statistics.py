# -*- coding: utf-8 -*-
from datetime import datetime

from django.contrib import messages
from django.shortcuts import render_to_response

from email_manager.models import EmailLog, EmailStatistics


class EmailStatisticsManager(object):
    def update_statistics(self, date_max=None):
        """
        @date_max: it will be ignored dates after or equal than date_max.
        if date_max is None, it will be used datetime.today()
        """
        today = date_max if date_max else datetime.today()
        while EmailLog.objects.filter(date__lt=today).exists():
            last_date = EmailLog.objects.filter(date__lt=today).latest('date').date
            qty = EmailLog.objects.filter(date=last_date).count()
            EmailStatistics.objects.create(date=last_date, quantity=qty)
            EmailLog.objects.filter(date=last_date).delete()


def update_statistics(request):
    EmailStatisticsManager().update_statistics()
    messages.info(request, 'E-mail statistics updated')
    return render_to_response('email_manager/send_email.html')