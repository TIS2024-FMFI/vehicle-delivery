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
from functools import wraps
from django.contrib.auth.forms import PasswordChangeForm
from .decorators import admin_required, login_required
from django.core.mail import send_mail
from django.conf import settings
from .models import ClaimModel, Person


#Create your views here.

def no_access(request):
    activate(request.session["language"])
    return render(request, 'no_access.html', {"message": "You do not have permission to access this page."})

def hello_world(request):
    return HttpResponse("Hello, World!")

def home(request):
    if "language" not in request.session:
        request.session["language"] = 'en'
    activate(request.session["language"])
    return render(request, "home.html")

@admin_required
def form_department(request, id):
    activate(request.session["language"])
    department_instance = Department.objects.get(id=id)
    if request.method == 'POST':
        if request.POST.get('delete'):
            department_instance.delete()
            return redirect('/departments/')
        form = DepartmentForm(request.POST, instance=department_instance)
        if form.is_valid():
            form.save()
            return redirect('/departments/')
    else:
        form = DepartmentForm(instance=department_instance)

    return render(request, "departments/department_form.html", {'form': form})

@admin_required
def form_create_person(request):
    activate(request.session["language"])
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/users/')
    else:
        form = PersonForm()
    return render(request, "registration/create_user.html", {'form': form})

@admin_required
def form_change_person_passwd(request, id):
    activate(request.session["language"])
    user = User.objects.get(id=id)
    message = None
    if request.method == 'POST':
        form = ChanngePersonPasswdForm(request.POST)
        if form.is_valid() and form.cleaned_data['password1'] == form.cleaned_data['password2']:
            user.set_password(form.cleaned_data['password1'])
            user.save()
            return redirect('/users/')
        else:
            message = "Passwords do not match"
    else:
        form = ChanngePersonPasswdForm()
    return render(request, "registration/change_passwd.html", {'form': form,
                                                               "user": user,
                                                               "message": message})

@admin_required
def form_update_person(request, id):
    activate(request.session["language"])
    user = User.objects.get(id=id)
    if request.method == 'POST':
        if request.POST.get('delete'):
            user.delete()
            return redirect('/users/')
        if request.POST.get('save'):
            form = UpdatePersonForm(request.POST, instance=user.person)
            if form.is_valid():
                form.save()
                return redirect('/users/')
    else:
        form = UpdatePersonForm(instance=user.person)
    return render(request, "registration/update_person.html", {'form': form,
                                                               "user": user,})

@admin_required
def users(request):
    search_query = request.GET.get('search', '')

    activate(request.session["language"])
    if request.method == 'POST':
        if request.POST.get('passwd'):
            return redirect(f"/change_passwd/{request.POST.get('passwd')}/")
        elif request.POST.get('update'):
            return redirect(f"/update_person/{request.POST.get('update')}/")


    users = User.objects.all().exclude(id=request.user.id).order_by('username')

    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )


    return render(request, "registration/users.html", {'users': users, 'search' : search_query})

@admin_required
def departments(request):
    search_query = request.GET.get('search', '')

    activate(request.session["language"])
    if request.method == 'POST':
        if request.POST.get('add'):
            department = Department()
            department.save()
        elif request.POST.get('department'):
            department = Department.objects.get(id=request.POST.get('department'))

        return redirect(f'/form_department/{department.id}/')

    departments = Department.objects.all().order_by('name')

    if search_query:
        departments = departments.filter(name__icontains=search_query)


    return render(request, "departments/departments.html", {'departments': departments, 'search' : search_query})

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
            claim = form.save(commit=False)
            claim.status = 'new'
            claim.save()

            mail_send(claim, 'CL')  # send mail to customer

            departments = Department.objects.filter(reclamationType='CL')
            for department in departments:
                if department.email:
                    send_claim_email_to_agent(claim, department.email)


            return HttpResponseRedirect('/form_claim/')
    else:
        form = ClaimForm()

    return render(request, "form_claim.html", {'form': form})


def form_communication(request):
    activate(request.session["language"])
    if request.method == 'POST':
        form = CommunicationForm(request.POST, request.FILES)
        if form.is_valid():
            communication = form.save(commit=False)
            communication.status = 'new'
            communication.save()

            mail_send(communication, 'CM')  # send mail to customer

            departments = Department.objects.filter(reclamationType='CM')
            for department in departments:
                if department.email:
                    send_claim_email_to_agent(communication, department.email)

            return HttpResponseRedirect('/thanks/')
    else:
        form = CommunicationForm()

    return render(request, "form_communication.html", {'form': form})


def form_other(request):
    activate(request.session["language"])
    if request.method == 'POST':
        form = OtherForm(request.POST, request.FILES)
        if form.is_valid():
            other = form.save(commit=False)
            other.status = 'new'
            other.save()

            mail_send(other, 'OT')  # send mail to customer

            departments = Department.objects.filter(reclamationType='OT')
            for department in departments:
                if department.email:
                    send_claim_email_to_agent(other, department.email)

            return HttpResponseRedirect('/thanks/')
    else:
        form = OtherForm()

    return render(request, "form_other.html", {'form': form})


