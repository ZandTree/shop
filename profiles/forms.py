from django import forms
from profiles.models import BillingProfile
from django.core import validators

class BillingProfileForm(forms.ModelForm):
    first_name = forms.CharField(required=False)
    district = forms.CharField(required=False)
    toevoegsel = forms.CharField(required=False)
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.fields['email'].label="Your email"
        self.fields['first_name'].label = 'First Name'
        self.fields['first_name'].help_text = 'Not required'
        self.fields['district'].label = 'District/Provintie/Regio'
        self.fields['district'].help_text = 'Not required'
        self.fields['toevoegsel'].help_text = 'Not required'
        self.fields['phone'].help_text = 'Phone should contain only digits and evt "-"'


    class Meta:
        model = BillingProfile
        fields = ['last_name','first_name',
                'email','country','state',
                'city','district','street',
                'house_number','postcode','toevoegsel','phone'
                ]
        widgets = {'postcode':forms.TextInput(attrs={'placeholder':"for example:1234AB"}),
                'phone':forms.TextInput(attrs={'placeholder':"for example:06-1234567"})
            }
    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        digit_phone = "".join(phone.split('-'))
        if not digit_phone.isdigit():
            raise forms.ValidationError('Tel number should contain only digits (and evt-)')
        if len(digit_phone) > 20:
            raise forms.ValidationError('Tel number is too long')
        return phone
