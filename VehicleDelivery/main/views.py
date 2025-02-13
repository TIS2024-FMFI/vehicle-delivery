from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q, Count
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.forms.models import model_to_dict
import json
from .forms import *
from .models import *
from .dropdown_options import NATURE_OF_DAMAGE, PLACE_OF_DAMAGE, STATUS_CHOICES, REPORT_TYPES
from django.utils.translation import activate
from functools import wraps
from django.contrib.auth.forms import PasswordChangeForm
from .decorators import admin_required, login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.conf import settings
from .models import ClaimModel, Person
from .export import export_single_object, download_all_files
from .logging import get_complaint_type




#Create your views here.

def set_language(request):
    if "language" not in request.session:
        request.session["language"] = 'en'
    activate(request.session["language"])

def no_access(request):
    set_language(request)
    return render(request, 'no_access.html', {"message": "You do not have permission to access this page."})

def hello_world(request):
    return HttpResponse("Hello, World!")

def home(request):
    if "language" not in request.session:
        request.session["language"] = 'en'
    set_language(request)
    return render(request, "home.html")

@admin_required
def form_update_department(request, id):
    set_language(request)

    # Fetch existing department
    department_instance = get_object_or_404(Department, id=id)

    if request.method == 'POST':
        if request.POST.get('delete'):
            ActionLog.objects.create(
                user=request.user.person,
                target_type=get_complaint_type(Department),
                target_id=id,
                action="delete",
                original_value=department_instance.name
            )
            department_instance.delete()
            return redirect('/departments/')
        
        # Track changes before saving
        old_values = model_to_dict(department_instance)
        form = DepartmentForm(request.POST, instance=department_instance)

        if form.is_valid():
            new_values = form.cleaned_data
            form.save()

            # Log only changed fields
            excluded_fields = {"id", "created_at"}
            for field in old_values:
                if field in excluded_fields:
                    continue
                
                old_value = old_values[field]
                new_value = new_values.get(field)

                if old_value != new_value:
                    ActionLog.objects.create(
                        user=request.user.person,
                        target_type=get_complaint_type(Department),
                        target_id=id,
                        action=f"update_{field}",
                        original_value=str(old_value) if old_value is not None else "",
                        new_value=str(new_value) if new_value is not None else ""
                    )

            return redirect('/departments/')
    
    else:
        form = DepartmentForm(instance=department_instance)

    return render(request, "departments/department_form.html", {'form': form,
                                                                'creating_new': False})

@admin_required
def form_create_department(request):
    set_language(request)
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        
        if form.is_valid():
            department_instance = form.save()
            ActionLog.objects.create(
                user=request.user.person,
                target_type=get_complaint_type(Department),
                target_id=department_instance.id,
                action="create",
                new_value=department_instance.name
            )
            return redirect('/departments/')
    else:
        form = DepartmentForm()
    return render(request, "departments/department_form.html", {'form': form,
                                                                'creating_new': True})

@admin_required
def form_create_person(request):
    set_language(request)
    
    if request.method == 'POST':
        form = PersonForm(request.POST)
        
        if form.is_valid():
            person_instance = form.save()  # Save and get the new instance
            
            ActionLog.objects.create(
                user=request.user.person,
                target_type=get_complaint_type(Person),
                target_id=person_instance.id,
                action="create",
                new_value=person_instance.username
            )
            return redirect('/users/')
    
    else:
        form = PersonForm()

    return render(request, "registration/create_user.html", {'form': form})

