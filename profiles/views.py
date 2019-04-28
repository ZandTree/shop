from django.shortcuts import render,redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from .forms import BillingProfileForm
from .models import BillingProfile
from django.urls import reverse,reverse_lazy
from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.contrib import messages

class ProfileInfo(LoginRequiredMixin,generic.UpdateView):
    form_class = BillingProfileForm
    template_name = 'profiles/profile.html'
    success_url = '/'
    def get_object(self):
        pk = self.kwargs.get('pk')
        profile_id = BillingProfile.objects.get(user_id=pk)
        return profile_id
    def form_valid(self,form):
        # self.request.phone = form.cleaned_data['phone']
        # self.request.user.last_name = form.cleaned_data['last_name']
        # self.request.user.save()
        messages.success(self.request,'Profile has been updated!')
        return super().form_valid(form)



class AdjustProfile(LoginRequiredMixin,generic.UpdateView):
    """edit profile form during checkout with reverse to payment page"""
    form_class = BillingProfileForm
    template_name = 'profiles/adjust_profile.html'
    def get_object(self):
        pk = self.kwargs.get('pk')
        profile_id = BillingProfile.objects.get(user_id=pk)
        return profile_id
    def get_success_url(self):
        return reverse('payments:pay')

class AccountOverview(generic.TemplateView):
    """
    render customer profile details and support data
    """
    template_name = 'profiles/account-overview.html'
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['email'] = 'contact@mail.com'
        return context


class DeleteAccount(generic.DeleteView):
    model = BillingProfile
    success_url = reverse_lazy('prods:home')
    template_name = 'profiles/ask_before_delete_account.html'

@receiver(post_delete, sender=BillingProfile)
def auto_delete_user(sender, instance, **kwargs):
    """ delete billingprofile.user together with related user"""
    instance.user.delete()
