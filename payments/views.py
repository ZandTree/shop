from django.shortcuts import render,get_object_or_404,redirect
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal
from django.conf import settings
from django.urls import reverse
from django.views.generic import View,TemplateView,DetailView
from orders.models import Order
from django.shortcuts import get_object_or_404
#paypal
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.models import ST_PP_COMPLETED
from paypal.standard.ipn.signals import valid_ipn_received
#stripe
import stripe
import pprint
from django.http import JsonResponse,HttpResponse,HttpResponseRedirect
#ideal
import mollie
from mollie.api.client import Client
from mollie.api.error import Error
import time

class PayIdealStart(View):
    def get(self,request):
        mollie_client = Client()
        mollie_client.set_api_key(settings.IDEAL_API)
        # mollie_client.methods.get('ideal', include='issuers,pricing')
        list_bank = mollie_client.methods.get('ideal', include='issuers')
        # list_bank = mollie_client.methods.get(mollie.api.objects.Method.IDEAL, include='issuers')
        return render(request,'payments/iDeal/start_ideal.html',{'list_bank':list_bank})

    def post(self,request):
        try:
            order_unid = request.session.get('order_id')
            order = get_object_or_404(Order,id=order_id)
            mollie_client = Client()
            mollie_client.set_api_key(settings.IDEAL_API)
            selectedIssuerId = request.POST.get("issuer",None)
            #pprint.pprint(request.POST.form)
            my_web_shop_id = int(time.time())
            print("starting collecting data for payment")
            # Payment parameters:
            payment = mollie_client.payments.create({
                'amount': {
                'currency': 'EUR',
                'value': '10.00'
                },
                'description': 'My first API payment',
                'redirectUrl': 'http://localhost:8000/start-ideal/',
                'webhookUrl': 'https://webhook.site/39caa308-2951-4e04-896d-f0ebb7a99a2e',
                'metadata':{'my_web_shop_id':str(my_web_shop_id)},
                'method': 'ideal',
                'issuer':selectedIssuerId

            })
            # In this example we store the order with its payment status in a database.
            status = payment.status
            data = {'status': payment.status}
            order.payIdeal_id = payment.id
            order.payment = 'ideal'
            order.save()
            request.session['ideal']= payment.id
            return redirect('payments:checkout-url')
        except Error as err:
            print('API call failed: {error}'.format(error=err))
            return redirect('payments:checkout-url')
            #return JsonResponse({"err":"error"})


class CheckoutIdeal(View):
    """
    after getting payment id, saving it in db,redirected customer to
    this point to Checkout through iDEAL
    """
    def get(self,request):
        print("welcome to chechout iDEAL")
        payment_id = request.session.get('ideal',None)
        if payment_id:
            mollie_client = Client()
            mollie_client.set_api_key("test_VsePnmyEn7BU6QEKjntaU2R59QxSAK")   #settings.IDEAL_API)
            payment = mollie_client.payments.get(payment_id)
            if payment.is_paid():
                print('Payment received.')
                msg = "paid"
            else:
                print("Got through payment but not paid")
                msg = "status: {}".format(payment.status)
        else:
            print("No paiment Id detected")

        return render(request,'payments/iDEAL/ideal_checkout.html',{"msg":msg})

class MollieWebHook(View):
    def get(self,request):
        msg = "coming ...."
        return render(request,'payments/ideal_webhook.html',{"msg":msg})

class PayPalPayment(View):
    """Payment through PayPay"""
    def get(self,request):
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order,id=order_id)
        order.payment = 'paypal'
        order.save()
        host = request.get_host()
        paypal_dict = {
            'business':settings.PAYPAL_RECEIVER_EMAIL,
            'amount' :'%.2f'%order.total.quantize(Decimal('.01')),
            'item_name':'Order {}'.format(order.order_unid),
            'invoice':str(order.id),#id will be used later in signal
            'currency_code':'EUR', #USD',
            'notify_url':'http://{}{}'.format(host,reverse('paypal-ipn')),
            'return_url':'http://{}{}'.format(host,reverse('payments:done')),
            'cancel_return':'http://{}{}'.format(host,reverse('payments:canceled'))
        }
        form = PayPalPaymentsForm(initial=paypal_dict)
        return render(request,'payments/process.html', {'order':order,'form':form})

@csrf_exempt
def payment_done(request):
    return render(request, 'payments/PayPal/done.html')
@csrf_exempt
def payment_canceled(request):
    return render(request, 'payments/PayPal/canceled.html')


class StripeCharge(View):
    def get(self,request):
        context = {}
        context['publish_key'] = settings.STRIPE_PUBLISHABLE_KEY
        return render(request,'payments/Stripe/start_stripe.html',context)

    def post(self,request):
        stripe.api_key = settings.SRTIPE_SECRET_KEY
        token = request.POST['stripeToken']
        order_id = request.session.get('order_id')
        order = get_object_or_404(Order,id=order_id)
        order.payment = 'stripe'
        order.save()
        description =  "Payment for order #{}".format(order.order_unid)
        try:
            charge  = stripe.Charge.create(
                    #customer = customer.id,
                    amount = int(order.total*100),
                    currency= "usd",   #"jpy",
                    description=description,
                    # using unique token for this user from Stripe
                    source = token,
                    receipt_email = request.user.email

            )
            pprint.pprint(charge)

            return redirect('payments:stripe_success')
        except stripe.error.CardError as err:
            # in case: car is declined
            context = self.get_context_data()
            context ['message'] = 'Your payment cannot be completed.The card has been declined.'
            return render('payments/Stripe/start_stripe.html')


        #return render(request,'payments/success_stripe.html')
        #return JsonResponse({"message":"Done"})
        #raise HttpResponse("error",status_code=401)

class StripeSuccess(TemplateView):
    template_name = 'payments/Stripe/stripe_success.html'


class StripeCharge(TemplateView):
    def post(self,request):
        print(request.POST)
        stripe.api_key = settings.SRTIPE_SECRET_KEY
        customer = stripe.Customer.create(
            email = request.user.email,
            source = request.POST['stripeToken']
        )
        charge  = stripe.Charge.create(
            #customer = customer.id,
            amount = 500,
            currency="usd",
            description='Pay Now',
            # using unique token for this user from Stripe
            source = request.POST['stripeToken']

        )
        return render(request,'payments/charge_stripe.html')

class StripePayment(TemplateView):
    """ To start payment through Stripe payment system"""
    template_name = 'payments/start_stripe.html'

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['key'] = settings.STRIPE_PUBLISHABLE_KEY
        return context


class OrderChargeView(View):
    def post(self, request, *args, **kwargs):
        stripe.api_key = settings.STRIPE_SECRET_KEY
        json_data = json.loads(request.body)
        course = Order.objects.filter(id=json_data['order.id']).first()
        try:
            customer = stripe.Customer.create(
                email=self.request.user.email,
                source=json_data['token'],
                stripe_account=course.seller.stripe_user_id,
            )
            charge = stripe.Charge.create(
                amount=json_data['amount'],
                currency='usd',
                customer=customer.id,
                description=json_data['description'],
                stripe_account=course.seller.stripe_user_id,
            )
            if charge:
                return JsonResponse({'status': 'success'}, status=202)
        except stripe.error.StripeError as e:
            return JsonResponse({'status': 'error'}, status=500)
