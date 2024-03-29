# Generated by Django 2.2.16 on 2023-05-20 18:46

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userfoodgram',
            options={'verbose_name': 'Имя пользователя', 'verbose_name_plural': 'Имя пользователей'},
        ),
        migrations.AlterField(
            model_name='userfoodgram',
            name='first_name',
            field=models.CharField(max_length=150, verbose_name='Имя пользователя'),
        ),
        migrations.AlterField(
            model_name='userfoodgram',
            name='last_name',
            field=models.CharField(max_length=150, verbose_name='Фамилия пользователя'),
        ),
        migrations.CreateModel(
            name='Follow',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('following', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='following', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='follower', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
