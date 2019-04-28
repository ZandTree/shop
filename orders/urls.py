from django.urls import path
from . import views

#from wkhtmltopdf.views import PDFTemplateView

app_name = 'orders'
urlpatterns = [
    path('create-order/',views.CreateOrder.as_view(),name = 'create-order'),
    path('list-orders/',views.ListPreOrder.as_view(),name = 'list-orders'),
    path('delete-order/',views.DeleteOrder.as_view(),name = 'delete-order'),
    path('order-detail/<order_unid>/',views.OrderDetail.as_view(),name = 'order-detail'),
    path('checkout/',views.Checkout.as_view(),name = 'checkout'),
    path('history/',views.OrderHistory.as_view(),name = 'history'),
    path('admin/order/<int:pk>/',views.admin_order_detail, name='admin_order_detail'),
    #path('pdf/', PDFTemplateView.as_view(template_name='orders/pdf.html',
                                           #filename='my_pdf.pdf'), name='pdf'),

]
