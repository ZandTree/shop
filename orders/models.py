from django.db import models
from prods.models import Cart
from shop.utils import make_unique_id
from django.db.models.signals import pre_save
from django.dispatch import receiver
from decimal import Decimal


ORDER_STATUS_CHOICES = (
    #('in db','to display')
    ('created','Created'),
    ('paid','Paid'),
    ('shipped','Shipped'),

)


class OrderManager(models.query.QuerySet):
    def totals_data(self):
        return self.aggregate(Sum('total'))
    def by_status(self,status="shipped"):
        return self.filter(status=status)

class Order(models.Model):
    order_unid = models.CharField(max_length=120,blank=True) #AB3245
    status = models.CharField(max_length=120,default="created",choices=ORDER_STATUS_CHOICES)
    cart = models.ForeignKey(Cart,related_name='order',on_delete=models.CASCADE)
    accepted = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True )
    shipping_total = models.DecimalField(default=5.00,max_digits=10,decimal_places=2)
    total = models.DecimalField(max_digits=10,decimal_places=2,default=0.00)
    payIdeal_id = models.CharField(max_length=30,blank=True,null=True)
    payment = models.CharField(max_length=12,blank=True,null=True)

    def __str__(self):
        return "This is an order {}".format(self.order_unid)

    def update_total(self):
        """ generate price for each cart_item"""
        new_total = self.cart.total + Decimal(self.shipping_total)
        format_new_total = format(new_total,".2f")
        self.total = format_new_total
        self.save()
        return new_total



def order_id_presave_receiver(sender, instance,*args,**kwargs):
    if not instance.order_unid: # if already created => no need to change
        instance.order_unid = make_unique_id(instance)
        # don't call here save(!)
pre_save.connect(order_id_presave_receiver,sender=Order)
