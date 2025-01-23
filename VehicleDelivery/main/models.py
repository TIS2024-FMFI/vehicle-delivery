from django.db import models
from django.utils import timezone
from datetime import date
import datetime
from .dropdown_options import NATURE_OF_DAMAGE, PLACE_OF_DAMAGE, STATUS_CHOICES
import os
from django.conf import settings

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
    waybill = models.FileField(upload_to='temp/')
    damage_report = models.FileField(upload_to='temp/')
    photo_car = models.FileField(upload_to='temp/')
    photo_VIN = models.FileField(upload_to='temp/')
    photo_area = models.FileField(upload_to='temp/')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        folder_name = str(self.id)
        new_folder_path = os.path.join(settings.MEDIA_ROOT, 'uploads/CL', folder_name)

        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)

        file_fields = [
            (self.waybill, "waybill"),
            (self.damage_report, "damage_report"),
            (self.photo_car, "photo_car"),
            (self.photo_VIN, "vin_number"),
            (self.photo_area, "photo_area"),
        ]

        for file, new_name in file_fields:
            if file and os.path.exists(file.path):
                old_path = file.path
                file_extension = os.path.splitext(old_path)[1]
                new_file_name = f"{new_name}{file_extension}"
                new_file_path = os.path.join(new_folder_path, new_file_name)

                os.rename(old_path, new_file_path)

                file.name = os.path.join('uploads/CL', folder_name, new_file_name)
        super().save(*args, **kwargs)

class OtherModel(models.Model):
    firm_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    email = models.EmailField()
    date = models.DateField(null=True, blank=True, default=datetime.date.today)

    #Poznamka
    message = models.TextField()

    #Subory
    photo = models.FileField(upload_to='temp/')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        folder_name = str(self.id)
        new_folder_path = os.path.join(settings.MEDIA_ROOT, 'uploads/OT', folder_name)

        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)

        file_fields = [
            (self.photo, "file"),
        ]

        for file, new_name in file_fields:
            if file and os.path.exists(file.path):
                old_path = file.path
                file_extension = os.path.splitext(old_path)[1]
                new_file_name = f"{new_name}{file_extension}"
                new_file_path = os.path.join(new_folder_path, new_file_name)

                os.rename(old_path, new_file_path)

                file.name = os.path.join('uploads/OT', folder_name, new_file_name)
        super().save(*args, **kwargs)

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
    photo = models.FileField(upload_to='temp/')


    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        folder_name = str(self.id)
        new_folder_path = os.path.join(settings.MEDIA_ROOT, 'uploads/TR', folder_name)

        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)

        file_fields = [
            (self.photo, "file"),
        ]

        for file, new_name in file_fields:
            if file and os.path.exists(file.path):
                old_path = file.path
                file_extension = os.path.splitext(old_path)[1]
                new_file_name = f"{new_name}{file_extension}"
                new_file_path = os.path.join(new_folder_path, new_file_name)

                os.rename(old_path, new_file_path)

                file.name = os.path.join('uploads/TR', folder_name, new_file_name)
        super().save(*args, **kwargs)

class CommunicationModel(models.Model):
    firm_name = models.CharField(max_length=30)
    second_name = models.CharField(max_length=30)
    first_name = models.CharField(max_length=30)
    email = models.EmailField()
    date = models.DateField(null=True, blank=True, default=datetime.date.today)

    #Poznamka
    message = models.TextField()

    #Subory
    photo = models.FileField(upload_to='temp/')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        folder_name = str(self.id)
        new_folder_path = os.path.join(settings.MEDIA_ROOT, 'uploads/CM', folder_name)

        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)

        file_fields = [
            (self.photo, "file"),
        ]

        for file, new_name in file_fields:
            if file and os.path.exists(file.path):
                old_path = file.path
                file_extension = os.path.splitext(old_path)[1]
                new_file_name = f"{new_name}{file_extension}"
                new_file_path = os.path.join(new_folder_path, new_file_name)

                os.rename(old_path, new_file_path)

                file.name = os.path.join('uploads/CM', folder_name, new_file_name)
        super().save(*args, **kwargs)

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
    photo = models.FileField(upload_to='temp/')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        folder_name = str(self.id)
        new_folder_path = os.path.join(settings.MEDIA_ROOT, 'uploads/VP', folder_name)

        if not os.path.exists(new_folder_path):
            os.makedirs(new_folder_path)

        file_fields = [
            (self.photo, "file"),
        ]

        for file, new_name in file_fields:
            if file and os.path.exists(file.path):
                old_path = file.path
                file_extension = os.path.splitext(old_path)[1]
                new_file_name = f"{new_name}{file_extension}"
                new_file_path = os.path.join(new_folder_path, new_file_name)

                os.rename(old_path, new_file_path)

                file.name = os.path.join('uploads/VP', folder_name, new_file_name)
        super().save(*args, **kwargs)




