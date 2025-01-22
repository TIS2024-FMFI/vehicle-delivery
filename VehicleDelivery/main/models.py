from django.db import models
from django.utils import timezone
from datetime import date
import datetime
from django.contrib.auth.models import User

# Create your models here.


class Department(models.Model):
    # code = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(default=None, null=True) 

    def __str__(self):
        return self.name

class Person(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None)
    TYPE_OF_USER = [
        ('ADMIN', 'Admin'),
        ('AGENT', 'Agent'),
    ]
    # category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    userType = models.CharField(max_length=5, choices=TYPE_OF_USER, default='AGENT')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)

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

