from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import *
from .models import *

def home(request):
    return render(request, "home.html")








def form_all(request):
    return render(request, "forms.html")

def form_claim(request):
    if request.method == 'POST':
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = ClaimForm()

    return render(request, "form_claim.html", {'form': form})

def form_communication(request):
    if request.method == 'POST':
        form = CommunicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = CommunicationForm()

    return render(request, "form_communication.html", {'form': form})

def form_other(request):
    if request.method == 'POST':
        form = OtherForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = OtherForm()

    print(form.errors)
    return render(request, "form_other.html", {'form': form})

def form_transport(request):
    if request.method == 'POST':
        form = TransportForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = TransportForm()

    return render(request, "form_transport.html", {'form': form})

def form_preparation(request):
    if request.method == 'POST':
        form = PreparationForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = PreparationForm()

    return render(request, "form_preparation.html", {'form': form})

def thanks(request):
    return render(request, "thank.html")

#(shows ClaimModel entries)----------------------------------------------------------------------
def agent_dashboard(request):
    input_status = request.GET.get('status', 'new')
    input_date_from = request.GET.get('date_from', '')
    input_date_to = request.GET.get('date_to', '')
    input_id = request.GET.get('id', '')
    input_vin = request.GET.get('vin', '')
    input_name = request.GET.get('first_name', '')
    input_email = request.GET.get('email', '')

    entries = ClaimModel.objects.all()

    if input_id:
        entries = entries.filter(id__icontains=input_id)
    if input_vin:
        entries = entries.filter(VIN_number__icontains=input_vin)
    if input_date_from:
        entries = entries.filter(date__gte=input_date_from)
    if input_date_to:
        entries = entries.filter(date__lte=input_date_to)
    if input_email:
        entries = entries.filter(email__icontains=input_email)
    if input_name:
        entries = entries.filter(Q(firm_name__icontains=input_name) | Q(first_name__icontains=input_name) | Q(second_name__icontains=input_name))
    if input_status:
        entries = entries.filter(status=input_status)






    return render(request, "agent_dashboard.html", {'entries': entries})

def update_status(request):
    if request.method == "POST":
        # Parse the received data
        new_status = request.POST.get('new_status')
        selected_entries_json = request.POST.get('selected_entries')

        try:
            # Decode the JSON string back into a Python list
            selected_entries = json.loads(selected_entries_json)
        except json.JSONDecodeError:
            return JsonResponse({'status': 'error', 'message': 'Invalid data'}, status=400)

        # Perform the status update
        if selected_entries and new_status:
            ClaimModel.objects.filter(id__in=selected_entries).update(status=new_status)
            return JsonResponse({'status': 'success', 'message': 'Status updated successfully'})

        return JsonResponse({'status': 'error', 'message': 'No entries or status provided'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

#(shows ClaimModel details)-----------------------------------------------------------------------
def entry_detail(request, id):
    entry = ClaimModel.objects.get(id=id)
    return render(request, "entry_detail.html", {"entry" : entry})



