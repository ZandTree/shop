from django.urls import path
from . import views

app_name = 'payments'
urlpatterns = [
    path('payment_paypal/',views.PayPalPayment.as_view(),name = 'pay'),
    path('done/',views.payment_done,name='done'),
    path('canceled/',views.payment_canceled,name='canceled'),
    #path('payment_stripe/',views.StripePayment.as_view(),name = 'start_stripe'),
    #path('charge/',views.StripeCharge.as_view(),name="stripe_charge"),
    path('start-stripe/',views.StripeCharge.as_view(),name="start_stripe"),
    path('stripe-success/',views.StripeSuccess.as_view(),name="stripe_success"),
    path('start-ideal/',views.PayIdealStart.as_view(),name="start_ideal"),
    path('checkout-ideal/',views.CheckoutIdeal.as_view(),name="checkout-url"),
    path('mollie-webhook/',views.MollieWebHook.as_view(),name="mollie-webhook"),


]
