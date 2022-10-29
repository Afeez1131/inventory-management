from cProfile import label
from django.shortcuts import render, get_object_or_404, redirect
from django import template
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from .models import Product, Sale, Customer, Invoice
from datetime import datetime
from django.views.generic import ListView
from .forms import SaleForm, AddProductForm
from django.forms import inlineformset_factory, modelformset_factory
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.contrib.auth import logout
from django.core.mail import send_mail

@staff_member_required
def dashboard(request):
    # if no
    products = Product.objects.all()[:10]
    today_date = datetime.now().date()
    sales = Sale.objects.filter(date=today_date)[:10]
    # today_sales = Sales.objects.filter(timestamp=)

    return render(
        request,
        "home/index.html",
        {
            "products": products,
            "sales": sales,
            "today_date": today_date,
        },
    )


def product_ajax(request):
    products = Product.objects.all()
    product_list = []
    today_date = datetime.now().date()
    sales = Sale.objects.filter(date=today_date)[:10]
    sales_list = []
    for sale in sales:
        sales_list.append(
            {
                "product": sale.product.stock.name,
                "unit": sale.product.unit,
                "qty": sale.qty,
                "buyer_name": sale.customer.name,
                "seller_name": sale.seller_name.full_name,
                "timestamp": sale.timestamp,
                "total_price": sale.total_price,
                "payment_type": sale.payment_type,
                "timestamp": sale.timestamp.strftime("%B %d, %Y, %I:%M %p")
            }
        )

    for product in products:
        product_list.append(
            {
                "product": product.stock.name,
                "unit": product.unit,
                "total_quantity": product.total_quantity,
                "qty_remain": product.qty_remain,
                "qty_sold": product.get_quantity_sold,
            }
        )
    return JsonResponse({"products": product_list,
                        "sales": sales_list}, safe=False)





class AllSales(ListView):
    model = Sale
    today = datetime.now().date()
    paginate_by = 10
    template_name = "home/all_sales.html"

    def get_context_data(self, *args, **kwargs):
        context = super(AllSales, self).get_context_data(*args, **kwargs)
        context["today"] = self.today
        context["sales"] = Sale.objects.filter(date=self.today)
        return context


def AllSalesDate(request, date):
    context = {}

    if not request.user.is_superuser:
        context["page_obj"] = Sale.objects.filter(date=date, seller_name=request.user)
        context["sales"] = Sale.objects.filter(date=date, seller_name=request.user)
    else:
        context["sales"] = Sale.objects.filter(date=date)
        context["page_obj"] = Sale.objects.filter(date=date)
    context["today"] = date
    

    return render(request, "home/all_sales.html", context)


class AllProduct(ListView):
    model = Product
    today = datetime.now().date()
    # queryset = Product.objects.all()
    paginate_by = 5
    template_name = "home/all_product.html"
    # context_object_name = "products"

    def get_context_data(self, **kwargs):
        context = super(AllProduct, self).get_context_data(**kwargs)
        context["products"] = Product.objects.all()
        return context


def edit_sale(request, id):
    sale = get_object_or_404(Sale, id=id)
    form = SaleForm(instance=sale)

    return render(request, "home/edit_sale.html", {"form": form})

