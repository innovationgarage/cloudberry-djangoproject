# from django.shortcuts import render
# from django.views.decorators.http import require_GET
# from django.conf import settings

# @require_GET
# def payment_process(request):
#     pdt_obj, failed = process_pdt(request)
#     context = {"failed": failed, "pdt_obj": pdt_obj}
#     if not failed:

#         # WARNING!
#         # Check that the receiver email is the same we previously
#         # set on the business field request. (The user could tamper
#         # with those fields on payment form before send it to PayPal)

#         if pdt_obj.receiver_email == "settings.PAYPAL_RECEIVER_EMAIL":

#             # ALSO: for the same reason, you need to check the amount
#             # received etc. are all what you expect.

#             # Do whatever action is needed, then:
#             return render(request, 'my_valid_payment_template', context)
#     return render(request, 'my_non_valid_payment_template', context)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from warnings import warn

from django.shortcuts import render
from django.views.decorators.http import require_GET

from paypal.standard.pdt.forms import PayPalPDTForm
from paypal.standard.pdt.models import PayPalPDT
from paypal.utils import warn_untested


@require_GET
def pdt(request, template="cloudberry_order/done.html", context=None):
    """Standard implementation of a view that processes PDT and then renders a template
    For more advanced uses, create your own view and call process_pdt.
    """
    warn("Use of pdt view is deprecated. Instead you should create your\n"
         "own view, and use the process_pdt helper function",
         DeprecationWarning)
    pdt_obj, failed = process_pdt(request)

    context = context or {}
    context.update({"failed": failed, "pdt_obj": pdt_obj})
    return render(request, template, context)


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

