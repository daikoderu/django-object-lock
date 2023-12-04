# Settings

All configuration related to `django-object-lock` is stored in the `DJANGO_OBJECT_LOCK` object, in your Django
settings. To make changes to the default settings, just add the dictionary with the corresponding settings.
For example:

```python
DJANGO_OBJECT_LOCK = {
    'DEFAULT_LOCKED_ICON_URL': 'myapp/images/lock.png'
}
```

Your Django project will be reloaded when any of these settings change.


## List of settings

`DEFAULT_LOCKED_ICON_URL: str`
    A string representing a static resource (image) to be used as the "locked" icon by default.
    You can override it for a specific admin by setting `locked_icon_url` in that admin.
