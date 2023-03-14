from app.core import models, exceptions


def is_superuser_or_owner(current_user: models.User, object_id: int | str):
    if current_user.is_superuser:
        return True

    if current_user.id == object_id:
        raise exceptions.PermissionDenied()

    return True
