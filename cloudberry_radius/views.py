from __future__ import unicode_literals

from warnings import warn

from django.shortcuts import render, redirect
from django.views.decorators.http import require_GET

from paypal.standard.pdt.forms import PayPalPDTForm
from paypal.standard.pdt.models import PayPalPDT
from paypal.utils import warn_untested

from django.shortcuts import render
import django.db.models
import django.db.models
import cloudberry_radius.models
import django_admin_ownership.models

from .models import RadiusAccounting

import paypalrestsdk
client_id = "AcVFttUpFaVG7IWsnhWGdr44_H0m2IM7G-X5ONi0OF4pALNB-1Jv1b_250mCapimGcKc2mNkMoARBcDq"
client_secret = "EHelJbyrsFaN8r9GH6COPYoercXs9RS36X5cV0WIzi7i1sUrG9zt1sge3Htz2032Tv58jfHPewCjlcPH"
paypalrestsdk.configure({
      'mode': 'sandbox', #sandbox or live
      'client_id': client_id,
      'client_secret': client_secret })

from paypalrestsdk import Payout, ResourceNotFound

def account_balance(request):
    return render(request,
                  'cloudberry_radius/account_balance.html',
                  {'balance': request.user.radius_accounting.all().aggregate(django.db.models.Sum('amount'))['amount__sum'],
                   'accounting': request.user.radius_accounting.all().order_by('-start_time')})

def device_owner_account_balance(request):
    groups = django_admin_ownership.models.ConfigurationGroup.objects.filter(
        django.db.models.Q(owner=request.user)
        | django.db.models.Q(write__user=request.user))

    res = []
    for group in groups:
        accounting = cloudberry_radius.models.RadiusAccounting.objects.filter(
            django.db.models.Q(device__group=group)
            | django.db.models.Q(withdrawal_group=group))
        res.append({'group': group,
                    'balance': -(accounting.aggregate(django.db.models.Sum('amount'))['amount__sum'] or 0),
                    'accounting': accounting.order_by('-start_time')})
        
    return render(request,
                  'cloudberry_radius/device_owner_account_balance.html',
                  {'accountings': res})
        
def payout(request):
    sender_batch_id = ''.join(
        random.choice(string.ascii_uppercase) for i in range(12))

    groups = django_admin_ownership.models.ConfigurationGroup.objects.filter(
        django.db.models.Q(owner=request.user)
        | django.db.models.Q(write__user=request.user))

    res = []
    for group in groups:
        accounting = cloudberry_radius.models.RadiusAccounting.objects.filter(
            django.db.models.Q(device__group=group)
            | django.db.models.Q(withdrawal_group=group))
        res.append({'group': group,
                    'balance': -(accounting.aggregate(django.db.models.Sum('amount'))['amount__sum'] or 0)})

    payout = Payout({
        "sender_batch_header": {
            "sender_batch_id": sender_batch_id,
            "email_subject": "Your Cloudberry device payment"
        },
        "items": [
            {
                "recipient_type": "EMAIL",
                "amount": {
                    "value": res.balance,
                    "currency": "USD"
                },
                "receiver": request.user.email,
                "note": "Thank you.",
                "sender_item_id": "item_1"
            }
        ]
    })
    
    if payout.create(sync_mode=True):
        res = []
        for group in groups:
            accounting = cloudberry_radius.models.RadiusAccounting.objects.filter(
                django.db.models.Q(device__group=group)
                | django.db.models.Q(withdrawal_group=group))
            res.append({'group': group,
                        'balance': 0,
                        'accounting': accounting.order_by('-start_time'),
                        'payout_id': payout.batch_header.payout_batch_id})
        return render(request,
                      'cloudberry_radius/device_owner_account_balance.html',
                      {'accountings': res})
    # else:
    #     print(payout.error)
    
@require_GET
def pdt(request, template="cloudberry_order/done.html", context=None):
    """Standard implementation of a view that processes PDT and then renders a template
    For more advanced uses, create your own view and call process_pdt.
    """
    warn("Use of pdt view is deprecated. Instead you should create your\n"
         "own view, and use the process_pdt helper function",
         DeprecationWarning)
    pdt_obj, failed = process_pdt(request)

    if failed:
        contect = failed
        return render(request, template, context)
    else:
        a = RadiusAccounting()
        a.amount = pdt_obj.amt
        a.user = request.user
        a.save()
        return redirect('cloudberry_radius:account_balance')

def process_pdt(request):
    """
    Payment data transfer implementation:
    https://developer.paypal.com/webapps/developer/docs/classic/products/payment-data-transfer/

    This function returns a tuple of (pdt_obj, failed)
    pdt_obj is an object of type PayPalPDT
    failed is a flag that is True if the input data didn't pass basic validation.

    Note: even for failed=False You must still check the pdt_obj is not flagged i.e.
    pdt_obj.flag == False
    """

    pdt_obj = None
    txn_id = request.GET.get('tx')
    failed = False
    if txn_id is not None:
        # If an existing transaction with the id tx exists: use it
        try:
            pdt_obj = PayPalPDT.objects.get(txn_id=txn_id)
        except PayPalPDT.DoesNotExist:
            # This is a new transaction so we continue processing PDT request
            pass

        if pdt_obj is None:
            form = PayPalPDTForm(request.GET)
            if form.is_valid():
                try:
                    pdt_obj = form.save(commit=False)
                except Exception as e:
                    warn_untested()
                    error = repr(e)
                    failed = True
            else:
                warn_untested()
                error = form.errors
                failed = True

            if failed:
                warn_untested()
                pdt_obj = PayPalPDT()
                pdt_obj.set_flag("Invalid form. %s" % error)

            pdt_obj.initialize(request)

            if not failed:
                # The PDT object gets saved during verify
                pdt_obj.verify()
    else:
        pass  # we ignore any PDT requests that don't have a transaction id

    return (pdt_obj, failed)

