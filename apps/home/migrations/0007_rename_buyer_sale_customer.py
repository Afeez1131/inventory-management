# Generated by Django 3.2.6 on 2022-06-23 14:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_rename_buyer_name_sale_buyer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='sale',
            old_name='buyer',
            new_name='customer',
        ),
    ]
