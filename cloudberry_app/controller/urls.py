from django_netjsonconfig.utils import get_controller_urls
from . import views

app_name = 'cloudberry_app'

urlpatterns = get_controller_urls(views)
