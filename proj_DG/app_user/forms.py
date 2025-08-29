from django import forms
from .models import Profile

class ProfileForm(forms.ModelForm):
    email = forms.EmailField(disabled=True, required=False)
    phone = forms.CharField(disabled=True, required=False)

    class Meta:
        model = Profile
        fields = ['name', 'billing_address', 'delivery_address', 'same_as_delivery', 'email', 'phone']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['email'].initial = user.email
            self.fields['phone'].initial