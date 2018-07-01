from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import views as auth_views

def homepage(request):
    if not request.user.is_authenticated:
        return auth_views.redirect_to_login(resolve_url('index'))
    if request.user.is_staff:
        return redirect('admin:index')
    return render(request, 'cloudberry_accounts/index.html')
