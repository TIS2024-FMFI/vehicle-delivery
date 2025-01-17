from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("name/", views.get_name, name="get_name"),
    path("thanks/", views.thanks, name="thanks"),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path("list/", views.view_submissions, name="list"),
    path("form_claim/", views.form_claim, name="form_claim"),
    path("form_transportation/", views.form_transport, name="form_transportation"),
    path("form_preparation/", views.form_preparation, name="form_preparation"),
    path("form_communication/", views.form_communication, name="form_communication"),
    path("form_other/", views.form_other, name="form_other"),
    path("forms/", views.form_all, name="form_all")
]