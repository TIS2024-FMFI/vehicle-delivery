from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.db.models import Q
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
from .export import export_single_object, download_all_files
from .logging import get_complaint_type




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

    # Create a new department if ID is 0
    if id == 0:
        if request.method == 'POST' and request.POST.get('save'):
            department_instance = Department.objects.create()
            form = DepartmentForm(request.POST, instance=department_instance)

            if form.is_valid():
                form.save()
                ActionLog.objects.create(
                    user=request.user.person,
                    target_type=get_complaint_type(Department),
                    target_id=department_instance.id,
                    action="create",
                    new_value=department_instance.name
                )
                return redirect('/departments/')
        
        return render(request, "departments/department_form.html", {'form': DepartmentForm()})

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

    return render(request, "departments/department_form.html", {'form': form})

@admin_required
def form_create_person(request):
    activate(request.session["language"])
    
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
    activate(request.session["language"])
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

    activate(request.session["language"])
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

    activate(request.session["language"])
    if request.method == 'POST':
        if request.POST.get('passwd'):
            return redirect(f'/change_passwd/{request.POST.get('passwd')}/')
        elif request.POST.get('update'):
            return redirect(f'/update_person/{request.POST.get('update')}/')


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
    activate(request.session["language"])
    return render(request, "forms.html")

def form_claim(request):
    activate(request.session["language"])
    if request.method == 'POST':
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            complaint = form.save()

            ActionLog.objects.create(
                user=request.user.person,
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
    activate(request.session["language"])
    if request.method == 'POST':
        form = CommunicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            complaint = form.save()

            ActionLog.objects.create(
                user=request.user.person,
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
    activate(request.session["language"])
    if request.method == 'POST':
        form = OtherForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            complaint = form.save()

            ActionLog.objects.create(
                user=request.user.person,
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
    activate(request.session["language"])
    if request.method == 'POST':
        form = TransportForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            complaint = form.save()

            ActionLog.objects.create(
                user=request.user.person,
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
    activate(request.session["language"])
    if request.method == 'POST':
        form = PreparationForm(request.POST, request.FILES)
        if form.is_valid():
            form.status = 'new'
            complaint = form.save()

            ActionLog.objects.create(
                user=request.user.person,
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
def entry_detail(request, id):
    activate(request.session["language"])

    entry = None
    if request.user.person.department == None:
        entry = ClaimModel.objects.get(id=id)
    else:
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

    if request.method == "POST":
        if "export" in request.POST:
            return export_single_object(request, id, entry.__class__)
        elif "download" in request.POST:
            return download_all_files(request, id, entry.__class__)
    else:
        return render(request, "entry_detail.html", {"entry" : entry})

@login_required
def statistics(request):
    activate(request.session["language"])
    return render(request, "statistics.html")




def no_access(request):
    return render(request, 'no_access.html', {"message": "You do not have permission to access this page."})

def thanks(request):
    return render(request, "thank.html")

