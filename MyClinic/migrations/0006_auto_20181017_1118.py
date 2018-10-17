# Generated by Django 2.1 on 2018-10-17 03:18

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('MyClinic', '0005_auto_20181011_2056'),
    ]

    operations = [
        migrations.AddField(
            model_name='drug',
            name='validity_date',
            field=models.DateField(default=django.utils.timezone.now, verbose_name='有效期'),
        ),
        migrations.AlterField(
            model_name='drug',
            name='unit',
            field=models.CharField(blank=True, choices=[('盒', '盒'), ('瓶', '瓶'), ('支', '支'), ('袋', '袋'), ('包', '包'), ('箱', '箱'), ('板', '板'), ('根', '根'), ('片', '片')], default='盒', max_length=40, null=True, verbose_name='单位'),
        ),
        migrations.AlterField(
            model_name='drug',
            name='validity_period',
            field=models.CharField(blank=True, default=' ', max_length=40, null=True, verbose_name='有效时长'),
        ),
    ]
