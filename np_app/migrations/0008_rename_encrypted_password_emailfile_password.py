# Generated by Django 4.2.5 on 2023-11-09 00:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('np_app', '0007_remove_emailfile_password_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailfile',
            old_name='encrypted_password',
            new_name='password',
        ),
    ]
