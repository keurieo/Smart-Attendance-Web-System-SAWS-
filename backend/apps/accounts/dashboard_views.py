"""
Dashboard metrics and views for admin panel
"""
from datetime import timedelta
from django.utils import timezone
from django.db.models import Count, Q, Avg
from apps.accounts.models import User
from apps.attendance.models import Session, AttendanceRecord
from apps.academics.models import Course, Enrollment


class DashboardMetrics:
    """
    Class to calculate and provide dashboard metrics
    """
    
    def __init__(self):
        self.now = timezone.now()
        self.today = self.now.date()
        self.week_ago = self.now - timedelta(days=7)
        self.month_ago = self.now - timedelta(days=30)
    
    def get_total_users(self):
        """Get total number of users"""
        return User.objects.count()
    
    def get_active_sessions(self):
        """Get number of currently active sessions"""
        return Session.objects.filter(
            is_active=True,
            expires_at__gt=self.now
        ).count()
    
    def get_attendance_rate(self):
        """Calculate overall attendance rate as percentage"""
        total_records = AttendanceRecord.objects.count()
        if total_records == 0:
            return 0
        
        present_records = AttendanceRecord.objects.filter(
            status='PRESENT'
        ).count()
        
        rate = (present_records / total_records) * 100
        return round(rate, 1)
    
    def get_total_courses(self):
        """Get total number of courses"""
        return Course.objects.count()
    
    def get_recent_sessions(self, limit=5):
        """Get most recent sessions"""
        return Session.objects.select_related(
            'course', 'teacher'
        ).order_by('-created_at')[:limit]
    
    def get_recent_users(self, limit=5):
        """Get most recently registered users"""
        return User.objects.order_by('-date_joined')[:limit]
    
    def get_user_growth_trend(self):
        """Calculate user growth percentage over last week"""
        users_this_week = User.objects.filter(
            date_joined__gte=self.week_ago
        ).count()
        
        users_last_week = User.objects.filter(
            date_joined__gte=self.week_ago - timedelta(days=7),
            date_joined__lt=self.week_ago
        ).count()
        
        if users_last_week == 0:
            return "+100%" if users_this_week > 0 else "0%"
        
        growth = ((users_this_week - users_last_week) / users_last_week) * 100
        sign = "+" if growth >= 0 else ""
        return f"{sign}{round(growth, 1)}%"
    
    def get_session_growth_trend(self):
        """Calculate session growth percentage over last week"""
        sessions_this_week = Session.objects.filter(
            created_at__gte=self.week_ago
        ).count()
        
        sessions_last_week = Session.objects.filter(
            created_at__gte=self.week_ago - timedelta(days=7),
            created_at__lt=self.week_ago
        ).count()
        
        if sessions_last_week == 0:
            return "+100%" if sessions_this_week > 0 else "0%"
        
        growth = ((sessions_this_week - sessions_last_week) / sessions_last_week) * 100
        sign = "+" if growth >= 0 else ""
        return f"{sign}{round(growth, 1)}%"
    
    def get_attendance_rate_trend(self):
        """Calculate attendance rate change over last week"""
        # This week's attendance rate
        this_week_records = AttendanceRecord.objects.filter(
            marked_at__gte=self.week_ago
        )
        this_week_total = this_week_records.count()
        this_week_present = this_week_records.filter(status='PRESENT').count()
        this_week_rate = (this_week_present / this_week_total * 100) if this_week_total > 0 else 0
        
        # Last week's attendance rate
        last_week_start = self.week_ago - timedelta(days=7)
        last_week_records = AttendanceRecord.objects.filter(
            marked_at__gte=last_week_start,
            marked_at__lt=self.week_ago
        )
        last_week_total = last_week_records.count()
        last_week_present = last_week_records.filter(status='PRESENT').count()
        last_week_rate = (last_week_present / last_week_total * 100) if last_week_total > 0 else 0
        
        if last_week_rate == 0:
            return "+100%" if this_week_rate > 0 else "0%"
        
        change = this_week_rate - last_week_rate
        sign = "+" if change >= 0 else ""
        return f"{sign}{round(change, 1)}%"
    
    def get_course_growth_trend(self):
        """Calculate course growth over last month"""
        courses_this_month = Course.objects.filter(
            created_at__gte=self.month_ago
        ).count()
        
        return f"+{courses_this_month}"
    
    def get_attendance_trend_data(self, days=30):
        """
        Get attendance trend data for chart
        Returns list of dates and attendance rates
        """
        data = []
        for i in range(days):
            date = self.today - timedelta(days=days - i - 1)
            day_start = timezone.make_aware(
                timezone.datetime.combine(date, timezone.datetime.min.time())
            )
            day_end = day_start + timedelta(days=1)
            
            day_records = AttendanceRecord.objects.filter(
                marked_at__gte=day_start,
                marked_at__lt=day_end
            )
            
            total = day_records.count()
            present = day_records.filter(status='PRESENT').count()
            rate = (present / total * 100) if total > 0 else 0
            
            data.append({
                'date': date.strftime('%Y-%m-%d'),
                'rate': round(rate, 1),
                'total': total,
                'present': present
            })
        
        return data
    
    def get_activity_heatmap_data(self):
        """
        Get activity heatmap data (day of week vs hour of day)
        Returns 7x24 grid of activity counts
        """
        # Initialize 7x24 grid (7 days, 24 hours)
        heatmap = [[0 for _ in range(24)] for _ in range(7)]
        
        # Get all attendance records from last 30 days
        records = AttendanceRecord.objects.filter(
            marked_at__gte=self.month_ago
        ).values_list('marked_at', flat=True)
        
        for marked_at in records:
            day_of_week = marked_at.weekday()  # 0 = Monday, 6 = Sunday
            hour = marked_at.hour
            heatmap[day_of_week][hour] += 1
        
        return heatmap
    
    def get_metrics(self):
        """
        Get all dashboard metrics in a single dictionary
        """
        return {
            'total_users': self.get_total_users(),
            'active_sessions': self.get_active_sessions(),
            'attendance_rate': self.get_attendance_rate(),
            'total_courses': self.get_total_courses(),
            'user_growth_trend': self.get_user_growth_trend(),
            'session_growth_trend': self.get_session_growth_trend(),
            'attendance_rate_trend': self.get_attendance_rate_trend(),
            'course_growth_trend': self.get_course_growth_trend(),
            'recent_sessions': self.get_recent_sessions(),
            'recent_users': self.get_recent_users(),
        }


def dashboard_context(request):
    """
    Context processor to inject dashboard metrics into all admin templates
    """
    # Only add metrics for admin pages
    if not request.path.startswith('/admin/'):
        return {}
    
    # Only calculate metrics for authenticated staff users
    if not request.user.is_authenticated or not request.user.is_staff:
        return {}
    
    metrics = DashboardMetrics()
    return {
        'metrics': metrics.get_metrics()
    }
