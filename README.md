# Cloudberry djangoproject

[![Build Status](http://build.innovationgarage.tech/buildStatus/icon?job=innovationgarage/cloudberry-djangoproject/master)](http://build.innovationgarage.tech/job/innovationgarage/job/cloudberry-djangoproject/job/master/)

This django project is an extension on top of https://github.com/openwisp/django-netjsonconfig that provides a radically different configuration and templating system:

* Multiple devices can be configured together in a single configuration that refers to the devices for various roles (e.g. server, clients, different types of clients...)
* Configuration can be arbitrarily abstracted using transformations written in the [SakForm](https://github.com/innovationgarage/sakstig) JSON templating language
* Configuration can optionally refer to other resources using drop-downs (e.g. certificates, CA:s)

# Installation

    apt install -y apache2 libapache2-mod-wsgi-py3 python3 python3-pip
    pip3 install -r requirements.txt
    python3 manage.py migrate
    python3 manage.py collectstatic
    python3 manage.py createsuperuser
    
    python manage.py import_file --resource-class django_admin_ownership.importexport.GroupResource examples/Groups.json
    python manage.py import_file --resource-class django_admin_ownership.importexport.ConfigurationGroupResource examples/ConfigurationGroups.json
    python manage.py import_file --resource-class cloudberry_app.importexport.BackendResource examples/Backends.json

    ln -s \
      /srv/www/cloudberry-djangoproject/cloudberry-djangoproject.conf \
      /etc/apache2/mods-enabled/cloudberry-djangoproject.conf
    chown -R www-data:www-data .
    /etc/init.d/apache2 restart

## See also

* [docker-manager](https://github.com/innovationgarage/cloudberry-docker-manager) - OpenWISP front-end to docker
* [lede-openwisp-docker](https://github.com/innovationgarage/cloudberry-lede-openwisp-docker) - OpenWISP docker image
