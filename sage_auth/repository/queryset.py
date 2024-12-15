from django.db.models import Sum
from django.db import models
from django.utils.timezone import now, timedelta

class LoginAttemptQuerySet(models.QuerySet):
    def sum_metrics(self, start_time=None, end_time=None):
        """
        Aggregate metrics for admin logins, failed attempts, and total logins in a given time range.
        """
        query = self
        if start_time:
            query = query.filter(timestamp__gte=start_time)
        if end_time:
            query = query.filter(timestamp__lt=end_time)
        return query.aggregate(
            total_failed_attempts=Sum('failed_attempts') or 0,
            total_admin_logins=Sum('admin_logins') or 0,
            total_logins=Sum('total_logins') or 0,
        )

    def monthly_metrics(self):
        """
        Aggregate metrics for the last month.
        """
        end_time = now()
        start_time = end_time - timedelta(days=30)
        return self.sum_metrics(start_time=start_time, end_time=end_time)

    def weekly_metrics(self):
        """
        Aggregate metrics for the last week.
        """
        end_time = now()
        start_time = end_time - timedelta(weeks=1)
        return self.sum_metrics(start_time=start_time, end_time=end_time)

    def daily_metrics(self):
        """
        Aggregate metrics for the last day.
        """
        end_time = now()
        start_time = end_time - timedelta(days=1)
        return self.sum_metrics(start_time=start_time, end_time=end_time)

    def hourly_metrics(self):
        """
        Aggregate metrics for the last 24 hours.
        """
        end_time = now()
        start_time = end_time - timedelta(hours=24)
        return self.sum_metrics(start_time=start_time, end_time=end_time)

    def twelve_hour_metrics(self):
        """
        Aggregate metrics for the last 12 hours.
        """
        end_time = now()
        start_time = end_time - timedelta(hours=12)
        return self.sum_metrics(start_time=start_time, end_time=end_time)
    
    def yearly_metrics(self):
        """
        Aggregate metrics for the last year.
        """
        end_time = now()
        start_time = end_time - timedelta(days=365)
        return self.sum_metrics(start_time=start_time, end_time=end_time)
