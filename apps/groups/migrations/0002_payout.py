# Generated by Django 5.1.1 on 2024-12-05 21:50

import django.db.models.deletion
import uuid
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Payout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('payout_id', models.UUIDField(default=uuid.uuid4, editable=False, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, help_text='The winning amount the bettor is paid.', max_digits=10, verbose_name='Amount')),
                ('status', models.CharField(choices=[('A', 'Approved'), ('C', 'Cancelled')], default='A', max_length=1, verbose_name='Status')),
                ('paid_on', models.DateTimeField(blank=True, null=True)),
                ('bundle', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payouts', to='groups.bundle', verbose_name='Bundle')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='payouts', to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Payout',
                'verbose_name_plural': 'Payouts',
                'ordering': ['-paid_on', '-created'],
            },
        ),
    ]
