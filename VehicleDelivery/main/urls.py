from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path("thanks/", views.thanks, name="thanks"),
    path("form_claim/", views.form_claim, name="form_claim"),
    path("forms/", views.form_all, name="form_all"),
    path("departments/", views.departments, name="departments"),
    path("form_department/<int:id>/", views.form_update_department, name="form_department"),
    path("create_department/", views.form_create_department, name="create_department"),
    path("create_person/", views.form_create_person, name="create_person"),
    path("users/", views.users, name="users"),
    path("change_passwd/<int:id>/", views.form_change_person_passwd, name="change_passwd"),
    path("update_person/<int:id>/", views.form_update_person, name="update_person"),
    path("form_transportation/", views.form_transport, name="form_transportation"),
    path("form_preparation/", views.form_preparation, name="form_preparation"),
    path("form_communication/", views.form_communication, name="form_communication"),
    path("form_other/", views.form_other, name="form_other"),
    path("no_access/", views.no_access, name="no_access"),
    path("agent_dashboard/", views.agent_dashboard, name="agent_dashboard"),
    path("entry_detail/<int:id>/", views.entry_detail, name="entry_detail"),
    path('update_status/', views.update_status, name='update_status'),
    path('switch-language/<str:language_code>/', views.switch_language, name='switch_language'),
    path("statistics", views.statistics, name="statistics")


]