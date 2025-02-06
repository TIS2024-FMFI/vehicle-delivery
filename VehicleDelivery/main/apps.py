from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='main/admin.env')

username = os.getenv('Admin_username')
mail = os.getenv('Admin_mail')
passwd = os.getenv('Admin_password')

class MainConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'main'

    def ready(self):
        post_migrate.connect(create_admin_user, sender=self)

def create_admin_user(sender, **kwargs):
    print("Something Terrible happend")
    from django.contrib.auth import get_user_model
    from .models import Person
    """Ensure an admin user always exists after migrations are done"""
    from django.db import IntegrityError

    try:
        User = get_user_model()

        if not Person.objects.filter(user_type='ADMIN').exists():
            user = User.objects.create_user(username=username, email=mail, password=passwd)

            person, created = Person.objects.get_or_create(user=user)

            person.user_type = 'ADMIN'
            person.save()

    except IntegrityError as e:
        print(f"IntegrityError: {e}")
    except Exception as e:
        print(f"Error in creating admin user: {e}")
