# Generated by Django 3.1 on 2020-08-27 20:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carzones', '0003_remove_carzone_blog_page'),
    ]

    operations = [
        migrations.AddField(
            model_name='carzone',
            name='operating_time',
            field=models.CharField(default='24시간', max_length=10),
        ),
    ]