from django.contrib import admin
from .models import Product, Sale, Stock, Customer, Invoice
from django.contrib.auth.admin import UserAdmin


class ProductAdmin(admin.ModelAdmin):
    list_display = ['stock', 'unit', 'total_quantity', 'qty_remain', 'timestamp']


class SaleAdmin(admin.ModelAdmin):
    list_display = ['customer', 'seller_name', 'qty', 'date', 'payment_type']


admin.site.register(Product, ProductAdmin)
admin.site.register(Stock)
admin.site.register(Customer)
admin.site.register(Invoice)
admin.site.register(Sale, SaleAdmin)
