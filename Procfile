web: gunicorn hashmicro_django_dev_test --log-file -
web: python manage.py migrate && gunicorn hashmicro_django_dev_test.wsgi