# Generated by Django 3.2.3 on 2024-06-20 12:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_subscription'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_subscribed',
        ),
    ]
