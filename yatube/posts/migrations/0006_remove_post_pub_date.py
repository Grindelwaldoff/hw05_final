# Generated by Django 2.2.16 on 2022-09-22 16:33

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0005_post_pub_date'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='post',
            name='pub_date',
        ),
    ]
