# Generated by Django 3.2.6 on 2022-06-23 15:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_rename_buyer_sale_customer'),
    ]

    operations = [
        migrations.CreateModel(
            name='Invoice',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('due_date', models.DateTimeField()),
                ('total', models.IntegerField()),
                ('invoice_id', models.UUIDField(default=['47ab4d5d', 'cead', '4f81', '993c', '50b8b37002ad'])),
                ('customer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.customer')),
                ('sale', models.ManyToManyField(to='home.Sale')),
            ],
        ),
    ]
