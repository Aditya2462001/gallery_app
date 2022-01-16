from django import forms
from .models import *

class ContactForm(forms.ModelForm):
     class Meta:
        model = ContactMe
        fields = "__all__"