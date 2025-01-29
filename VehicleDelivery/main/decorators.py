from django.shortcuts import redirect
from functools import wraps

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login') 
        
        if not request.user.person.user_type == 'ADMIN':
            return redirect('no_access')

        return view_func(request, *args, **kwargs)
    
    return _wrapped_view


def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')

        return view_func(request, *args, **kwargs)
    
    return _wrapped_view