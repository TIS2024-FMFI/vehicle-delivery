from django.db import models
from django.utils import timezone
from datetime import date
import datetime

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


    #Poznamka
    message = models.CharField(max_length=100)

    #Subory
    waybill = models.FileField()
    damage_report = models.FileField()
    photo_car = models.FileField()
    photo_VIN = models.FileField()
    photo_area = models.FileField()

