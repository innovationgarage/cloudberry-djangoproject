from ..models import *
from django_netjsonconfig.controller.generics import (
    BaseChecksumView,
    BaseDownloadConfigView,
    BaseRegisterView,
    BaseReportStatusView
)
from  django_netjsonconfig.utils import get_object_or_404

class ChecksumView(BaseChecksumView):
    model = Device

class DownloadConfigView(BaseDownloadConfigView):
    model = Device
    def get_object(self, *args, **kwargs):
        return get_object_or_404(self.model, *args, **kwargs)

class ReportStatusView(BaseReportStatusView):
    model = Device

class RegisterView(BaseRegisterView):
    model = Device

checksum = ChecksumView.as_view()
download_config = DownloadConfigView.as_view()
report_status = ReportStatusView.as_view()
register = RegisterView.as_view()
