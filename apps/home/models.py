from django.db import models
from django.db.utils import IntegrityError
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from django.contrib.auth import get_user_model
from uuid import uuid4


USER = get_user_model()


UNIT = (
    ('Unit', 'Unit'),
    ('Kilogram', 'Kilogram'),
    ('Gram', 'Gram'),
    ('Litre', 'Litre'), # 25 litre
    ('Bag', 'Bag'),
    ('Crate', 'Crate'),
    ('Kongo', 'Kongo'),
    ('Carton', 'Carton'),
)


PAYMENT_TYPE = (
    ('Cash', 'Cash'),
    ('Bank', 'Bank'),
)


class Stock(models.Model):
    name = models.CharField(max_length=100, unique=True)
    # unit = models.CharField(max_length=100, choices=UNIT) 

    def __str__(self):
        return self.name


class Product(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    unit = models.CharField(max_length=100, choices=UNIT)
    description = models.TextField(blank=True, null=True)
    total_quantity = models.PositiveIntegerField(default=0)
    qty_remain = models.PositiveIntegerField(default=0, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    price_per_one = models.PositiveIntegerField(default=0)

    def __str__(self):
        return '%s (%s)' %(self.stock.name, self.unit)

    class Meta:
        ordering = ('-id', )
        # unique_together = ('stock', 'unit')

    @property
    def stock_level(self):
        result = (self.qty_remain / self.total_quantity) * 100
        return "{:.2f}".format(result)

    @property
    def get_quantity_sold(self):
        return self.total_quantity - self.qty_remain

@receiver(post_save, sender=Product)
def set_the_value_for_quantity_remain_on_initial_save(sender, created, instance, **kwargs):
    if created:
        instance.qty_remain += instance.total_quantity
        instance.save()


class Customer(models.Model):
    name = models.CharField(max_length=100)
    # customer_id =
    email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=11)

    def __str__(self):
        return self.name


class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    # customer = models.CharField(max_length=255, blank=True)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    seller_name = models.ForeignKey(USER, on_delete=models.CASCADE, blank=True)
    qty = models.PositiveIntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    date = models.DateField(auto_now=True, blank=True)
    total_price = models.PositiveIntegerField(default=0, null=True, blank=True)
    payment_type = models.CharField(max_length=10, choices=PAYMENT_TYPE, blank=True, null=True)
    # price = models.PositiveIntegerField(default=0)

    @property
    def calculate_price(self):
        return self.product.price_per_one * self.qty


    def save(self, *args, **kwargs):
        if not self.total_price:
            self.total_price = self.product.price_per_one * self.qty
        super().save(*args, **kwargs)

    def __str__(self):
        return '%s: %s' % (self.product.stock.name, self.product.unit)


    class Meta:
        ordering = ('-id', )

@receiver(pre_save, sender=Sale)
def update_product_quantity_remaining_after_selling(sender, instance, **kwargs):
    # if created:t
    # if instance.product.q
    instance.product.qty_remain -= instance.qty
    instance.product.save()


class Invoice(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField( blank=True, null=True)
    sale = models.ManyToManyField(Sale, null=True, blank=True)
    total = models.PositiveIntegerField(null=True, blank=True)
    invoice_id = models.CharField(max_length=255, unique=True, blank=True)

    def __str__(self):
        return '%s: %s' % (self.customer, self.invoice_id)

    # def save(self, *args, **kwargs):
    #     print("Instance: ", self)
    #     if not self.invoice_id:
    #         uuid = str(uuid4()).split('-')[4]
    #         invoice = Invoice.objects.filter(invoice_id=uuid).exists()
    #         while invoice:
    #             uuid = str(uuid4()).split('-')[4]
    #         self.invoice_id = uuid
    #         self.save()
    #     super(Invoice, self).save(*args, **kwargs)
        # list_sale = [sale.total_price for sale in self.sale.all()]
        # print(list_sale)
        # total = 0
        # for price in list_sale:
        #     total += price
        # print('Total: ', total)
        # print(self, self.total)
        # self.total = total
        # self.save()
        # super().save(*args, **kwargs)

@receiver(post_save, sender=Invoice)
def populate_uuid_field(sender, instance, created, **kwargs):
    if created:
        print("Instance: ", instance)
        if not instance.invoice_id:
            uuid = str(uuid4()).split('-')[4]
            invoice = Invoice.objects.filter(invoice_id=uuid).exists()
            while invoice:
                uuid = str(uuid4()).split('-')[4]
            instance.invoice_id = uuid
            instance.save()


# from django.db.models import Sum

    # total_price = instance.sale.all().aggregate(total_price=Sum('total_price'))["total_price"]

    # instance.total_price = total_price
    # instance.save()
       
