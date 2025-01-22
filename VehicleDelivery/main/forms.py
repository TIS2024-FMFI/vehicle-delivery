from django import forms
from .models import *
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
class ClaimForm2(forms.ModelForm):
    class Meta:
        model = ClaimModel
        fields = "__all__"
        labels = {
            "date" : "Datum vykladky"
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = "__all__"
        labels = {
            "name" : "Name of department"
        }


class ClaimForm(forms.Form):
    #Udaje o strane nahlasujuceho
    firm_name = forms.CharField(label="Firm name", max_length=30)
    second_name = forms.CharField(label="Second name", max_length=30)
    first_name = forms.CharField(label="First name", max_length=30)
    email = forms.EmailField(label='Your email')

    #Udaje o preprave
    record_number = forms.CharField(label="Record number", max_length=30)
    registration_number = forms.CharField(label="Registration number", max_length=30)
    date = forms.DateField(initial=datetime.date.today)
    country_of_arrival = forms.CharField(label="Country of Arrival", max_length=30)
    place_of_arrival = forms.CharField(label="Place of Arrival", max_length=30)
    city_of_arrival = forms.CharField(label="City of Arrival", max_length=30)


    #Podrobnosti o poskodenom vozidle
    VIN_number = forms.CharField(label="VIN", max_length=30)

    #Poznamka
    message = forms.CharField(label="Note", max_length=100)

    #Subory
    waybill = forms.FileField(label="Waybill")
    damage_report = forms.FileField(label="Damage Report")
    photo_car = forms.FileField(label="Photo of whole car")
    photo_VIN = forms.FileField(label="Photo of VIN")
    photo_area = forms.FileField(label="Photo of damaged area")

    def __str__(self):
        return str(self.firm_name) + ";" + str(self.first_name) + " " + str(self.second_name) + ";" + str(self.email)
