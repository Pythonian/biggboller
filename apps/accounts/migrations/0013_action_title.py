# Generated by Django 5.1.1 on 2024-10-13 06:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0012_alter_profile_options_profile_created_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='action',
            name='title',
            field=models.CharField(default='', max_length=255, verbose_name='title'),
            preserve_default=False,
        ),
    ]
