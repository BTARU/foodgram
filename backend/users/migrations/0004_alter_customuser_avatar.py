# Generated by Django 3.2.3 on 2024-06-06 12:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20240531_0304'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='avatar',
            field=models.ImageField(default=None, null=True, upload_to='user_avatars'),
        ),
    ]
