from django.db import models
from django.utils import timezone
from datetime import date
import datetime
from .dropdown_options import NATURE_OF_DAMAGE, PLACE_OF_DAMAGE, STATUS_CHOICES

# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    profile_image = models.ImageField(upload_to='profile_images/')
    CATEGORY_CHOICES = [
        ('ST', 'Student'),
        ('TE', 'Teacher'),
        ('OT', 'Other'),
    ]
    category = models.CharField(max_length=2, choices=CATEGORY_CHOICES, default='ST')

    def __str__(self):
        return self.name



class ClaimModel(models.Model):
    #Udaje o strane nahlasujuceho
    firm_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    email = models.EmailField()

    #Udaje o preprave
    record_number = models.CharField(max_length=30)
    registration_number = models.CharField(max_length=30)
    date = models.DateField(null=True, blank=True, default=datetime.date.today)
    country_of_arrival = models.CharField(max_length=30)
    place_of_arrival = models.CharField(max_length=30)
    city_of_arrival = models.CharField(max_length=30)


    #Podrobnosti o poskodenom vozidle
    VIN_number = models.CharField(max_length=30)
    nature_of_damage_1 = models.CharField(max_length=30, choices=NATURE_OF_DAMAGE, default='XX')
    place_of_damage_1 = models.CharField(max_length=30, choices=PLACE_OF_DAMAGE, default='00')
    nature_of_damage_2 = models.CharField(max_length=30, choices=NATURE_OF_DAMAGE, default='XX')
    place_of_damage_2 = models.CharField(max_length=30, choices=PLACE_OF_DAMAGE, default='00')
    nature_of_damage_3 = models.CharField(max_length=30, choices=NATURE_OF_DAMAGE, default='XX')
    place_of_damage_3 = models.CharField(max_length=30, choices=PLACE_OF_DAMAGE, default='00')


    #Poznamka
    message = models.TextField()

    #Subory
    waybill = models.FileField()
    damage_report = models.FileField()
    photo_car = models.FileField()
    photo_VIN = models.FileField()
    photo_area = models.FileField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

class OtherModel(models.Model):
    firm_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    email = models.EmailField()
    date = models.DateField(null=True, blank=True, default=datetime.date.today)

    #Poznamka
    message = models.TextField()

    #Subory
    photo = models.FileField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

class TransportModel(models.Model):
    firm_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    email = models.EmailField()
    date = models.DateField(null=True, blank=True, default=datetime.date.today)

    #Podrobnosti o vozidle
    VIN_number = models.CharField(max_length=30)
    vehicle_model = models.CharField(max_length=30)
    registration_number = models.CharField(max_length=30)


    #Poznamka
    message = models.TextField()

    #Subory
    photo = models.FileField()


    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

class CommunicationModel(models.Model):
    firm_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    email = models.EmailField()
    date = models.DateField(null=True, blank=True, default=datetime.date.today)

    #Poznamka
    message = models.TextField()

    #Subory
    photo = models.FileField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

class PreparationModel(models.Model):
    firm_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    email = models.EmailField()
    date = models.DateField(null=True, blank=True, default=datetime.date.today)

    #Podrobnosti o vozidle
    VIN_number = models.CharField(max_length=30)
    vehicle_model = models.CharField(max_length=30)

    #Poznamka
    message = models.TextField()

    #Subory
    photo = models.FileField()

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')




