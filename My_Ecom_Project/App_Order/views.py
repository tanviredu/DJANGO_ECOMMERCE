from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import Cart,Order
from App_Shop.models import Product


from django.contrib import messages

@login_required
def add_to_cart(request,pk):
    ## fet the item From the product table with id
    item = get_object_or_404(Product,pk=pk)
    print(item)
    ## now make a cart object with the product item
    ## it will create the cart if not it will create one
    ## for every click we default quantity is 1
    order_item = Cart.objects.get_or_create(item=item,user=request.user,purchased=False)
    print(order_item)
    ## we get the item and we get the order object
    ## any loggedin user can do this
    ## now fetch all the cart object which os unpaid  with the current logged in user
    ## all the cart object
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    print(order_qs)
    ## find if the user have any unpaid order
    if order_qs.exists():
        # only one unpaid order will be there
        # because after payment the ordered=True happend
        # and it will not come to the order query
        # we get the unpaid order list
        # why add the [0] when you add index?
        # because when you use filter even if one object
        # retuen it comes in a list
        # we have to take it out from the list
        order = order_qs[0]
        ## order is now the incomplete/unpaid order
        ## now check if inthe order there is multiple same product
        ## then we will increase the quantity
        ## item is the product that he add to cart
        # item is the product
        # if the item  even exists it will come in a list
        ## because of the filter so use index for getting it
        ## out of the list
        if order.orderitems.filter(item=item).exists():
            order_item[0].quantity+=1
            order_item[0].save()
            messages.info(request,"This item quantity is updated")
            return redirect('App_Shop:home')
        else:
            # if not exists
            # then add it to the order
            # dont confuse order_item[0] is a cart object
            order.orderitems.add(order_item[0])
            messages.info(request,"This item is added")
            return redirect('App_Shop:home')
    # else if he does now have any order yet
    #then create the order
    # means he never oder anything like he has not any order
    # object then create one and add the element
    else:
        order = Order(user = request.user)
        order.save()
        order.orderitems.add(order_item[0])
        return redirect('App_Shop:home')

@login_required
def cart_view(request):
    ''' if he wants to see the cart '''
    carts  = Cart.objects.filter(user=request.user,purchased=False)
    orders = Order.objects.filter(user=request.user,ordered=False)

    if carts.exists() and orders.exists():
        ## get the order from the list
        ## one unpaid order but inside a list
        ## so indexing
        order = orders[0]
        return render(request,'App_Order/cart.html',{'carts':carts,'order':order})
    else:
        messages.warning(request,"You dont have any item in your cart")
        return redirect('App_Shop:home')
@login_required
def remove_from_cart(request,pk):
    item = get_object_or_404(Product,pk=pk)
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    ## we dont search the order with product
    ## first we search if we even have any order
    ## if ther is not order so there is no question that
    ## he has no item
    if order_qs.exists():
        order = order_qs[0]
        if order.orderitems.filter(item=item).exists():
            ## if anything in the order
            ## thendefinitly it is in the cart
            ## so search in the cart table
            order_item = Cart.objects.filter(item=item,user=request.user,purchased=False)
            order_item = order_item[0]
            order.orderitems.remove(order_item) ## delete from the order
            order_item.delete() ### now delete from the cart
            messages.warning(request,"This item was removed from your cart")
            return redirect('App_Order:cart')


        else:
            messages.info(request,"Not in your cart")
            return redirect("App_Shop:home")
        
    else:
        ## when he dont have any order?
        ## when he paid everything
        messages.info(request,"You dont have any order")
        return redirect('App_Shop:home')



@login_required
def increase_cart(request,pk):
    item = get_object_or_404(Product,pk=pk)
    order_qs = Order.objects.filter(user = request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.orderitems.filter(item=item).exists():
            order_item = Cart.objects.filter(item=item,user=request.user,purchased=False)
            order_item = order_item[0]
            if order_item.quantity >=1:
                order_item.quantity+=1
                order_item.save()
                messages.info(request,"Quantity is Updated")
                return redirect("App_Order:cart")
        

        else:
            messages.info(request,"Not in your Cart")
    
    else:
        messages.info(request,"you dont have any active order")
        return redirect("App_Shop:home")


@login_required
def decrease_cart(request,pk):
    item = get_object_or_404(Product,pk=pk)
    order_qs = Order.objects.filter(user = request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.orderitems.filter(item=item).exists():
            order_item = Cart.objects.filter(item=item,user=request.user,purchased=False)
            order_item = order_item[0]
            if order_item.quantity >1:
                order_item.quantity -=1
                order_item.save()
                messages.info(request,"Quantity is changed")
                return redirect("App_Order:cart")
            else:
                ## delete from the order
                order.orderitems.remove(order_item) ## from the order
                order_item.delete()    # from the cart
                messages.warning(request,"Product is removed")
                return redirect('App_Order:cart')
        else:
            messages.info(request,"Not in your cart")
            return redirect("App_Shop:home")
    else:
        messages.info(request,"You dont have any active order")
        return redirect("App_Shop:home")
        
