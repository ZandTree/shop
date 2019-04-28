from django.shortcuts import render,get_object_or_404,redirect
from django.views.generic import View,ListView,DetailView   #FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse,HttpResponse
from prods.models import Cart
from .models import Order
from django.db.models import Sum
from profiles.models import BillingProfile
from profiles.forms import BillingProfileForm

# module for generation PDF
# from wkhtmltopdf.views import PDFTemplateView

# class MyPDF(PDFTemplateView):
#     filename = 'my_pdf.pdf'
#     template_name = 'orders/pdf.html'
#     cmd_options = {
#         'margin-top': 3,
#     }
def admin_order_detail(request,pk):
    """
    function accessible from admin to fetch extra info about
    prods in cart/order
    """
    order = get_object_or_404(Order, id=pk)
    cart = Cart.objects.get(order=order,accepted=True)
    cart_items = cart.cart_items.all()
    return render(request, 'admin/orders/order/detail.html',
            {'order': order,'cart':cart,'items':cart_items})

class ListPreOrder(LoginRequiredMixin,ListView):
    """list of all pre-orders(based on accepted carts) but not paid yet"""
    model = Order
    context_object_name = "orders"
    template_name = 'orders/list_orders.html'

    def get_queryset(self):
        return  Order.objects.filter(cart__user = self.request.user,accepted=False).order_by('-date')

class OrderHistory(LoginRequiredMixin,ListView):
    model = Order
    template_name = 'orders/order-history.html'

    def get_queryset(self):
        return Order.objects.filter(cart__user =            self.request.user,accepted=True,status='paid').order_by('-date')

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['accepted_not_paid_yet_orders'] = Order.objects.filter(cart__user =            self.request.user,accepted=True).exclude(status='paid').order_by('-date')

        return context

class DeleteOrder(LoginRequiredMixin,View):
    """user can remove pre-order from list of orders,
       related cart gets deleted as well
    """
    def post(self,request):
        pk = request.POST.get('pk')
        order = get_object_or_404(Order,id=pk,accepted=False)
        cart = get_object_or_404(Cart,id=order.cart_id,accepted=True)
        order.delete()
        cart.delete()
        return redirect('orders:list-orders')

class CreateOrder(LoginRequiredMixin,View):
    """
    Create a new order with flipping cart status =>
    old one gets status accepted; a new one gets created and goes into session
    Final update cart total(excl shipping)
    """
    # ? def get(in case user stops)
    def post(self,request):
        pk_cart = request.POST.get('pk','pk not found')
        cart = Cart.objects.get(id=pk_cart,accepted=False)
        # final update cart attr total
        cart.get_sum_items_price()
        order = Order.objects.create(cart=cart) # per default accepted=False)
        # calc cart.total + shipping cost
        order.update_total()
        cart.accepted = True
        cart.save()
        new_cart = Cart.objects.create(user=request.user)
        request.session["cart_id"] = new_cart.id
        return redirect('orders:list-orders')

class Checkout(LoginRequiredMixin,View):
    def get(self,request):
        """make final order """
        pk=request.GET.get('pk')
        form = BillingProfileForm(
                instance=BillingProfile.objects.get(user__email=request.user.email)
                )
        order = get_object_or_404(Order,id=pk,accepted=False,cart__user=request.user)
        order.accepted = True
        order.save()
        request.session['order_id'] = order.id
        return render(request,'orders/checkout.html',{'form':form,'order':order})

class OrderDetail(LoginRequiredMixin,DetailView):
    model = Order
    def get_object(self):
        order_unid_ = self.kwargs.get('order_unid')
        return get_object_or_404(Order,order_unid=order_unid_)
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        order = self.get_object()
        cart = Cart.objects.get(order=order,accepted=True)
        cart_items = cart.cart_items.all()
        context['amount'] = cart.get_sum_items_amount()
        context['total_cart'] = cart.get_sum_items_price()
        context['cart_items'] = cart_items
        return context
