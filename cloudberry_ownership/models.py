from django.db import models

import django_admin_ownership.models
import django_x509.models
import django_freeradius.models

django_x509.models.Ca.add_to_class(
    'group', models.ForeignKey(django_admin_ownership.models.ConfigurationGroup,
                               on_delete=models.CASCADE))

django_x509.models.Ca._configuration_group = ["group"]
django_x509.models.Cert._configuration_group = ["ca", "group"]


django_freeradius.models.Nas.add_to_class(
    'group', models.ForeignKey(django_admin_ownership.models.ConfigurationGroup,
                               on_delete=models.CASCADE))
django_freeradius.models.Nas._configuration_group = ["group"]
