from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    """Manager for the email-based HubOS user model."""

    use_in_migrations = True

    @staticmethod
    def normalize_email_address(email: str) -> str:
        """HubOS email policy: addresses are case-insensitive and stored lowercase."""
        return email.strip().lower()

    def get_by_natural_key(self, email):
        # Natural-key lookups (including authenticate()) compare case-insensitively.
        return self.get(email__iexact=self.normalize_email_address(email))

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("An email address must be provided."))
        email = self.normalize_email_address(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self._create_user(email, password, **extra_fields)
