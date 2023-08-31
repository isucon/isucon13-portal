# Generated by Django 4.2.4 on 2023-08-31 01:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0002_team_is_guest'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now, verbose_name='作成日時'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='team',
            name='declined_at',
            field=models.DateTimeField(blank=True, null=True, verbose_name='辞退日時'),
        ),
        migrations.AddField(
            model_name='team',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, verbose_name='最終更新日時'),
        ),
    ]
