from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("name/", views.get_name, name="get_name"),
    path("thanks/", views.thanks, name="thanks"),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path("list/", views.view_submissions, name="list"),
    path("form_claim/", views.form_claim_2, name="form_claim"),
    path("forms/", views.form_all, name="form_all"),
    path("departments/", views.departments, name="departments"),
    path("form_department/<int:id>/", views.form_department, name="form_department"),
]