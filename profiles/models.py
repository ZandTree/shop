from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.urls import reverse

class BillingProfile(models.Model):
    user = models.OneToOneField(User,blank=True,
                null=True,on_delete=models.CASCADE,
                related_name="profile"
                )
    email = models.EmailField(unique=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    first_name = models.CharField(max_length=120,default="")
    last_name = models.CharField(max_length=120,default="")
    country = models.CharField(max_length=120,default="")
    state = models.CharField(max_length=120,default="")
    city = models.CharField(max_length=120,default="")
    district = models.CharField(max_length=120,default="")
    street = models.CharField(max_length=120,default="")
    house_number = models.PositiveIntegerField(default=1)
    toevoegsel = models.CharField(max_length=12,default="")
    postcode = models.CharField(max_length=16,default="")
    phone = models.CharField(max_length=32,default="")
    create_account = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    def get_absolute_url(self):
        return reverse('profiles:profile-info', kwargs={'pk': self.user.id})

def user_created_profile(sender,instance,created,*args,**kwargs):
    if created and instance.email:
        print('creating user')
        BillingProfile.objects.get_or_create(user=instance,email=instance.email)
post_save.connect(user_created_profile,sender=User)
