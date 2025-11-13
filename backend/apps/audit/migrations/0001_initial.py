# Generated migration for audit app

from django.conf import settings
import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AuditLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=100)),
                ('target_table', models.CharField(max_length=100)),
                ('target_id', models.BigIntegerField()),
                ('old_data', models.JSONField(blank=True, null=True)),
                ('new_data', models.JSONField(blank=True, null=True)),
                ('performed_at', models.DateTimeField(auto_now_add=True)),
                ('performed_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='audit_logs', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Audit Log',
                'verbose_name_plural': 'Audit Logs',
                'db_table': 'audit_logs',
                'ordering': ['-performed_at'],
            },
        ),
        migrations.CreateModel(
            name='LocationSnapshot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('recorded_at', models.DateTimeField(auto_now_add=True)),
                ('location', django.contrib.gis.db.models.fields.PointField(geography=True, srid=4326)),
                ('source', models.CharField(choices=[('browser_geolocation', 'Browser Geolocation'), ('gps', 'GPS'), ('manual', 'Manual')], max_length=50)),
                ('accuracy', models.FloatField(blank=True, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='location_snapshots', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Location Snapshot',
                'verbose_name_plural': 'Location Snapshots',
                'db_table': 'location_snapshots',
                'ordering': ['-recorded_at'],
            },
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_id', models.CharField(max_length=255, unique=True)),
                ('device_info', models.JSONField()),
                ('last_seen', models.DateTimeField(auto_now=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='devices', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Device',
                'verbose_name_plural': 'Devices',
                'db_table': 'devices',
            },
        ),
        migrations.AddIndex(
            model_name='locationsnapshot',
            index=models.Index(fields=['user', 'recorded_at'], name='location_snapshots_user_recorded_idx'),
        ),
        migrations.AddIndex(
            model_name='locationsnapshot',
            index=models.Index(fields=['recorded_at'], name='location_snapshots_recorded_idx'),
        ),
        migrations.AddIndex(
            model_name='device',
            index=models.Index(fields=['user'], name='devices_user_idx'),
        ),
        migrations.AddIndex(
            model_name='device',
            index=models.Index(fields=['device_id'], name='devices_device_id_idx'),
        ),
        migrations.AddIndex(
            model_name='device',
            index=models.Index(fields=['last_seen'], name='devices_last_seen_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['performed_by', 'performed_at'], name='audit_logs_performed_by_at_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['target_table', 'target_id'], name='audit_logs_target_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['action'], name='audit_logs_action_idx'),
        ),
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(fields=['performed_at'], name='audit_logs_performed_at_idx'),
        ),
    ]
