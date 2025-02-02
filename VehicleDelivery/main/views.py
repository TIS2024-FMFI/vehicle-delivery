from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from .forms import *
from .models import *
from functools import wraps
from django.contrib.auth.forms import PasswordChangeForm


# Create your views here.
def hello_world(request):
    return HttpResponse("Hello, World!")

def home(request):
    return render(request, "home.html")

def form_department(request, id):
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

def form_create_person(request):
    if request.method == 'POST':
        form = PersonForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/users/')
    else:
        form = PersonForm()
    return render(request, "registration/create_user.html", {'form': form})

def form_change_person_passwd(request, id):
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

def form_update_person(request, id):
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


def users(request):
    if request.method == 'POST':
        if request.POST.get('passwd'):
            return redirect(f'/change_passwd/{request.POST.get('passwd')}/')
        elif request.POST.get('update'):
            return redirect(f'/update_person/{request.POST.get('update')}/')    
    user = User.objects.all().order_by('username')
    return render(request, "registration/users.html", {'users': user})

def departments(request):
    if request.method == 'POST':
        if request.POST.get('add'):
            department = Department()
            department.save()
        elif request.POST.get('department'):
            department = Department.objects.get(id=request.POST.get('department'))

        return redirect(f'/form_department/{department.id}/')
    
    departments = Department.objects.all().order_by('name')
    return render(request, "departments/departments.html", {'departments': departments})

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





def form_claim(request):
    if request.method == 'POST':
        form = ClaimForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = ClaimForm()

    return render(request, "form_claim.html", {'form': form})

def form_communication(request):
    if request.method == 'POST':
        form = CommunicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/thanks/')
        else:
            print(form.errors)
    else:
        form = CommunicationForm()

    return render(request, "form_communication.html", {'form': form})

def form_other(request):
    if request.method == 'POST':
        form = OtherForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = OtherForm()

    return render(request, "form_other.html", {'form': form})

def form_transport(request):
    if request.method == 'POST':
        form = TransportForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = TransportForm()

    return render(request, "form_transport.html", {'form': form})

def form_preparation(request):
    if request.method == 'POST':
        form = PreparationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/thanks/')
    else:
        form = PreparationForm()

    return render(request, "form_preparation.html", {'form': form})


#(shows ClaimModel entries)----------------------------------------------------------------------
def agent_dashboard(request):
    entries = ClaimModel.objects.all()
    return render(request, "agent_dashboard.html", {'entries': entries})

#(shows ClaimModel details)-----------------------------------------------------------------------
def entry_detail(request, id):
    entry = ClaimModel.objects.get(id=id)
    return render(request, "entry_detail.html", {"entry" : entry})




def thanks(request):
    return render(request, "thank.html")

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

def view_submissions(request):
    people = Person.objects.all()
    return render(request, 'list.html', {'people': people})
