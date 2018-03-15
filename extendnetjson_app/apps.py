from django_netjsonconfig.apps import DjangoNetjsonconfigApp
from models import *

class CloudberryDjangoprojectConfig(DjangoNetjsonconfigApp):
    name = 'extendnetjson_app'

    def __setmodels__(self):
        self.config_model = Config
        self.vpnclient_model = VpnClient