def form_transport(request):
    activate(request.session["language"])
    if request.method == 'POST':
        form = TransportForm(request.POST, request.FILES)
        if form.is_valid():
            transport = form.save(commit=False)
            transport.status = 'new'
            transport.save()

            mail_send(transport, 'TR')  # send mail to customer

            departments = Department.objects.filter(reclamationType='TR')
            for department in departments:
                if department.email:
                    send_claim_email_to_agent(transport, department.email)

            return HttpResponseRedirect('/thanks/')
    else:
        form = TransportForm()

    return render(request, "form_transport.html", {'form': form})


def form_preparation(request):
    activate(request.session["language"])
    if request.method == 'POST':
        form = PreparationForm(request.POST, request.FILES)
        if form.is_valid():
            prepair = form.save(commit=False)
            prepair.status = 'new'
            prepair.save()

            mail_send(prepair, 'VP')  # send mail to customer

            departments = Department.objects.filter(reclamationType='VP')
            for department in departments:
                if department.email:
                    send_claim_email_to_agent(prepair, department.email)

            return HttpResponseRedirect('/thanks/')
    else:
        form = PreparationForm()

    return render(request, "form_preparation.html", {'form': form})


def thanks(request):
    activate(request.session["language"])
    return render(request, "thank.html")

#(shows ClaimModel entries)----------------------------------------------------------------------

@login_required
def agent_dashboard(request):
    activate(request.session["language"])
    input_status = request.GET.get('status', 'new')
    input_date_from = request.GET.get('date_from', '')
    input_date_to = request.GET.get('date_to', '')
    input_id = request.GET.get('id', '')
    input_vin = request.GET.get('vin', '')
    input_name = request.GET.get('first_name', '')
    input_email = request.GET.get('email', '')


    print(input_status)
    print(input_name)
    print(input_id)

    input_type = "CL"
    if request.user.person.department != None:
        if request.user.person.department.reclamationType:
            input_type = request.user.person.department.reclamationType

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

    print()

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

@login_required
def update_status(request):
    print("Som tu----------------------------------------------------")
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
            match request.user.person.department.reclamationType:
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
@login_required
def entry_detail(request, id):
    activate(request.session["language"])

    entry = None

    match request.user.person.department.reclamationType:
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

@login_required
def statistics(request):
    activate(request.session["language"])
    return render(request, "statistics.html")

def form_claim_next(request):
    if request.methid == 'POST':
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save()
            mail_send(complaint)

            return HttpResponse("Claim submitted successfully, notification sent")
        else:
            form = ClaimForm()
        return render(request, "thank.html", {'form': form})

def mail_send(claim, complaint_type):
    complaint = None
    match complaint_type:
        case 'CL':
            try:
                complaint = ClaimModel.objects.get(pk=claim.id)
            except ClaimModel.DoesNotExist:
                return HttpResponse("Complaint not found.", status=404)
        case 'CM':
            try:
                complaint = CommunicationModel.objects.get(pk=claim.id)
            except CommunicationModel.DoesNotExist:
                return HttpResponse("Complaint not found.", status=404)
        case 'TR':
            try:
                complaint = TransportModel.objects.get(pk=claim.id)
            except TransportModel.DoesNotExist:
                return HttpResponse("Complaint not found.", status=404)
        case 'VP':
            try:
                complaint = PreparationModel.objects.get(pk=claim.id)
            except PreparationModel.DoesNotExist:
                return HttpResponse("Complaint not found.", status=404)
        case 'OT':
            try:
                complaint = OtherModel.objects.get(pk=claim.id)
            except OtherModel.DoesNotExist:
                return HttpResponse("Complaint not found.", status=404)

    subject = "Complaint Submitted Successfully"
    message = f"""
    Dear {complaint.first_name} {complaint.second_name},

    Thank you for submitting your complaint with us. Here are the details of your submission:

    - Submission Date: {complaint.date}
    - Message: {complaint.message}

    Our team will review your complaint and contact you soon.

    Best regards,
    CEVA Logistic
    """
    recipient = complaint.email

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # sender
        [recipient],
        fail_silently=False,
    )

    return HttpResponse("Email notification sent successfully.")


def send_claim_email_to_agent(complaint, agent_email):
    subject = "New Claim Submission"
    message = f"""
    A new complaint has been submitted with the following details:
    
    - Complaint id: {complaint.id}
    - Submission Date: {complaint.date}
    - Message: {complaint.message}
    
    Please review the claim and take appropriate action.
    """

    send_mail(
        subject,
        message,
        settings.EMAIL_HOST_USER,  # Sender's email
        [agent_email],  # Agent's email
        fail_silently=False,
    )


def no_access(request):
    return render(request, 'no_access.html', {"message": "You do not have permission to access this page."})

def thanks(request):
    return render(request, "thank.html")

