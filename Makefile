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
