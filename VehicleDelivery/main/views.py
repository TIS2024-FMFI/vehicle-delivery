from django.shortcuts import render
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .forms import *
from .models import *

# Create your views here.
def hello_world(request):
    return HttpResponse("Hello, World!")

def home(request):
    return render(request, "home.html")

def get_name(request):
    if request.method == 'POST':
        form = NameForm(request.POST, request.FILES)
        if form.is_valid():
            new_person = Person(
                name=form.cleaned_data['your_name'],
                email=form.cleaned_data['email'],
                profile_image=form.cleaned_data['profile_image'],
                category=form.cleaned_data['category']
            )
            new_person.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = NameForm()

    return render(request, 'name.html', {'form': form})

def form_all(request):
    return render(request, "forms.html")

def form_claim_2(request):
    if request.method == 'POST':
        form = ClaimForm2(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponse("Claim submitted successfully.")
    else:
        form = ClaimForm2()

    return render(request, "test_form_claim.html", {'form': form})

"""
def form_claim(request):
    if request.method == 'POST':
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            new_claim = ClaimModel(
                #Udaje o strane nahlasujuceho----------------------------------------
                firm_name=form.cleaned_data['firm_name'],
                second_name=form.cleaned_data['second_name'],
                first_name=form.cleaned_data['first_name'],
                email=form.cleaned_data['email'],
                #udaje o preprave----------------------------------------------------
                record_number=form.cleaned_data['record_number'],
                registration_number=form.cleaned_data['registration_number'],
                date=form.cleaned_data['date'],
                country_of_arrival=form.cleaned_data['country_of_arrival'],
                place_of_arrival=form.cleaned_data['place_of_arrival'],
                city_of_arrival=form.cleaned_data['city_of_arrival'],
                #Podrobnosti o poskodeni---------------------------------------------
                VIN_number=form.cleaned_data['VIN_number'],
                #Poznamka------------------------------------------------------------
                message=form.cleaned_data['message'],
                #Subory--------------------------------------------------------------
                waybill=request.FILES['waybill'],
                damage_report=request.FILES['damage_report'],
                photo_car=request.FILES['photo_car'],
                photo_VIN=request.FILES['photo_VIN'],
                photo_area=request.FILES['photo_area']
            )
            new_claim.save()
            return HttpResponse("Claim submitted successfully.")
    else:
        form = ClaimForm()

    return render(request, 'test_form_claim.html', {'form': form})
"""
def form_communication(request):
    pass

def form_other(request):
    pass

def form_transport(request):
    pass

def form_preparation(request):
    pass

def thanks(request):
    return render(request, "thank.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def view_submissions(request):
    people = Person.objects.all()
    return render(request, 'list.html', {'people': people})
