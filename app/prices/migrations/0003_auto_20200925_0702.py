# Generated by Django 3.1.1 on 2020-09-25 07:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('prices', '0002_auto_20200924_1546'),
    ]

    operations = [
        migrations.RenameField(
            model_name='carprice',
            old_name='weekday_price_per_min',
            new_name='weekday_price_per_ten_min',
        ),
        migrations.RenameField(
            model_name='carprice',
            old_name='weekend_price_per_min',
            new_name='weekend_price_per_ten_min',
        ),
        migrations.RenameField(
            model_name='insurancefee',
            old_name='light_price_per_min',
            new_name='light_price_per_ten_min',
        ),
        migrations.RenameField(
            model_name='insurancefee',
            old_name='special_price_per_min',
            new_name='special_price_per_ten_min',
        ),
        migrations.RenameField(
            model_name='insurancefee',
            old_name='standard_price_per_min',
            new_name='standard_price_per_ten_min',
        ),
    ]