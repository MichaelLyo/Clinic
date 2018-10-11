# Generated by Django 2.1 on 2018-10-11 09:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MyClinic', '0003_auto_20181006_1706'),
    ]

    operations = [
        migrations.AddField(
            model_name='medication',
            name='sale_mode',
            field=models.IntegerField(choices=[(0, '零售价'), (1, '批发价')], default=0, verbose_name='销售模式'),
        ),
    ]