from django.db.models import Q
@login_required
def seller(request):
    if not request.user.is_worker and not request.user.is_superuser:
        logout(request)
        return redirect("login")
    # product = Product.objects.all()
    # SaleFormSet = inlineformset_factory(Customer, Sale, fields=('product', 'qty', 'payment_type'), extra=5)
    form = SaleForm()
    # form = SaleFormSet()
    products = Product.objects.all()
    # customers = Customer.objects.all()
    today = datetime.now().date()
    sales = Sale.objects.filter(seller_name=request.user, date=today)
    # print("form: ", form)
    if request.method == "POST":
        form = SaleForm(request.POST)
        # print("form: ", form)
        print(request.POST)
        if form.is_valid():
            sale = form.save(commit=False)
            c_name = request.POST.get('c_name')
            c_number = request.POST.get("c_phone_no")
            c_email = request.POST.get("c_email")
            try:
                customer = Customer.objects.get(Q(phone_number=c_number) | Q(email= c_email))
            except Customer.DoesNotExist:
                customer = Customer.objects.create(phone_number=c_number, email=c_email, name=c_name)

            sale.seller_name = request.user
            sale.customer = customer
            sale.payment_type = request.POST.get("payment_type")
            # sale__invoice.set()
            sale.customer.save()
            sale.save()
            print("Sale: ", sale, sale.payment_type)

            inv = Invoice.objects.create(customer=customer)
            inv = Invoice.objects.get(invoice_id=inv.invoice_id)
            # inv.customer = customer
            inv.sale.add(sale)
            inv.save()

            total_price = inv.sale.all().aggregate(total_price=Sum('total_price'))["total_price"]

            inv.total_price = total_price
            inv.save()

            messages.success(request, "Sales Registered succesfully")
            # return redirect(reverse("invoice_generator", args=[inv.invoice_id]))
            return redirect(reverse("sell_customer", args=[inv.invoice_id, customer.id]))
        else:
            # messages.warning(request, "make sure to enter all field")
            return render(
                request,
                "home/sale.html",
                {
                    "form": form,
                    "products": products,
                    "sales": sales,
                    "today": today,

                },
            )
            # return redirect('sales_page') 2b85ba73d511

    return render(
        request,
        "home/sale.html",
        {
            "form": form,
            "products": products,
            "sales": sales,
            "today": today,

            # "customers": customers,
        },
    )

def sell_customer(request, invoice_id, customer_id):
    if not request.user.is_worker and not request.user.is_superuser:
        logout(request)
        return redirect("login")

    form = SaleForm()
    inv = Invoice.objects.get(invoice_id=invoice_id)
    today = datetime.now().date()
    sales = Sale.objects.filter(seller_name=request.user, date=today)
    customer = Customer.objects.get(id=customer_id)
    payment_type = inv.sale.latest('id').payment_type

    if request.method == "POST":
        form = SaleForm(request.POST)
        print(request.POST)
        if form.is_valid():
            product = form.cleaned_data['product']
            qty = form.cleaned_data['qty']

            sale = Sale.objects.create(product=product, qty=qty, customer=customer, payment_type=payment_type, seller_name=request.user)
            # inv = Invoice.objects.create(customer=customer)
            # inv = Invoice.objects.get(invoice_id=inv.invoice_id)
            # inv.customer = customer
            inv.sale.add(sale)
            inv.save()

            total_price = inv.sale.all().aggregate(total_price=Sum('total_price'))["total_price"]
            print("Total PRICE: ", total_price)

            inv.total = total_price
            inv.save()
            print("Total: ", inv.total)

            messages.success(request, "Sales Registered succesfully")
            return redirect(reverse("sell_customer", args=[inv.invoice_id, customer.id]))


    return render(
        request,
        "home/sell_customer.html",
        {
            "form": form,
            # "products": products,
            "sales": sales,
            "today": today,
            "invoice": inv,

            # "customers": customers,
        },
    )

from .forms import GenerateInvoiceForm
from django.db.models import Sum
from django.contrib.auth import get_user_model
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa


def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()

    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def invoice_generator(request, invoice_id):
    User = get_user_model()
    invoice = Invoice.objects.get(invoice_id=invoice_id)
    form = GenerateInvoiceForm()
    seller_id = list(invoice.sale.all().values('seller_name'))[0]['seller_name']
    seller_name = User.objects.get(id=seller_id).full_name

    # beginning link: https://stackoverflow.com/questions/19630388/django-attach-pisa-generated-pdf-to-email
    # template = get_template('home/invoice.html')
    # html = template.render({"invoice": invoice, "seller_name": seller_name})
    # pdf = BytesIO()
    # end

    pdf = render_to_pdf('home/invoice.html', {"invoice": invoice, "seller_name": seller_name})

    if request.method == "POST":
        try:
            custom_send_mail(request, date=invoice.date, file=pdf)

        except Exception as e:
            return HttpResponse('Error %s' % e)
        return HttpResponse('Message sent')
    # print(seller_name)
    

    # pdf = render_to_pdf('home/invoice_template.html', {"invoice": invoice, })
    # print("PDF:", pdf)

    return render(request, 'home/generate_invoice.html', {"form": form, "invoice": invoice, "seller_name": seller_name})


from django.core.mail import EmailMessage


