# Generated by Django 3.2.6 on 2022-06-23 15:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0013_alter_invoice_total'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='total',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=6, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='price_per_one',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=6),
        ),
        migrations.AlterField(
            model_name='sale',
            name='total_price',
            field=models.DecimalField(blank=True, decimal_places=2, default=0.0, max_digits=6, null=True),
        ),
    ]
