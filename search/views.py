from django.shortcuts import render
from django.views.generic import ListView
from prods.models import Product
from django.db.models import Q
import operator
from functools import reduce


class SearchList(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'search/view_search.html'
    paginate_by = 6

    def get_queryset(self,*args,**kwargs):
        words = self.request.GET.get('q')
        if words is not None:
            qs = Product.objects.all()
            query_list = words.split()
            lookup = qs.filter(
                            reduce(operator.or_,
                                   (Q(title__icontains=word) for word in query_list)) |
                            reduce(operator.or_,
                                   (Q(description__icontains=word) for word in query_list))
                        )
            return lookup
        if  not lookup:
            return Product.objects.search(words)
        else:
            print('nothing; just nothing')
            return Product.objects.none()

class SaleList(ListView):
    model = Product
    context_object_name = 'products'
    template_name = 'search/view_search.html'

    def get_queryset(self,*args,**kwargs):
        return Product.objects.for_sale()
