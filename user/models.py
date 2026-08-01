from django.db import models
from audit.models import BaseModel
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import datetime
from django.contrib.auth.models import BaseUserManager, Group


class UserManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Users must have an email address")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        user = self.create_user(email, password, **extra_fields)

        admin_group, created = Group.objects.get_or_create(name="Admin")
        user.groups.add(admin_group)

        return user


class User(AbstractUser, BaseModel):
    FACULTY_CHOICES = [
        ("CSIT", "BSc CSIT"),
        ("BCA", "BCA"),
        ("BBS", "BBS"),
        ("BBM", "BBM"),
        ("MBA", "MBA"),
        ("BIT", "BIT"),
    ]

    def batch_choices():
        start_year = 2068
        current_year = datetime.now().year + 57
        return [(str(year), str(year)) for year in range(start_year, current_year + 1)]

    username = None
    email = models.EmailField("email address", unique=True)
    faculty = models.CharField(max_length=10, choices=FACULTY_CHOICES, blank=True)
    batch = models.CharField(max_length=10, choices=batch_choices(), blank=True)
    phone = models.CharField(max_length=15, blank=True)
    interested_topics = models.TextField(help_text="Comma separated topics", blank=True)

    objects = UserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.full_name or self.email

    @property
    def full_name(self):
        name = f"{self.first_name} {self.last_name}".strip()
        return name or self.email

    @property
    def group_names(self):
        if "_group_names" not in self.__dict__:
            self._group_names = set(self.groups.all().values_list("name", flat=True))
        return self._group_names

    @property
    def is_admin_group(self):
        return "Admin" in self.group_names
