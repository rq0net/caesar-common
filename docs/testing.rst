
.. include:: links.inc

Testing
=======
You can run the tests by ::

    SECRET_KEY=my_secret_key python manage.py test

or by ::

    python setup.py test

or by ::

    DJANGO_SETTINGS_MODULE=caesar_auth.config.local SECRET_KEY=my_secret_key pytest
