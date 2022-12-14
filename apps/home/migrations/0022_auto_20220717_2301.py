# Generated by Django 3.2.6 on 2022-07-17 22:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0021_alter_invoice_customer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invoice',
            name='sale',
            field=models.ManyToManyField(blank=True, null=True, to='home.Sale'),
        ),
        migrations.AlterField(
            model_name='sale',
            name='payment_type',
            field=models.CharField(blank=True, choices=[('Cash', 'Cash'), ('Bank', 'Bank')], max_length=10, null=True),
        ),
    ]