@admin_required
def form_change_person_passwd(request, id):
    set_language(request)
    user = User.objects.get(id=id)
    message = None
    if request.method == 'POST':
        form = ChanngePersonPasswdForm(request.POST)
        if form.is_valid() and form.cleaned_data['password1'] == form.cleaned_data['password2']:
            user.set_password(form.cleaned_data['password1'])
            user.save()

            ActionLog.objects.create(
                user=request.user.person,
                target_type=get_complaint_type(Person),
                target_id=id,
                action="admin_password_change"
            )

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
    if request.user.id == id:
        return redirect('/users/')

    set_language(request)
    user = get_object_or_404(User, id=id)
    
    if request.method == 'POST':
        # Handle delete
        if request.POST.get('delete'):
            ActionLog.objects.create(
                user=request.user.person,
                target_type=get_complaint_type(Person),
                target_id=user.person.id,
                action="delete",
                original_value=user.username
            )
            user.delete()
            return redirect('/users/')

        # Handle update
        if request.POST.get('save'):
            person_instance = user.person
            old_values = model_to_dict(person_instance)  # Get old values
            old_values['username'] = person_instance.user.username
            form = UpdatePersonForm(request.POST, instance=person_instance)

            if form.is_valid():
                new_values = form.cleaned_data  # Get new field values
                form.save()

                # Log only changed fields
                excluded_fields = {"id", "created_at", "user"}
                for field in old_values:
                    if field in excluded_fields:
                        continue
                    
                    old_value = old_values.get(field)
                    new_value = new_values.get(field)

                    if old_value != new_value:  # Only log changes
                        ActionLog.objects.create(
                            user=request.user.person,
                            target_type=get_complaint_type(Person),
                            target_id=person_instance.id,
                            action=f"update_{field}",
                            original_value=str(old_value) if old_value is not None else "",
                            new_value=str(new_value) if new_value is not None else ""
                        )

                return redirect('/users/')
    
    else:
        form = UpdatePersonForm(instance=user.person)

    return render(request, "registration/update_person.html", {'form': form, "user": user})

@admin_required
def users(request):
    search_query = request.GET.get('search', '')

    set_language(request)
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

    set_language(request)
    if request.method == 'POST':
        if request.POST.get('add'):
            return redirect('/form_department/0/')
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
    set_language(request)
    return render(request, "forms.html")


def form_claim(request):
    set_language(request)
    if request.method == 'POST':
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            complaint = form.save()

            mail_send(complaint, 'CL')  # send mail to customer

            departments = Department.objects.filter(reclamationType='CL')
            for department in departments:
                if department.email:
                    send_claim_email_to_agent(complaint, department.email)

            ActionLog.objects.create(
                target_type=get_complaint_type(complaint.__class__),
                target_id=complaint.id,
                action=f"complaint_import",
                new_value=complaint.firm_name
            )
            return HttpResponseRedirect('/thanks/')
    else:
        form = ClaimForm()

    return render(request, "form_claim.html", {'form': form})


def form_communication(request):
    set_language(request)
    if request.method == 'POST':
        form = CommunicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            complaint = form.save()

            mail_send(complaint, 'CM')  # send mail to customer

            departments = Department.objects.filter(reclamationType='CM')
            for department in departments:
                if department.email:
                    send_claim_email_to_agent(complaint, department.email)

            ActionLog.objects.create(
                target_type=get_complaint_type(complaint.__class__),
                target_id=complaint.id,
                action=f"complaint_import",
                new_value=complaint.firm_name
            )
            return HttpResponseRedirect('/thanks/')
    else:
        form = CommunicationForm()

    return render(request, "form_communication.html", {'form': form})


def form_other(request):
    set_language(request)
    if request.method == 'POST':
        form = OtherForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            complaint = form.save()

            mail_send(complaint, 'OT')  # send mail to customer

            departments = Department.objects.filter(reclamationType='OT')
            for department in departments:
                if department.email:
                    send_claim_email_to_agent(complaint, department.email)

            ActionLog.objects.create(
                target_type=get_complaint_type(complaint.__class__),
                target_id=complaint.id,
                action=f"complaint_import",
                new_value=complaint.firm_name
            )
            return HttpResponseRedirect('/thanks/')
    else:
        form = OtherForm()

    return render(request, "form_other.html", {'form': form})


