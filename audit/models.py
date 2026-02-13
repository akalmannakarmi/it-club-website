from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from audit.middleware.current_user import get_current_user


class ActiveManager(models.Manager):
    """Default manager that filters out soft-deleted records."""

    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)


class BaseModel(models.Model):
    """
    Abstract base model with:
    - deleted_at: soft delete timestamp
    - created_at / updated_at: timestamps
    - automatic audit logging
    """

    deleted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects_all = models.Manager()
    objects = ActiveManager()

    class Meta:
        abstract = True

    def _serialize_instance(self):
        data = {}

        # Regular fields + ForeignKeys
        for field in self._meta.fields:
            value = getattr(self, field.name)

            if field.is_relation:  # ForeignKey / OneToOne
                value = f"[{value.pk}]{str(value)}" if value else None

            data[field.name] = str(value) if value is not None else None

        # ManyToMany fields
        for field in self._meta.many_to_many:
            values = getattr(self, field.name).all()

            data[field.name] = [f"[{obj.pk}]{str(obj)}" for obj in values]

        return data

    def _get_user(self):
        if user := get_current_user():
            return user
        if isinstance(self, User):
            return self
        if hasattr(self, "user") and isinstance(self.user, User):
            return self.user
        return None

    def save(self, no_audit=False, *args, **kwargs):
        is_create = self._state.adding

        super().save(*args, **kwargs)
        if no_audit:
            return

        AuditLog.objects.create(
            user=self._get_user(),
            model_name=self.__class__.__name__,
            object_id=self.pk,
            action="create" if is_create else "update",
            changes=self._serialize_instance(),
        )

    def delete(self, *args, **kwargs):
        """Soft delete: mark deleted_at instead of removing row."""
        self.deleted_at = timezone.now()
        self.save(no_audit=True)

        AuditLog.objects.create(
            user=self._get_user(),
            model_name=self.__class__.__name__,
            object_id=self.pk,
            action="delete",
            changes=self._serialize_instance(),
        )


User = get_user_model()


class AuditLog(models.Model):
    ACTIONS = [
        ("create", "Create"),
        ("update", "Update"),
        ("delete", "Delete"),
    ]

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    model_name = models.CharField(max_length=100)
    object_id = models.IntegerField()
    action = models.CharField(max_length=10, choices=ACTIONS)
    timestamp = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"{self.model_name} ({self.object_id}) {self.action} by {self.user}"
