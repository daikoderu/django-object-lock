# Installation

To use `django-object-lock` in your own project, install the Python library from PyPI:

```sh
pip install django-object-lock
```

Then add `django_object_lock` to your `INSTALLED_APPS` in your settings:

```py
INSTALLED_APPS = [
    # ...
    'rest_framework'  # If you have a Django REST framework API
    # ...
    'django_object_lock',
]
```

See ["Model locking"](#model-locking) to find out how can you implement model-level locking.
However, if you are not interested in making object locking effective from all your interfaces, you may lock
objects only [from the admin](#admin-locking) or [from your Django REST Framework API](#api-locking).
