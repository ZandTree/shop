from django.db import models
import os
from django.http import Http404
from PIL import Image
from mptt.models import MPTTModel,TreeForeignKey
from shop.utils import make_unique_slug
from django.db.models.signals import pre_save,post_save
from django.dispatch import receiver
from django.urls import reverse
from django.contrib.auth.models import User
# # for search method
from django.db.models import Q,Sum
from django.shortcuts import get_object_or_404



class Category(MPTTModel):
    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120,unique=True)
    parent = TreeForeignKey(
                "self",
                blank=True,
                null=True,
                on_delete=models.CASCADE,
                related_name='kids')
    class MPTTMeta:
        order_insertion_by=['name']

    class Meta:
        verbose_name_plural = 'categories'
    def __str__(self):
        return  self.name

def upload_img_file(instance,filepath):
    """
     shorten filename and pack into folder with title + id
     let op: splitext returns already period='.ext'
    """
    print("loading a file",instance.id)
    filename = os.path.basename(filepath)         # 'abababa.jpeg'
    name,ext = os.path.splitext(filename)         # tuple ('abababa', '.jpeg')
    if len(name) > 5:
         name = name[:5]
    new_file_name = name + ext
    # to correct os.path.join('prod_{0}','{1}').format(instance.id,new_file_name)
    if instance.id:
        return os.path.join('image','prod_{0}','{1}').format(instance.id,new_file_name)
    else:
        return os.path.join('image','prods_load','{}').format(new_file_name)

class ProductManager(models.Manager):
    def search(self,words):
        lookup = (Q(title__icontains=words)|
                        Q(description__icontains=words)|
                        Q(price__icontains=words)|
                        Q(tags__title__icontains=words)
                        # without related_name use just tag_title,tag_slug (through the field)
                        )
        return Product.objects.filter(lookup).distinct()

    def for_sale(self):
        return Product.objects.filter(sale=True)

class Product(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120,blank=True,unique=True)
    price = models.DecimalField(max_digits=10,decimal_places=2)
    description = models.TextField(default="")
    stock = models.BooleanField(default=True)
    new = models.BooleanField(default=False)
    sale = models.BooleanField(default=False)
    photo = models.ImageField(upload_to=upload_img_file,blank=True,null=True)
    categ = models.ForeignKey(Category,on_delete=models.CASCADE,related_name='products')

    objects = ProductManager() # not overriding but extending .objects()

    def __str__(self):
        return self.title
    def get_absolute_url(self,**kwargs):
        return reverse('prods:detail',kwargs={'slug':self.slug})
    class Meta:
        ordering = ['id']

    @property
    def get_photo_url(self,*args,**kwargs):
        """ return path to prod image """
        if self.photo:
            return "/media/{}".format(self.photo)
        else:
            return "/static/images/carrot.jpg/"
    def save(self,*args,**kwargs):
        """ adjust image size"""
        super().save(*args,**kwargs)
        if self.photo:
            img = Image.open(self.photo.path)
            if img.height >525 or img.width >350:
                output_size = (350,550)
                img.thumbnail(output_size)
                img.save(self.photo.path)


class CartManager(models.Manager):
    def new_or_get(self,request,accepted=False):
        """ return cart object for either anonymnus user,or authenticated user"""
        cart_id = request.session.get('cart_id',None)
        qs = Cart.objects.filter(id=cart_id,accepted =False)
        if qs.count() == 1:
            cart_obj = qs.last()
            if request.user.is_authenticated and cart_obj.user is None:
                # user is auth but current cart with user=None
                try:
                    # case: user has already an account but put items into the cart
                    # without login ==> current cart becomes user's; prev gets deleted
                    auth_user_cart = Cart.objects.get(user=request.user,accepted=False)
                    auth_user_cart.delete()
                    #print("prev cart of this user is deleted")
                    cart_obj.user = request.user
                    cart_obj.save()
                except:
                    # user collected item into anonym cart and decided to signup
                    cart_obj.user = request.user
                    cart_obj.save()
                # print("omzet to a formaly anonym cart ==> auth user: Done")
        else:
            if request.user.is_authenticated:
                # request.session['cart_id'] not found: auth user hasn't used cart routs yet
                try:
                    cart_obj = Cart.objects.get(user=request.user,accepted=False)
                    print("found cart of auth user")
                except:
                    cart_obj = Cart.objects.create(user=request.user)
                    print("creating a new cart for auth")
            else:
                # anonymnus user uses cart routs
                cart_obj = Cart.objects.create(user=None)
                print("creating a new cart for anonyn")
            request.session['cart_id'] = cart_obj.id
            print("setting a session cart_id")
        return cart_obj


class Cart(models.Model):
    user = models.ForeignKey(User,blank=True,null=True,on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    changed = models.DateTimeField(auto_now=True)
    accepted = models.BooleanField(default=False)
    total = models.DecimalField(decimal_places=2,
                        max_digits=10,
                        editable=True,
                        null=True,blank=True
                        )
    active = models.BooleanField(default=True)
    objects = CartManager()

    def __str__(self):
        if self.user:
            return "cart id:{} user:{}".format(self.id,self.user.id)
        return  "cart id:{} anonymnus".format(self.id)

    def get_sum_items_price(self):
        """
        return cost  of all products in cart
        """
        total_price = self.cart_items.aggregate(total_price=Sum('sub_total'))
        price = total_price.get('total_price')
        self.total = price
        return price

    def get_sum_items_amount(self):
        """
        return amount of all products in cart
        """
        total_qty = self.cart_items.aggregate(total=Sum('qty'))
        num_items_cart = total_qty.get('total',0)
        if isinstance(num_items_cart,int):
            qty =num_items_cart
        else:
            qty = 0
        return qty


class CartItem(models.Model):
    cart = models.ForeignKey(Cart,on_delete=models.CASCADE,related_name='cart_items')
    product = models.ForeignKey(Product,on_delete=models.CASCADE,related_name='prod_in_carts')
    qty = models.PositiveIntegerField(default=0)
    sub_total = models.DecimalField(decimal_places=2,max_digits=10)

    def save(self,*args,**kwargs):
        """ generate price for each cart_item"""
        self.sub_total = self.product.price *self.qty
        super().save(*args,**kwargs)


@receiver(pre_save, sender=Product)
def product_presave_receiver(sender, instance,*args,**kwargs):
    if not instance.slug:
        instance.slug = make_unique_slug(instance)
pre_save.connect(product_presave_receiver,sender=Product)
