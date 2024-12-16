from django.db.models.functions import ExtractHour, ExtractDay, ExtractMonth, ExtractYear
from django.db.models import Sum, Count
from django.utils.timezone import now, timedelta
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
        Aggregate metrics grouped by month for the last 12 months.
        """
        end_time = now()
        start_time = end_time - timedelta(days=365)  # Last 12 months
        query = self.filter(timestamp__gte=start_time, timestamp__lt=end_time)
        
        # Annotate with the month and year for unique month/year combinations
        monthly_data = query.annotate(month=ExtractMonth('timestamp'), year=ExtractYear('timestamp')).values('month', 'year').annotate(
            total_attempts=Sum('total_logins') + Sum('failed_attempts'),
            total_logins=Sum('total_logins'),
            failed_attempts=Sum('failed_attempts'),
        ).order_by('year', 'month')

        # Ensure all 12 months are represented
        current_month = end_time.month
        current_year = end_time.year
        months = []
        totals = []

        for i in range(12):
            # Calculate month and year for each entry
            month = (current_month - i - 1) % 12 + 1
            year = current_year - ((current_month - i - 1) // 12)
            months.append(f"{year}-{month:02d}")  # Format as "YYYY-MM"

        # Map existing data to the months
        monthly_metrics = {month: 0 for month in months}
        for data in monthly_data:
            key = f"{data['year']}-{data['month']:02d}"
            if key in monthly_metrics:
                monthly_metrics[key] = data["total_attempts"]

        return {
            "months": [month.split('-')[1] for month in months],  # Extract month names
            "totals": list(monthly_metrics.values()),
        }

    def weekly_metrics(self):
        """
        Aggregate weekly metrics for the last 7 days.
        """
        end_time = now()
        start_time = end_time - timedelta(days=7)
        query = self.filter(timestamp__gte=start_time, timestamp__lt=end_time)
        weekly_data = query.annotate(day=ExtractDay('timestamp')).values('day').annotate(
            total_attempts=Sum('total_logins') + Sum('failed_attempts'),
            total_logins=Sum('total_logins'),
            failed_attempts=Sum('failed_attempts'),
        ).order_by('day')

        # Ensure all 7 days are represented
        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        weekly_metrics = {day: {"total_attempts": 0} for day in range(1, 8)}
        for data in weekly_data:
            weekly_metrics[data['day']] = {
                "total_attempts": data["total_attempts"],
                "total_logins": data["total_logins"],
                "failed_attempts": data["failed_attempts"],
            }

        return {
            "days": day_names,  # Names of days in order
            "totals": [entry["total_attempts"] for entry in weekly_metrics.values()],
        }

    def daily_metrics(self):
        """
        Aggregate daily metrics for the last 30 days.
        """
        end_time = now()
        start_time = end_time - timedelta(days=30)
        query = self.filter(timestamp__gte=start_time, timestamp__lt=end_time)
        daily_data = query.annotate(day=ExtractDay('timestamp')).values('day').annotate(
            total_attempts=Sum('total_logins') + Sum('failed_attempts'),
            total_logins=Sum('total_logins'),
            failed_attempts=Sum('failed_attempts'),
        ).order_by('day')

        # Ensure all 30 days are represented
        daily_metrics = {day: {"total_attempts": 0} for day in range(1, 31)}
        for data in daily_data:
            daily_metrics[data['day']] = {
                "total_attempts": data["total_attempts"],
                "total_logins": data["total_logins"],
                "failed_attempts": data["failed_attempts"],
            }

        return {
            "days": list(daily_metrics.keys()),
            "totals": [entry["total_attempts"] for entry in daily_metrics.values()],
        }

    def hourly_metrics(self):
        """
        Aggregate hourly metrics for the last 24 hours.
        """
        end_time = now()
        start_time = end_time - timedelta(hours=24)
        query = self.filter(timestamp__gte=start_time, timestamp__lt=end_time)
        hourly_data = query.annotate(hour=ExtractHour('timestamp')).values('hour').annotate(
            total_attempts=Sum('total_logins') + Sum('failed_attempts'),
            total_logins=Sum('total_logins'),
            failed_attempts=Sum('failed_attempts'),
        ).order_by('hour')

        # Ensure all 24 hours are represented
        hourly_metrics = {hour: {"total_attempts": 0} for hour in range(1, 25)}
        for data in hourly_data:
            hourly_metrics[data['hour']] = {
                "total_attempts": data["total_attempts"],
                "total_logins": data["total_logins"],
                "failed_attempts": data["failed_attempts"],
            }

        return {
            "hours": list(hourly_metrics.keys()),
            "totals": [entry["total_attempts"] for entry in hourly_metrics.values()],
        }

    def twelve_hour_metrics(self):
        """
        Aggregate 12-hour metrics for the last 12 hours.
        """
        end_time = now()
        start_time = end_time - timedelta(hours=12)
        query = self.filter(timestamp__gte=start_time, timestamp__lt=end_time)
        hourly_data = query.annotate(hour=ExtractHour('timestamp')).values('hour').annotate(
            total_attempts=Sum('total_logins') + Sum('failed_attempts'),
            total_logins=Sum('total_logins'),
            failed_attempts=Sum('failed_attempts'),
        ).order_by('hour')

        # Ensure all 12 hours are represented
        last_12_hours = [(end_time - timedelta(hours=i)).hour for i in reversed(range(12))]
        hourly_metrics = {hour: {"total_attempts": 0} for hour in last_12_hours}
        for data in hourly_data:
            hourly_metrics[data['hour']] = {
                "total_attempts": data["total_attempts"],
                "total_logins": data["total_logins"],
                "failed_attempts": data["failed_attempts"],
            }

        return {
            "hours": last_12_hours,
            "totals": [entry["total_attempts"] for entry in hourly_metrics.values()],
        }
    
    def yearly_metrics(self):
        """
        Aggregate yearly metrics for the last 5 years.
        """
        end_time = now()
        start_time = end_time - timedelta(days=365 * 5)
        query = self.filter(timestamp__gte=start_time, timestamp__lt=end_time)
        yearly_data = query.annotate(year=ExtractYear('timestamp')).values('year').annotate(
            total_attempts=Sum('total_logins') + Sum('failed_attempts'),
            total_logins=Sum('total_logins'),
            failed_attempts=Sum('failed_attempts'),
        ).order_by('year')

        return {
            "years": [data['year'] for data in yearly_data],
            "totals": [data["total_attempts"] for data in yearly_data],
        }
