# Model-level locking

Model-level locking allows you to prevent saving an object (using the
[`save()`](https://docs.djangoproject.com/en/4.2/ref/models/instances/#django.db.models.Model.save) method) or 
deleting it (using the
[`delete()`](https://docs.djangoproject.com/en/4.2/ref/models/instances/#django.db.models.Model.delete>) method).
If the object you're trying to save or delete is locked, an `ObjectLocked` exception is raised which you can use to
handle this situation.

```{important}
When using `QuerySet` methods such as
[`update`](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#update) or
[`bulk_update`](https://docs.djangoproject.com/en/4.2/ref/models/querysets/#bulk-update), the lock status is not
checked and therefore the object may be updated or deleted without throwing the exception.
```

To use model-level locking, inherit from the abstract `LockableModel` and implement the `is_locked()` method, which
must return `True` if your model instance is locked and `False` otherwise. This function will be evaluated when calling
`save()` or `delete()`.

Optionally, if you want the locked status to be set directly for an instance, implement `set_locked(value)` and define
your own logic for locking or unlocking the object.

```{important}
In order to determine whether updates are allowed to a locked object, lockable model instances remember
whether they have been locked at the moment they are fetched from the database or not, so an instance may be fetched
unlocked and then locked manually or automatically.

In that case, the instance will be successfully saved because it has not been locked in the database yet. After that,
the instance will be locked and the next successful save must unlock the instance.
```


## Making objects lockable with a flag

`django-object-lock` does not provide a default "locked" flag to your model. Instead, you define `is_locked()` and
use your own attribute to indicate that an object is locked or not.

In this case you will need to define `set_locked(value)` as well to set the "locked" flag to the appropiate value.

For example:

```python
from django.db import models
from django_object_lock.models import LockableModel


class Article(LockableModel):
    title = models.CharField(max_length=120)
    is_locked_flag = models.BooleanField(default=False)

    def is_locked(self) -> bool:
        return self.is_locked_flag

    def set_locked(self, value: bool) -> None:
        self.is_locked_flag = value
```

You could let the user set the `is_locked_flag`, or add more logic in any of these methods that your may require.


## Making related objects lockable

In other cases it may not make sense to use a flag attribute to control whether the instance is locked or not, and
that is why the `is_locked()` method is provided instead of an attribute.

For example, if a lockable object may have "child" objects, you can lock the child objects if and only if the parent
has been manually locked. That is the case of `Article`s and `ArticleSection`s.

```python
class ArticleSection(LockableModel):
    parent = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='sections')
    heading = models.CharField(max_length=120)
    content = models.TextField()
    order = models.IntegerField()

    class Meta:
        ordering = ['order']

    def __str__(self) -> str:
        return f'ArticleSection "{self.heading}"'

    def is_locked(self) -> bool:
        return self.parent.is_locked_flag
```

Note that in this case you do not need to implement `set_locked(value)`, because the locked status would be
automatically set via the parent `Article`. That is, unless we needed to make each section lockable on its own.

```{note}
Remember that when you are accessing attributes on related objects you may encounter a *N + 1* problem. Use
`select_related` to reduce the number of database queries when checking lock status for a large amount of instances.
```


## Locking objects automatically according to a condition

Suppose we wanted to prevent edition of `Articles` that have been already published. We can implement this logic
in our `is_locked`.

```python
from django.db import models
from django.utils.timezone import now
from django_object_lock.models import LockableModel


class Article(LockableModel):
    title = models.CharField(max_length=120)
    is_locked_flag = models.BooleanField(default=False)
    published_at = models.DateTimeField()

    def is_locked(self) -> bool:
        return self.published_at >= now()
```

Now published articles may not be edited nor deleted. Again, there is no `set_locked(value)` method because it would
not make sense.
