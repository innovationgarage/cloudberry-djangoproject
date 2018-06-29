from django.shortcuts import render

def account_balance(request):
    return render(request,
                  'cloudberry_radius/account_balance.html',
                  {'accounting': request.user.radius_accounting.all().order_by('-start_time')})
