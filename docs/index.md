# Django Object Lock documentation

>   Oops! I think I've edited the wrong object.
>   
>   We don't need to edit this any longer, but need to keep it in an "archive" state...

**Django Object Lock** (`django-object-lock`) adds a "locked" status to your models to prevent their unintentional
modification or deletion from your Django admin site, your API or any view. You can "lock" an instance to protect it
and then "unlock" it to allow further modifications or deletions.

```{toctree}
:maxdepth: 1

installation
model-locking
admin-locking
api-locking
settings
changelog
```
