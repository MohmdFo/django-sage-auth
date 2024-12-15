from django.db import models
from .queryset import  LoginAttemptQuerySet


class LoginAttemptManager(models.Manager):
    def get_queryset(self):
        return LoginAttemptQuerySet(self.model, using=self._db)

    def monthly_metrics(self):
        """
        Aggregate metrics for the last month.
        """
        return self.get_queryset().monthly_metrics()

    def weekly_metrics(self):
        """
        Aggregate metrics for the last week.
        """
        return self.get_queryset().weekly_metrics()

    def daily_metrics(self):
        """
        Aggregate metrics for the last day.
        """
        return self.get_queryset().daily_metrics()

    def hourly_metrics(self):
        """
        Aggregate metrics for the last 24 hours.
        """
        return self.get_queryset().hourly_metrics()

    def twelve_hour_metrics(self):
        """
        Aggregate metrics for the last 12 hours.
        """
        return self.get_queryset().twelve_hour_metrics()
    
    def yearly_metrics(self):
        """
        Aggregate metrics for the last year.
        """
        return self.get_queryset().yearly_metrics()