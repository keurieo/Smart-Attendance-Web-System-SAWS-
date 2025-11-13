# Generated migration for attendance app

from django.conf import settings
import django.contrib.gis.db.models.fields
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('academics', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_at', models.DateTimeField()),
                ('end_at', models.DateTimeField()),
                ('teacher_location', django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326)),
                ('radius_meters', models.IntegerField(validators=[django.core.validators.MinValueValidator(10), django.core.validators.MaxValueValidator(500)])),
                ('status', models.CharField(choices=[('active', 'Active'), ('expired', 'Expired'), ('cancelled', 'Cancelled')], default='active', max_length=20)),
                ('notes', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_sessions', to='academics.course')),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='created_sessions', to=settings.AUTH_USER_MODEL)),
                ('schedule', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attendance_sessions', to='academics.schedule')),
            ],
            options={
                'verbose_name': 'Attendance Session',
                'verbose_name_plural': 'Attendance Sessions',
                'db_table': 'attendance_sessions',
            },
        ),
        migrations.CreateModel(
            name='QRToken',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('token', models.CharField(max_length=500, unique=True)),
                ('code6', models.CharField(max_length=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('expires_at', models.DateTimeField()),
                ('is_revoked', models.BooleanField(default=False)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='qr_tokens', to='attendance.attendancesession')),
            ],
            options={
                'verbose_name': 'QR Token',
                'verbose_name_plural': 'QR Tokens',
                'db_table': 'qr_tokens',
            },
        ),
        migrations.CreateModel(
            name='AttendanceRecord',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marked_at', models.DateTimeField(auto_now_add=True)),
                ('method', models.CharField(choices=[('qr_scan', 'QR Scan'), ('manual_code', 'Manual Code'), ('admin_override', 'Admin Override')], max_length=20)),
                ('student_location', django.contrib.gis.db.models.fields.PointField(blank=True, geography=True, null=True, srid=4326)),
                ('distance_meters', models.FloatField(blank=True, null=True)),
                ('status', models.CharField(choices=[('present', 'Present'), ('absent', 'Absent'), ('rejected', 'Rejected'), ('pending', 'Pending')], max_length=20)),
                ('reason', models.TextField(blank=True)),
                ('flagged_for_review', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('session', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to='attendance.attendancesession')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendance_records', to=settings.AUTH_USER_MODEL)),
                ('token', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attendance_records', to='attendance.qrtoken')),
            ],
            options={
                'verbose_name': 'Attendance Record',
                'verbose_name_plural': 'Attendance Records',
                'db_table': 'attendance_records',
            },
        ),
        migrations.AddIndex(
            model_name='qrtoken',
            index=models.Index(fields=['token'], name='qr_tokens_token_idx'),
        ),
        migrations.AddIndex(
            model_name='qrtoken',
            index=models.Index(fields=['session'], name='qr_tokens_session_idx'),
        ),
        migrations.AddIndex(
            model_name='qrtoken',
            index=models.Index(fields=['code6'], name='qr_tokens_code6_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancesession',
            index=models.Index(fields=['course', 'start_at'], name='attendance_sessions_course_start_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancesession',
            index=models.Index(fields=['created_by'], name='attendance_sessions_created_by_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancesession',
            index=models.Index(fields=['status'], name='attendance_sessions_status_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecord',
            index=models.Index(fields=['session', 'student'], name='attendance_records_session_student_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecord',
            index=models.Index(fields=['student', 'marked_at'], name='attendance_records_student_marked_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecord',
            index=models.Index(fields=['status'], name='attendance_records_status_idx'),
        ),
        migrations.AddIndex(
            model_name='attendancerecord',
            index=models.Index(fields=['flagged_for_review'], name='attendance_records_flagged_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='attendancerecord',
            unique_together={('session', 'student')},
        ),
    ]
