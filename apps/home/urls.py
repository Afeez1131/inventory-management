from django.urls import path, re_path
from datetime import datetime
from apps.home import views

urlpatterns = [
    # The home page
    path("", views.dashboard, name="dashboard"),
    path("all-sales/", views.AllSales.as_view(), name="all_sales"),
    path("all-sales/<date>/", views.AllSalesDate, name="all_sales_date"),
    path("all-product/", views.AllProduct.as_view(), name="all_product"),
    path("edit-sale/<int:id>/", views.edit_sale, name="edit_sale"),
    path("sell/", views.seller, name="sales_page"),
    path("sell/<invoice_id>/<customer_id>", views.sell_customer, name="sell_customer"),
    path("stock-product/", views.restock, name="restock"),

    path('ajax-sale-submit/', views.ajax_sale_submit, name='ajax_sale_submit'),

    path("product-ajax/", views.product_ajax, name='product_ajax'),
    path("invoice/<invoice_id>/", views.invoice_generator, name='invoice_generator'),
    path("invoice/download/<invoice_id>/", views.pdf_download, name='pdf_download'),
    # Matches any html file
    re_path(r"^.*\.*", views.pages, name="pages"),
]
