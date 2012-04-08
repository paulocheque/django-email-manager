# -*- coding: utf-8 -*-
from datetime import datetime, timedelta

from django.test import TestCase
from django_dynamic_fixture import G

from email_manager.models import EmailLog, EmailStatistics
from email_manager.feature_update_statistics import EmailStatisticsManager


class EmailStatisticsManagerTest(TestCase):
    def setUp(self):
        self.stat = EmailStatisticsManager()

    def test_when_there_is_no_log_it_must_do_nothing(self):
        self.stat.update_statistics()
        
        self.assertEquals(0, EmailStatistics.objects.count())
        self.assertEquals(0, EmailLog.objects.count())
        
    def test_logs_of_today_must_be_ignored(self):
        G(EmailLog)
        
        self.stat.update_statistics()
        
        self.assertEquals(0, EmailStatistics.objects.count())
        self.assertEquals(1, EmailLog.objects.count())
        
    def test_logs_of_the_future_must_be_ignored(self):
        l = G(EmailLog)
        l.date = datetime.today() + timedelta(days=1)
        l.save()
        
        self.stat.update_statistics()
        
        self.assertEquals(0, EmailStatistics.objects.count())
        self.assertEquals(1, EmailLog.objects.count())
        
    def test_logs_of_the_past_must_be_collected_and_logs_must_be_cleaned(self):
        l = G(EmailLog)
        l.date = datetime.today() - timedelta(days=1)
        l.save()
        
        self.stat.update_statistics()
        
        self.assertEquals(1, EmailStatistics.objects.count())
        self.assertEquals(1, EmailStatistics.objects.get(date=l.date).quantity)
        self.assertEquals(0, EmailLog.objects.count())
        
    def test_complete_scenario(self):
        l1a, l1b = G(EmailLog, n=2)
        l1a.date = datetime.today() - timedelta(days=2)
        l1b.date = datetime.today() - timedelta(days=2)
        l1a.save() ; l1b.save()
        
        l2 = G(EmailLog)
        l2.date = datetime.today() - timedelta(days=1)
        l2.save()
        
        l3 = G(EmailLog)
        l4 = G(EmailLog)
        
        self.stat.update_statistics()
        
        self.assertEquals(2, EmailStatistics.objects.count())
        self.assertEquals(2, EmailStatistics.objects.get(date=l1a.date).quantity)
        self.assertEquals(1, EmailStatistics.objects.get(date=l2.date).quantity)
        
        self.assertTrue(l1a not in EmailLog.objects.all())
        self.assertTrue(l1b not in EmailLog.objects.all())
        self.assertTrue(l2 not in EmailLog.objects.all())
        self.assertTrue(l3 in EmailLog.objects.all())
        self.assertTrue(l4 in EmailLog.objects.all())
        
        