def form_transport(request):
    set_language(request)
    if request.method == 'POST':
        form = TransportForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            complaint = form.save()

            mail_send(complaint, 'TR')  # send mail to customer

            departments = Department.objects.filter(reclamationType='TR')
            for department in departments:
                if department.email:
                    send_claim_email_to_agent(complaint, department.email)

            ActionLog.objects.create(
                target_type=get_complaint_type(complaint.__class__),
                target_id=complaint.id,
                action=f"complaint_import",
                new_value=complaint.firm_name
            )
            return HttpResponseRedirect('/thanks/')
    else:
        form = TransportForm()

    return render(request, "form_transport.html", {'form': form})


def form_preparation(request):
    set_language(request)
    if request.method == 'POST':
        form = PreparationForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            complaint = form.save()

            mail_send(complaint, 'VP')  # send mail to customer

            departments = Department.objects.filter(reclamationType='VP')
            for department in departments:
                if department.email:
                    send_claim_email_to_agent(complaint, department.email)

            ActionLog.objects.create(
                target_type=get_complaint_type(complaint.__class__),
                target_id=complaint.id,
                action=f"complaint_import",
                new_value=complaint.firm_name
            )
            return HttpResponseRedirect('/thanks/')
    else:
        form = PreparationForm()

    return render(request, "form_preparation.html", {'form': form})


def thanks(request):
    set_language(request)
    return render(request, "thank.html")

#(shows ClaimModel entries)----------------------------------------------------------------------

@login_required
def agent_dashboard(request):
    set_language(request)
    input_status = request.GET.get('status', 'new')
    input_date_from = request.GET.get('date_from', '')
    input_date_to = request.GET.get('date_to', '')
    input_id = request.GET.get('id', '')
    input_vin = request.GET.get('vin', '')
    input_name = request.GET.get('first_name', '')
    input_email = request.GET.get('email', '')
    input_type = request.GET.get('type', '')


    if (input_type == ''):
        if request.user.person.department != None:
            if request.user.person.department.reclamationType:
                input_type = request.user.person.department.reclamationType # normal agent
            else:
                input_type = "CL" #something went wrong
        else:
            input_type = "CL" #admin



    filters = {
        'status': request.GET.get('status', 'new'),
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'id': request.GET.get('id', ''),
        'vin': request.GET.get('vin', ''),
        'first_name': request.GET.get('first_name', ''),
        'email': request.GET.get('email', ''),
        'type': request.GET.get('type', 'CL'),
        'type' : input_type

    }

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
                    complaint = ClaimModel.objects.filter(id__in=selected_entries)
                case 'CM':
                    complaint = CommunicationModel.objects.filter(id__in=selected_entries)
                case 'TR':
                    complaint = TransportModel.objects.filter(id__in=selected_entries)
                case 'VP':
                    complaint = PreparationModel.objects.filter(id__in=selected_entries)
                case 'OT':
                    complaint = OtherModel.objects.filter(id__in=selected_entries)

            
            ActionLog(
                user=request.user.person,
                target_type=get_complaint_type(complaint.get().__class__),
                target_id=complaint.get().id,
                action="status_update",
                original_value=complaint.get().status,
                new_value=new_status
            ).save()
            complaint.update(status=new_status)

            return JsonResponse({'status': 'success', 'message': 'Status updated successfully'})

        return JsonResponse({'status': 'error', 'message': 'No entries or status provided'}, status=400)

    return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

#(shows ClaimModel details)-----------------------------------------------------------------------
@login_required
def entry_detail(request, id, _type):
    set_language(request)

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

    if request.method == "POST":
        if "export" in request.POST:
            return export_single_object(request, id, entry.__class__)
        elif "download" in request.POST:
            return download_all_files(request, id, entry.__class__)
    else:
        return render(request, "entry_detail.html", {"entry" : entry})

