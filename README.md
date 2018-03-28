# Cloudberry djangoproject

This django project is an extension on top of https://github.com/openwisp/django-netjsonconfig that provides a radically different configuration and templating system:

* Multiple devices can be configured together in a single configuration that refers to the devices for various roles (e.g. server, clients, different types of clients...)
* Configuration can be arbitrarily abstracted using transformations written in the [SakForm](https://github.com/innovationgarage/sakstig) JSON templating language
* Configuration can optionally refer to other resources using drop-downs (e.g. certificates, CA:s)
​
# Installation

    apt install -y apache2 libapache2-mod-wsgi-py3 python3 python3-pip
    pip3 install -r requirements.txt
    python3 manage.py migrate
    python3 manage.py collectstatic
    python3 manage.py createsuperuser
    ln -s \
      /srv/www/cloudberry-djangoproject/cloudberry-djangoproject.conf \
      /etc/apache2/mods-enabled/cloudberry-djangoproject.conf
    chown -R www-data:www-data .
    /etc/init.d/apache2 restart

