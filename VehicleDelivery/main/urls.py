from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("thanks/", views.thanks, name="thanks"),
    path("form_claim/", views.form_claim, name="form_claim"),
    path("form_transportation/", views.form_transport, name="form_transportation"),
    path("form_preparation/", views.form_preparation, name="form_preparation"),
    path("form_communication/", views.form_communication, name="form_communication"),
    path("form_other/", views.form_other, name="form_other"),
    path("forms/", views.form_all, name="form_all"),
    path("agent_dashboard/", views.agent_dashboard, name="agent_dashboard"),
    path("entry_detail/<int:id>/", views.entry_detail, name="entry_detail"),
    path('update_status/', views.update_status, name='update_status'),
]