@login_required
def statistics(request):
    set_language(request)

    # Get start_date and end_date from the GET request
    start_date_str = request.GET.get("start_date", "")
    end_date_str = request.GET.get("end_date", "")

    # Convert to datetime objects if the dates are provided
    if start_date_str and end_date_str:
        start_date = start_date_str
        end_date = end_date_str
    else:
        start_date = now()
        end_date = now()

    # Count imports by type (filter by date if provided)
    imports_by_type = (
        ActionLog.objects.filter(action="complaint_import")
        .filter(timestamp__range=[start_date, end_date] if start_date and end_date else [])
        .values("target_type")
        .annotate(count=Count("id"))
        .order_by("target_type")
    )

    # Count status changes (filter by date if provided)
    status_changes = (
        ActionLog.objects.filter(action__startswith="status_update")
        .filter(timestamp__range=[start_date, end_date] if start_date and end_date else [])
        .values("target_type", "new_value")
        .annotate(count=Count("id"))
        .order_by("target_type", "new_value")
    )

    NATURE_OF_DAMAGE_DICT = dict(NATURE_OF_DAMAGE)
    PLACE_OF_DAMAGE_DICT = dict(PLACE_OF_DAMAGE)

    # Nature of damage counts (filter by ActionLogs within the date range)
    raw_nature_of_damage_counts = (
        ClaimModel.objects.filter(id__in=ActionLog.objects.filter(action="complaint_import")
                                  .filter(timestamp__range=[start_date, end_date] if start_date and end_date else [])
                                  .values("target_id"))
        .exclude(nature_of_damage_1="XX")
        .values("nature_of_damage_1")
        .annotate(count=Count("nature_of_damage_1"))
        .union(
            ClaimModel.objects.filter(id__in=ActionLog.objects.filter(action="complaint_import")
                                      .filter(timestamp__range=[start_date, end_date] if start_date and end_date else [])
                                      .values("target_id"))
            .exclude(nature_of_damage_2="XX")
            .values("nature_of_damage_2")
            .annotate(count=Count("nature_of_damage_2"))
        )
        .union(
            ClaimModel.objects.filter(id__in=ActionLog.objects.filter(action="complaint_import")
                                      .filter(timestamp__range=[start_date, end_date] if start_date and end_date else [])
                                      .values("target_id"))
            .exclude(nature_of_damage_3="XX")
            .values("nature_of_damage_3")
            .annotate(count=Count("nature_of_damage_3"))
        )
        .order_by("-count")
    )

    # Place of damage counts (filter by ActionLogs within the date range)
    raw_place_of_damage_counts = (
        ClaimModel.objects.filter(id__in=ActionLog.objects.filter(action="complaint_import")
                                  .filter(timestamp__range=[start_date, end_date] if start_date and end_date else [])
                                  .values("target_id"))
        .exclude(place_of_damage_1="00")
        .values("place_of_damage_1")
        .annotate(count=Count("place_of_damage_1"))
        .union(
            ClaimModel.objects.filter(id__in=ActionLog.objects.filter(action="complaint_import")
                                      .filter(timestamp__range=[start_date, end_date] if start_date and end_date else [])
                                      .values("target_id"))
            .exclude(place_of_damage_2="00")
            .values("place_of_damage_2")
            .annotate(count=Count("place_of_damage_2"))
        )
        .union(
            ClaimModel.objects.filter(id__in=ActionLog.objects.filter(action="complaint_import")
                                      .filter(timestamp__range=[start_date, end_date] if start_date and end_date else [])
                                      .values("target_id"))
            .exclude(place_of_damage_3="00")
            .values("place_of_damage_3")
            .annotate(count=Count("place_of_damage_3"))
        )
        .order_by("-count")
    )

    # Total counts for percentages
    total_nature_count = sum(entry["count"] for entry in raw_nature_of_damage_counts)
    total_place_count = sum(entry["count"] for entry in raw_place_of_damage_counts)
    total_imports = sum(entry["count"] for entry in imports_by_type)
    total_status_changes = sum(entry["count"] for entry in status_changes)

    # Convert damage codes to readable names and add percentages
    nature_of_damage_counts = [
        {
            "code": entry["nature_of_damage_1"] or entry["nature_of_damage_2"] or entry["nature_of_damage_3"],
            "name": NATURE_OF_DAMAGE_DICT.get(entry["nature_of_damage_1"] or entry["nature_of_damage_2"] or entry["nature_of_damage_3"], "Unknown"),
            "count": entry["count"],
            "percentage": round((entry["count"] / total_nature_count) * 100, 2) if total_nature_count else 0,
        }
        for entry in raw_nature_of_damage_counts
    ]

    place_of_damage_counts = [
        {
            "code": entry["place_of_damage_1"] or entry["place_of_damage_2"] or entry["place_of_damage_3"],
            "name": PLACE_OF_DAMAGE_DICT.get(entry["place_of_damage_1"] or entry["place_of_damage_2"] or entry["place_of_damage_3"], "Unknown"),
            "count": entry["count"],
            "percentage": round((entry["count"] / total_place_count) * 100, 2) if total_place_count else 0,
        }
        for entry in raw_place_of_damage_counts
    ]

    # Add percentage to imports and status changes
    imports_by_type = [
        {
            **entry,
            "percentage": round((entry["count"] / total_imports) * 100, 2) if total_imports else 0,
        }
        for entry in imports_by_type
    ]

    status_changes = [
        {
            **entry,
            "percentage": round((entry["count"] / total_status_changes) * 100, 2) if total_status_changes else 0,
        }
        for entry in status_changes
    ]

    context = {
        "imports_per_month": imports_by_type,
        "status_changes": status_changes,
        "nature_of_damage_counts": nature_of_damage_counts,
        "place_of_damage_counts": place_of_damage_counts,
    }

    return render(request, "statistics.html", context)



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
    Milý {complaint.first_name} {complaint.second_name},

    Ďakujeme za podanie reklamacie. Tu sú podrobnosti o vašom podaní:

    - Dátum podania: {complaint.date}
    - Správa: {complaint.message}

    Náš tím vašu reklamáciu preskúma a čoskoro vás kontaktuje.

    S pozdravom,
    CEVA Logistic
    
    -------------------------------------------

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
    Nová reklamácia bola podaná s nasledujúcimi podrobnosťami:

    - ID reklamácie: {complaint.id}
    - Dátum podania: {complaint.date}
    - Správa: {complaint.message}

    Prosím, skontrolujte reklamáciu a podniknite príslušné kroky.

    -------------------------------------------

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