def custom_send_mail(request, file, date):
    email_subject = "hello from website"
    message = "Attached herein is your purchases invoices dated %s" % date
    from_email = 'temp@gmail.com'
    recipient_list = ['lawalafeez052@gmail.com']
    email = EmailMessage(email_subject, message, from_email, recipient_list)
    email.attach('invoice.pdf', file.getvalue(), 'application/pdf')
    email.send()


def pdf_download(request, invoice_id):
    User = get_user_model()
    invoice = Invoice.objects.get(invoice_id=invoice_id)
    seller_id = list(invoice.sale.all().values('seller_name'))[0]['seller_name']
    seller_name = User.objects.get(id=seller_id).full_name
    
    pdf = render_to_pdf('home/invoice.html', {"invoice": invoice, "seller_name": seller_name})
    return HttpResponse(pdf, content_type='application/pdf')





from django.views.decorators.csrf import csrf_exempt

# @csrf_exempt
def ajax_sale_submit(request):
    if request.is_ajax():
        # print(request.POST.get("product"))
        product = request.POST.get("product")
        quantity = request.POST.get("quantity")
        payment_type = request.POST.get("payment_type")
        customer_name = request.POST.get("customer_name")
        customer_phone = request.POST.get("customer_phone")
        customer_email = request.POST.get("customer_email")

        print(product, quantity, payment_type, customer_phone, customer_email, customer_name, type(customer_name))
        try:
            customer = Customer.objects.get(Q(phone_number=customer_phone) | Q(email= customer_email))
        except Customer.DoesNotExist:
            customer = Customer.objects.create(phone_number=customer_phone, email=customer_email, name=customer_name)

        
        # sale = Sale(
        #     product=Product.objects.get(id=product),
        #     qty=int(quantity),
        #     payment_type=payment_type,
        #     seller_name=request.user
        # )

        # sale.customer = customer
        # sale.save()

        # form = SaleForm(request.POST)
        # if form.is_valid():
        #     product = request.POST.get("product")
        #     buyer_name = request.POST.get("buyer_name")
        #     qty = request.POST.get("qty")
        #     # total_price = request.POST.get("total_price")
        #     payment_type = request.POST.get("payment_type")

        #     sale = Sale(
        #         product=product,
        #         buyer_name=buyer_name,
        #         qty=qty,
        #         payment_type=payment_type,
        #     )
        #     sale.save()

        response = {
                    'msg':'Your form has been submitted successfully' # response message
            }
        return JsonResponse(response)
        # else:
        #     return JsonResponse({"status": "Data not saved"})



def restock(request):
    if request.method == "POST":
        form = AddProductForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data["total_quantity"]
            stock = form.cleaned_data["stock"]
            product = Product.objects.get(stock=stock)
            product.total_quantity += quantity
            product.qty_remain += quantity
            product.save()
            messages.success(
                request, "%s %s of %s stocked" % (quantity, product.unit, stock)
            )
        else:
            messages.warning(request, "there is an error in your form information")

    recent_product = Product.objects.order_by("id")[:5]
    form = AddProductForm()
    return render(
        request,
        "home/restock.html",
        {
            "form": form,
            "recent_product": recent_product,
        },
    )




@login_required(login_url="/login/")
def pages(request):
    context = {}
    # All resource paths end in .html.
    # Pick out the html file name from the url. And load that template.
    try:

        load_template = request.path.split("/")[-1]

        if load_template == "admin":
            return HttpResponseRedirect(reverse("admin:index"))
        context["segment"] = load_template

        html_template = loader.get_template("home/" + load_template)
        return HttpResponse(html_template.render(context, request))

    except template.TemplateDoesNotExist:

        html_template = loader.get_template("home/page-404.html")
        return HttpResponse(html_template.render(context, request))

    except:
        html_template = loader.get_template("home/page-500.html")
        return HttpResponse(html_template.render(context, request))


from django.http import HttpResponse
from django.views.generic import View

from .utils import render_to_pdf  #created in step 4

class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        data = {
             'today': datetime.date.today(), 
             'amount': 39.99,
            'customer_name': 'Cooper Mann',
            'order_id': 1233434,
        }
        pdf = render_to_pdf('pdf/invoice.html', data)
        return HttpResponse(pdf, content_type='application/pdf')