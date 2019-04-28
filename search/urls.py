from django.urls import path
from . import views

app_name = 'search'

urlpatterns = [
    path('',views.SearchList.as_view(),name='simple-search'),
    # path('sale/',views.SaleList.as_view(),name='sale-search'),

]
