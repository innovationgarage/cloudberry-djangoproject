ifndef VIRTUAL_ENV
env/bin/activate:
	virtualenv env -p python3
$(MAKECMDGOALS): env/bin/activate
	. env/bin/activate; $(MAKE) $(MAKECMDGOALS)
else

dev: install-depends migrate
	python3 manage.py runserver

install-depends:
	pip3 --disable-pip-version-check install -r requirements.txt

migrate:
	python3 manage.py makemigrations
	python3 manage.py showmigrations
	python3 manage.py migrate

createsuperuser:
	python3 manage.py createsuperuser

defaultdata:
	python3 manage.py import_file --resource-class django_admin_ownership.importexport.GroupResource examples/Groups.json
	python3 manage.py import_file --resource-class django_admin_ownership.importexport.ConfigurationGroupResource examples/ConfigurationGroups.json
	python3 manage.py import_file --resource-class cloudberry_app.importexport.BackendResource examples/Backends.json

jenkins:
	./setup-jenkins.sh

endif
