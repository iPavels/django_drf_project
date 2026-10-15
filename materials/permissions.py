from rest_framework.permissions import BasePermission, SAFE_METHODS


def is_moderator(user):
    """Проверяет, состоит ли пользователь в группе модераторов."""
    return (
        user.is_authenticated
        and user.groups.filter(name="Модераторы").exists()
    )


class IsOwnerOrModerator(BasePermission):
    """
    Владелец работает со своими объектами.
    Модератор просматривает и редактирует любые объекты,
    но не может создавать или удалять их.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        moderator = is_moderator(request.user)

        if moderator and request.method in ("POST", "DELETE"):
            return False

        return True

    def has_object_permission(self, request, view, obj):
        if is_moderator(request.user):
            return request.method != "DELETE"

        return getattr(obj, "owner_id", None) == request.user.pk
