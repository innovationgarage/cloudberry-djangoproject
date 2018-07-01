from django.shortcuts import render, redirect, resolve_url
from django.contrib.auth import views as auth_views
import registration.backends.default.views
import registration.forms
import django.forms
from django.utils.translation import gettext as _

def homepage(request):
    if not request.user.is_authenticated:
        return auth_views.redirect_to_login(resolve_url('index'))
    if request.user.is_staff:
        return redirect('admin:index')
    return render(request, 'cloudberry_accounts/index.html')

class CustomRegistrationForm(registration.forms.RegistrationForm):
    class Meta(registration.forms.RegistrationForm.Meta):
        fields = registration.forms.RegistrationForm.Meta.fields + ('is_staff',)
    is_staff = django.forms.ChoiceField(
         label=_("User type"),
         choices=[(False, 'Internet user (subscriber)'), (True, 'Hotspot owner')],
         help_text = "Chose 'Internet user' to be able to surf the internet using one of" +
         "our hotspot. Chose 'Hotspot owner' if you want to provide internet for" +
         "your customers or staff."
    )
    
register = registration.backends.default.views.RegistrationView.as_view(
    form_class=CustomRegistrationForm
)
