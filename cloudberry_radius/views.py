from django.shortcuts import render
import django.db.models

def account_balance(request):
    return render(request,
                  'cloudberry_radius/account_balance.html',
                  {'balance': request.user.radius_accounting.all().aggregate(django.db.models.Sum('amount'))['amount__sum'],
                   'accounting': request.user.radius_accounting.all().order_by('-start_time')})
