# Generated by Django 3.2.6 on 2022-06-23 15:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0015_alter_product_price_per_one'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='total',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_per_one',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='sale',
            name='total_price',
            field=models.PositiveIntegerField(blank=True, default=0, null=True),
        ),
    ]
