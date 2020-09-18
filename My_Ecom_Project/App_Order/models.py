from django.db import models
from django.conf import settings
from App_Shop.models import Product

# you can't directly import the user. you change the user table
# so we use settings.AUTH_USER_MODEL to autometically search the user model

class Cart(models.Model):
    ## cart has relation with user
    user      = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="cart")
    ## item in the cart fetch from the Product
    item      = models.ForeignKey(Product,on_delete=models.CASCADE)
    quantity  = models.IntegerField(default=1)
    purchased = models.BooleanField(default=False)
    created   = models.DateTimeField(auto_now_add=True)
    updated   = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{} X {} ".format(self.quantity,self.item)

    def get_total(self):
         # self.item is a product it has a price attr 
         total = self.item.price * self.quantity
         float_total = format(total,'0.2f')
         return float_total

class Order(models.Model):
    # a cart objet has a speecfic item
    # a user can have multiple cart object if he order multiple types of
    # product
    # and different different user can have the same product mens cart object
    # so we need many to many relation
    # where which cart-object ---- which-order
    # order class have orders attribute it hold all the different cart object
    # of the user with a pivot table
    # after payment all the cart goes to one order
    # many order may have the same Cart
    orderitems = models.ManyToManyField(Cart)
    user       = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    ordered    = models.BooleanField(default=False)
    created    = models.DateTimeField(auto_now_add=True)
    paymentId  = models.CharField(max_length=300,blank=True,null=True)
    orderId    = models.CharField(max_length=200,blank=True,null=True)

    def get_totals(self):
        ''' total = sum(order_itemXquantity)'''
        total = 0
        for order_item in self.orderitems.all():
            total += float(order_item.get_total())
        return total
        

