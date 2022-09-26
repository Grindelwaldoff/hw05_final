# Generated by Django 2.2.6 on 2022-09-20 19:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='comments',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Комментарий', 'verbose_name_plural': 'Коментарии'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Пост', 'verbose_name_plural': 'Посты'},
        ),
        migrations.RenameField(
            model_name='comments',
            old_name='created',
            new_name='pub_date',
        ),
        migrations.RenameField(
            model_name='post',
            old_name='created',
            new_name='pub_date',
        ),
    ]
