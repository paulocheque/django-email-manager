# -*- coding: utf-8 -*-
from django.core.management.base import AppCommand
from email_manager.feature_update_statistics import EmailStatisticsManager


class Command(AppCommand):
    def handle(self, *args, **options):
        EmailStatisticsManager().update_statistics()