from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [

    path("<int:pk>/",views.AdjustProfile.as_view(),name='adjust-profile'),
    path("info/<int:pk>/",views.ProfileInfo.as_view(),name='profile-info'),
    #add user.id by account-overview
    path("account-overview/",views.AccountOverview.as_view(),name='account-info'),
    path("account-delete/<int:pk>/",views.DeleteAccount.as_view(),name='account-delete'),

]
