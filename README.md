# Django Object Lock

`django-object-lock` helps you "lock" your model instances to make them read-only and avoid
unintended modifications or deletions on your locked objects. You can then "unlock" your objects
to make them editable again.

## Features

*   A `LockableAdminMixin` your model admins can inherit from to support instance locking.
    An icon will appear in the changelist for each locked instance.

    ![Locked articles](docs/images/example-article.png)

*   The possibility to control under what conditions are your objects locked.

    For example, you can have a parent model that can be locked setting manually a Boolean field
    and a child model that will be automatically locked or unlocked whenever its parent is.

    ![Locked articles](docs/images/example-article-section.png)

    This way, you can lock and unlock entire hierarchies of model instances.

There is no ``LockableModel`` in order to prevent this library from being coupled to your models
and your database. Instead, use the admin mixins to define when an object is locked.
