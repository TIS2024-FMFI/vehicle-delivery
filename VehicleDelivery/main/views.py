from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .forms import *
from .models import *
from .dropdown_options import NATURE_OF_DAMAGE, PLACE_OF_DAMAGE, STATUS_CHOICES, REPORT_TYPES
from django.utils.translation import activate

def home(request):
    activate(request.session["language"])
    return render(request, "home.html")


def switch_language(request, language_code):
    activate(language_code)
    request.session["language"] = language_code
    return redirect(request.META.get('HTTP_REFERER', '/'))





def form_all(request):
    activate(request.session["language"])
    return render(request, "forms.html")

def form_claim(request):
    activate(request.session["language"])
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
    activate(request.session["language"])
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
    activate(request.session["language"])
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
    activate(request.session["language"])
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
    activate(request.session["language"])
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
    activate(request.session["language"])
    return render(request, "thank.html")

#(shows ClaimModel entries)----------------------------------------------------------------------
def agent_dashboard(request):
    activate(request.session["language"])
    input_status = request.GET.get('status', 'new')
    input_date_from = request.GET.get('date_from', '')
    input_date_to = request.GET.get('date_to', '')
    input_id = request.GET.get('id', '')
    input_vin = request.GET.get('vin', '')
    input_name = request.GET.get('first_name', '')
    input_email = request.GET.get('email', '')
    input_type = request.GET.get('type', 'CL')

    filters = {
        'status': request.GET.get('status', 'new'),
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'id': request.GET.get('id', ''),
        'vin': request.GET.get('vin', ''),
        'first_name': request.GET.get('first_name', ''),
        'email': request.GET.get('email', ''),
        'type': request.GET.get('type', 'CL'),
    }

    print(input_type)

    context = {
        'report_types': REPORT_TYPES,
        'filters' : filters
    }
    entries = None
    match input_type:
        case 'CL':
            entries = ClaimModel.objects.all()
        case 'CM':
            entries = CommunicationModel.objects.all()
        case 'TR':
            entries = TransportModel.objects.all()
        case 'VP':
            entries = PreparationModel.objects.all()
        case 'OT':
            entries = OtherModel.objects.all()

    if input_id:
        entries = entries.filter(id__icontains=input_id)

    try:
        if input_vin:
            entries = entries.filter(VIN_number__icontains=input_vin)
    except:
        pass


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


    context['entries'] = entries

    return render(request, "agent_dashboard.html", context)

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
            match request.POST.get('type'):
                case 'CL':
                    ClaimModel.objects.filter(id__in=selected_entries).update(status=new_status)
                case 'CM':
                    CommunicationModel.objects.filter(id__in=selected_entries).update(status=new_status)
                case 'TR':
                    TransportModel.objects.filter(id__in=selected_entries).update(status=new_status)
                case 'VP':
                    PreparationModel.objects.filter(id__in=selected_entries).update(status=new_status)
                case 'OT':
                    OtherModel.objects.filter(id__in=selected_entries).update(status=new_status)

            return JsonResponse({'status': 'success', 'message': 'Status updated successfully'})

        return JsonResponse({'status': 'error', 'message': 'No entries or status provided'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

#(shows ClaimModel details)-----------------------------------------------------------------------
def entry_detail(request, id, _type):
    activate(request.session["language"])

    entry = None

    match _type:
        case 'CL':
            entry = ClaimModel.objects.get(id=id)
        case 'CM':
            entry = CommunicationModel.objects.get(id=id)
        case 'TR':
            entry = TransportModel.objects.get(id=id)
        case 'VP':
            entry = PreparationModel.objects.get(id=id)
        case 'OT':
            entry = OtherModel.objects.get(id=id)


    return render(request, "entry_detail.html", {"entry" : entry})



