# Generated by Django 5.1.4 on 2025-02-04 12:03

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('climate_tracker', '0002_useractivity'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='role',
        ),
        migrations.CreateModel(
            name='EnvironmentalObservation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('observation_type', models.CharField(choices=[('air_quality', 'Air Quality'), ('water_quality', 'Water Quality'), ('noise_pollution', 'Noise Pollution'), ('other', 'Other')], max_length=50)),
                ('description', models.TextField(blank=True, null=True)),
                ('latitude', models.FloatField()),
                ('longitude', models.FloatField()),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('photo', models.ImageField(blank=True, null=True, upload_to='observations/')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='SustainabilityScore',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('score', models.FloatField(default=0.0)),
                ('last_updated', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
