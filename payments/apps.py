from django.apps import AppConfig

class PaymentsConfig(AppConfig):
    name = 'payments'
    verbose_name = "Payment"

    def ready(self):
        import payments.signals
