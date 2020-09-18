from django.shortcuts import render,HttpResponseRedirect,redirect
from django.urls import reverse
from django.contrib import messages
from App_Order.models import Order,Cart
from .models import BillingAddress
from .forms import BillingForm
from django.contrib.auth.decorators import login_required
# Create your views here.

import requests
from sslcommerz_python.payment import SSLCSession
from decimal import Decimal
import socket
from django.views.decorators.csrf import csrf_exempt


@login_required
def checkout(request):
    saved_address = BillingAddress.objects.get_or_create(user = request.user)
    saved_address = saved_address[0]
    form = BillingForm(instance=saved_address)
    if request.method == "POST":
        form = BillingForm(request.POST,instance=saved_address)
        if form.is_valid():
            form.save()
            form = BillingForm(instance=saved_address)
            messages.success(request,'Shipping Address is saved')
    
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    order_qs = order_qs[0]
    order_items = order_qs.orderitems.all()
    order_total = order_qs.get_totals()
    return render(request,"App_Payment/checkout.html",{'form':form,'order_items':order_items,'order_total':order_total,'saved_address':saved_address})


@login_required
def payment(request):
    saved_address = BillingAddress.objects.get_or_create(user=request.user)[0]
    if not saved_address.is_fully_filled():
        messages.info(request,"please Complete shipping address")
        return redirect("App_Payment:checkout")
    
    if not request.user.profile.is_fully_filled():
        messages.info(request,"Please complete Profile details")
        return redirect("App_LOgin:profile")

    store_id = "test5f63e7c01865f"
    API_Key  = "test5f63e7c01865f@ssl"
    mypayment = SSLCSession(sslc_is_sandbox=True,sslc_store_id=store_id,sslc_store_pass=API_Key)
    status_url = request.build_absolute_uri(reverse("App_Payment:complete"))
    ## set the same url and show diffent notification
    mypayment.set_urls(success_url=status_url, fail_url=status_url, cancel_url=status_url, ipn_url=status_url)
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    order_qs = order_qs[0]
    order_items = order_qs.orderitems.all()
    order_items_count = order_qs.orderitems.count()
    order_total = order_qs.get_totals()
    mypayment.set_product_integration(total_amount=Decimal(order_total), currency='BDT', product_category='Mixed', product_name=order_items, num_of_item=order_items_count, shipping_method='Courier', product_profile='None')
    current_user = request.user
    mypayment.set_customer_info(name=current_user.profile.full_name, email=current_user.email, address1=current_user.profile.address_1, address2=current_user.profile.address_1, city=current_user.profile.city, postcode=current_user.profile.zipcode, country=current_user.profile.country, phone=current_user.profile.phone)
    mypayment.set_shipping_info(shipping_to=current_user.profile.full_name, address=saved_address.address, city=saved_address.city, postcode=saved_address.zipcode, country=saved_address.country)
    response_data = mypayment.init_payment()
    print(response_data)
    return redirect(response_data['GatewayPageURL'])



## payment gateway reply with a POST data
## so make to disable the csrf verification
## for this case

@csrf_exempt
def complete(request):
    if request.method == "POST" or request.method == "post":
        payment_data = request.POST
        status = payment_data['status']
        if status == "VALID":
            val_id  = payment_data['val_id']
            tran_id = payment_data['tran_id']
            messages.success(request,"Payment Successfull") 
            return HttpResponseRedirect(reverse("App_Payment:purchase",kwargs={'val_id':val_id,'tran_id':tran_id}))
        elif status == "FAILED":
            messages.success(request,"Payment Failed")
        
    return render(request,'App_Payment/complete.html',context={})

## when the complete method call the purchage method it will change
## the ordered from False to true

@login_required
def purchase(request,val_id,tran_id):
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    order = order_qs[0]
    ##chaging the status
    ## remember orderid in the table is the equivalednt of tran id
    ## and payment id in table is equivalednt to val_id
    orderId = tran_id
    order.ordered = True
    order.orderId = tran_id
    order.paymentId = val_id
    order.save()
    ## order complete
    ## now chnage the cart purchaged =True
    cart_items = Cart.objects.filter(user = request.user,purchased=False)
    for item in cart_items:
        item.purchased = True 
        item.save()
    return HttpResponseRedirect(reverse("App_Shop:home"))



@login_required
def order_view(request):
    try:
        ## now you search for the order that is processed
        ## means ordered=True
        orders = Order.objects.filter(user=request.user,ordered=True)
        context = {'orders':orders}
    except:
        messages.warning(request,"You do not have an active order")
        return redirect("App_Shop:home")
    return render(request,"App_Payment/order.html",context=context)