from django.shortcuts import render

def account_balance(request):
    return render(request,
                  'cloudberry_order/account_balance.html',
                  {'accounting': request.user.radius_accounting.all(),
                   'orders': request.user.orders.all()})
