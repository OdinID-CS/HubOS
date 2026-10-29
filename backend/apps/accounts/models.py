"""HubOS custom user model.

Sign-in identity is the email address. HubOS treats email addresses as
case-insensitive: addresses are normalized to lowercase on save, and a
database-level unique constraint on LOWER(email) enforces case-insensitive
uniqueness even for writes that bypass model normalization. No CIText
extension is required.
"""
import uuid

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.db.models.functions import Lower
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .managers import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(
        _("email address"),
        max_length=254,
        unique=True,
        help_text=_(
            "Unique. Stored lowercase (case-insensitive); a database-level "
            "LOWER(email) unique constraint guards against case variants."
        ),
    )
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user can sign in. Deactivate instead of "
            "deleting to preserve audit history."
        ),
    )
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_("Designates access to the Django admin site."),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ["date_joined"]
        constraints = [
            models.UniqueConstraint(
                Lower("email"),
                name="accounts_user_email_ci_unique",
                violation_error_message=_(
                    "A user with this email address already exists."
                ),
            ),
        ]
        indexes = [
            models.Index(Lower("email"), name="accounts_user_email_lower_idx"),
        ]

    def clean(self):
        super().clean()
        self.email = type(self).objects.normalize_email_address(self.email)

    def __str__(self):
        return self.email


class InstitutionalProfile(models.Model):
    class VerificationStatus(models.TextChoices):
        UNVERIFIED = "UNVERIFIED", _("Unverified")
        PENDING = "PENDING", _("Pending review")
        VERIFIED = "VERIFIED", _("Verified")
        REJECTED = "REJECTED", _("Rejected")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="institutional_profile",
    )
    institutional_email = models.EmailField(blank=True, null=True)
    institutional_id = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=150, blank=True)
    designation = models.CharField(max_length=150, blank=True)
    verification_status = models.CharField(
        max_length=10,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNVERIFIED,
    )
    verified_at = models.DateTimeField(blank=True, null=True)
    verified_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="verified_institutional_profiles",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]
        permissions = [
            ("view_verification_queue", "Can view the institutional verification queue"),
            ("verify_institutionalprofile", "Can decide institutional verification"),
            ("view_verificationhistory", "Can view institutional verification history"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(
                        verification_status="VERIFIED",
                        verified_at__isnull=False,
                        verified_by__isnull=False,
                    )
                    | (
                        ~models.Q(verification_status="VERIFIED")
                        & models.Q(verified_at__isnull=True, verified_by__isnull=True)
                    )
                ),
                name="accounts_profile_verified_audit_consistent",
            ),
        ]

    def save(self, *args, **kwargs):
        if self.institutional_email:
            self.institutional_email = self.institutional_email.strip().lower() or None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Institutional profile for {self.user_id}"


class VerificationEvent(models.Model):
    profile = models.ForeignKey(
        InstitutionalProfile,
        on_delete=models.PROTECT,
        related_name="verification_events",
    )
    from_status = models.CharField(
        max_length=10,
        choices=InstitutionalProfile.VerificationStatus.choices,
    )
    to_status = models.CharField(
        max_length=10,
        choices=InstitutionalProfile.VerificationStatus.choices,
    )
    actor = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="institutional_verification_events",
    )
    reason = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "pk"]

    def __str__(self):
        return f"{self.profile_id}: {self.from_status} -> {self.to_status}"
