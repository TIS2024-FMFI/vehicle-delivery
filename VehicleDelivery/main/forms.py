from django import forms
from .models import *
from django.contrib.auth.models import User
import datetime
from django.contrib.auth.forms import UserCreationForm



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

class UpdatePersonForm(forms.ModelForm):
    username = forms.CharField(label='Username', widget=forms.TextInput)
    class Meta:
        model = Person
        fields = ['user_type', 'department']
        # labels = {
        #     "user_type" : "User type",
        #     "department" : "Department"
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if kwargs.get('instance'):
            self.fields['username'].initial = self.instance.user.username

        

    def save(self, commit=True):
        # Save the User model first
        person = super().save(commit=commit)

        if commit:
            person.user.username = self.cleaned_data['username']
            person.user.save()
            
        return person

class ChanngePersonPasswdForm(forms.Form):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)



class PersonForm(UserCreationForm):
    # Add fields from the Person model
    user_type = forms.ChoiceField(choices=Person.TYPE_OF_USER, label='User type')
    department = forms.ModelChoiceField(queryset=Department.objects.all(), label='Department')

    class Meta:
        model = User
        fields = ['username', 'password1', 'password2'] #, 'email', 'first_name', 'last_name']

    def __init__(self, *args, **kwargs):
        user_instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)

        if user_instance:
            try:
                person_instance = user_instance.person
                self.fields['user_type'].initial = person_instance.user_type
                self.fields['department'].initial = person_instance.department
            except Person.DoesNotExist:
                # Handle the case where no Person object exists for the User
                pass


    def save(self, commit=True):
        # Save the User model first
        user = super().save(commit=commit)

        # Update the email field of the User model
        # self.instance.email = user.username
        # self.instance.save()

        # Then save the Person model
        if commit:
            Person.objects.create(
                user=user,
                user_type=self.cleaned_data['user_type'],
                department=self.cleaned_data['department']
            )
        return user

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
