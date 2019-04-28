from django.db import models
from shop.utils import make_unique_slug
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.urls import reverse

from prods.models import Product

class Tag(models.Model):
    """
    make possible search for features not from
    title-description-price only
    """
    title = models.CharField(max_length=120)
    slug = models.SlugField(max_length=120)
    products = models.ManyToManyField(Product,blank=True,related_name='tags')

    def __str__(self):
        return self.title

@receiver(pre_save, sender=Tag)
def tag_presave_receiver(sender, instance,*args,**kwargs):
    if not instance.slug:
        instance.slug = make_unique_id(instance)
pre_save.connect(tag_presave_receiver,sender=Tag)