def logs(request):
    set_language(request)
    input_date_from = request.GET.get('date_from', '')
    input_date_to = request.GET.get('date_to', '')
    input_id = request.GET.get('id', '')
    input_user = request.GET.get('user', '')
    input_target_type = request.GET.get('target_type', '')
    input_target_id = request.GET.get('target_id', '')
    input_action = request.GET.get('action', '')



    filters = {
        'date_from': request.GET.get('date_from', ''),
        'date_to': request.GET.get('date_to', ''),
        'id': request.GET.get('id', ''),
        'user': request.GET.get('user', ''),
        'target_type': request.GET.get('target_type', ''),
        'target_id': request.GET.get('target_id', ''),
        'action': request.GET.get('action', '')
    }
    entries = ActionLog.objects.all().order_by('-id')

    if input_date_from:
        entries = entries.filter(timestamp__gte=input_date_from)
    if input_date_to:
        entries = entries.filter(timestamp__lte=input_date_to)
    if input_id:
        entries = entries.filter(id__icontains=input_id)
    if input_user:
        user_ids = User.objects.filter(
            Q(username__icontains=input_user) | 
            Q(first_name__icontains=input_user) | 
            Q(last_name__icontains=input_user)
        ).values_list('id', flat=True)  # Get matching user IDs

        entries = entries.filter(user_id__in=user_ids) 
    if input_target_type:
        entries = entries.filter(target_type__icontains=input_target_type)
    if input_target_id:
        entries = entries.filter(target_id__icontains=input_target_id)
    if input_action:
        entries = entries.filter(action__icontains=input_action)

    paginator = Paginator(entries, 100)  # Show 50 entries per page
    page_number = request.GET.get('page', 1)  # Get current page, default to 1
    page_obj = paginator.get_page(page_number)  # Get the page object

    context = {
        'report_types': REPORT_TYPES,
        'filters' : filters,
        'entries' : page_obj
    }

    return render(request, "logs.html", context)