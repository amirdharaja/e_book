# Generated by Django 3.0.3 on 2020-04-10 06:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('book_service', '0003_loginhistory'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='email_id',
            new_name='email',
        ),
    ]