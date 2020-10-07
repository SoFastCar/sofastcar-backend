# Generated by Django 3.1.1 on 2020-10-07 03:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('cars', '0003_cartimetable_zone'),
    ]

    operations = [
        migrations.CreateModel(
            name='InsuranceFee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('light_price', models.PositiveIntegerField(default=0)),
                ('standard_price', models.PositiveIntegerField(default=0)),
                ('special_price', models.PositiveIntegerField(default=0)),
                ('light_price_per_ten_min', models.PositiveIntegerField(default=0)),
                ('standard_price_per_ten_min', models.PositiveIntegerField(default=0)),
                ('special_price_per_ten_min', models.PositiveIntegerField(default=0)),
                ('car', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='insurances', to='cars.car')),
            ],
        ),
        migrations.CreateModel(
            name='Coupon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expire_date_time', models.DateTimeField(help_text='만료시간')),
                ('title', models.CharField(help_text='쿠폰명', max_length=100)),
                ('limit_delta_term', models.PositiveIntegerField(default=0, help_text='N일이상 예약 제한 체크용')),
                ('discount_fee', models.PositiveIntegerField(default=0, help_text='할인금액')),
                ('is_enabled', models.BooleanField(default=True, help_text='사용가능여부')),
                ('will_use_check', models.BooleanField(default=False, help_text='사용시체크')),
                ('is_used', models.BooleanField(default=False, help_text='사용했는지여부')),
                ('is_free', models.BooleanField(default=False, help_text='무료쿠폰여부')),
                ('description', models.CharField(help_text='부가설명', max_length=160, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='TimeStamp')),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('member', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='coupons', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CarPrice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('standard_price', models.PositiveIntegerField(default=0)),
                ('min_price_per_km', models.PositiveIntegerField(default=0)),
                ('mid_price_per_km', models.PositiveIntegerField(default=0)),
                ('max_price_per_km', models.PositiveIntegerField(default=0)),
                ('weekday_price_per_ten_min', models.PositiveIntegerField(default=0)),
                ('weekend_price_per_ten_min', models.PositiveIntegerField(default=0)),
                ('car', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='carprice', to='cars.car')),
            ],
        ),
    ]
