# Generated by Django 5.1.1 on 2024-10-12 02:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_ticket_reply'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ticket',
            name='created',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
