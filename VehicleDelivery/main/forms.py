from django import forms
from .models import *
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Div, Submit
import datetime

class NameForm(forms.Form):
    your_name = forms.CharField(label='Your name', max_length=100)
    email = forms.EmailField(label='Your email')
    profile_image = forms.ImageField(label='Profile image')
    CATEGORY_CHOICES = [
        ('ST', 'Student'),
        ('TE', 'Teacher'),
        ('OT', 'Other'),
    ]
    category = forms.ChoiceField(choices=CATEGORY_CHOICES, label='Choose category')

    def __str__(self):
        return self.name

#We are going to use this one
class ClaimForm(forms.ModelForm):
    class Meta:
        model = ClaimModel
        fields = "__all__"

    def __str__(self):
        return self.firm_name
    def __repr__(self):
        return self.firm_name


class TransportForm(forms.ModelForm):
    class Meta:
        model = TransportModel
        fields = "__all__"
    def __str__(self):
        return self.firm_name
    def __repr__(self):
        return self.firm_name

class PreparationForm(forms.ModelForm):
    class Meta:
        model = PreparationModel
        fields = "__all__"
    def __str__(self):
        return self.firm_name
    def __repr__(self):
        return self.firm_name

class CommunicationForm(forms.ModelForm):
    class Meta:
        model = CommunicationModel
        fields = "__all__"
    def __str__(self):
        return self.firm_name
    def __repr__(self):
        return self.firm_name

class OtherForm(forms.ModelForm):
    class Meta:
        model = OtherModel
        fields = "__all__"
    def __str__(self):
        return self.firm_name

    def __repr__(self):
        return self.firm_name