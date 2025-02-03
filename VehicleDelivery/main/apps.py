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
        # Connect the signal to the post_migrate handler
        post_migrate.connect(create_admin_user, sender=self)

# The function that will create the admin user
def create_admin_user(sender, **kwargs):
    from django.contrib.auth import get_user_model
    from .models import Person
    """Ensure an admin user always exists after migrations are done"""
    from django.db import IntegrityError
    
    try:
        # Get the User model (works for both default and custom user models)
        User = get_user_model()

        # Check if there is already a Person with user_type='ADMIN'
        if not Person.objects.filter(user_type='ADMIN').exists():
            # Create a new user if no Person with ADMIN user_type exists
            user = User.objects.create_user(username=username, email=mail, password=passwd)
            
            # Ensure a related Person object is created for this user
            person, created = Person.objects.get_or_create(user=user)
            
            # Set the user type for the related Person object
            person.user_type = 'ADMIN'
            person.save()

    except IntegrityError as e:
        # Handle database-related errors (e.g., duplicate entry issues)
        print(f"IntegrityError: {e}")
    except Exception as e:
        # Handle any other errors
        print(f"Error in creating admin user: {e}")
