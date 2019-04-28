from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import *

class CustomMPTTModelAdmin(MPTTModelAdmin):
    mptt_level_indent = 30
admin.site.register(Category, CustomMPTTModelAdmin)


class ProductAdmin(admin.ModelAdmin):
    list_display = ['title','id','slug','photo']
    class Meta:
        model = Product
admin.site.register(Product,ProductAdmin)
