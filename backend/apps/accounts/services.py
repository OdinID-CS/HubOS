from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from .models import InstitutionalProfile, VerificationEvent


PROFILE_FIELDS = frozenset(
    {"institutional_email", "institutional_id", "department", "designation"}
)


@transaction.atomic
def update_institutional_profile(
    profile: InstitutionalProfile,
    *,
    fields: dict,
    actor,
) -> InstitutionalProfile:
    if (
        not actor.is_authenticated
        or not actor.is_active
        or actor.pk != profile.user_id
    ):
        raise PermissionDenied("Only the profile owner can update this profile.")
    if not set(fields).issubset(PROFILE_FIELDS):
        raise ValidationError({"profile": "One or more profile fields cannot be changed."})

    locked_profile = InstitutionalProfile.objects.select_for_update().get(pk=profile.pk)
    changed_fields = {
        field for field, value in fields.items() if getattr(locked_profile, field) != value
    }
    for field, value in fields.items():
        setattr(locked_profile, field, value)

    verification_invalidated = (
        locked_profile.verification_status == InstitutionalProfile.VerificationStatus.VERIFIED
        and bool(changed_fields & PROFILE_FIELDS)
    )
    if verification_invalidated:
        locked_profile.verification_status = InstitutionalProfile.VerificationStatus.PENDING
        locked_profile.verified_at = None
        locked_profile.verified_by = None

    update_fields = [*fields]
    if verification_invalidated:
        update_fields.extend(["verification_status", "verified_at", "verified_by"])
    if update_fields:
        locked_profile.save(update_fields=[*update_fields, "updated_at"])

    if verification_invalidated:
        VerificationEvent.objects.create(
            profile=locked_profile,
            from_status=InstitutionalProfile.VerificationStatus.VERIFIED,
            to_status=InstitutionalProfile.VerificationStatus.PENDING,
            actor=actor,
            reason="Profile identity details changed; re-review required.",
        )
    return locked_profile


@transaction.atomic
def request_verification(profile: InstitutionalProfile, actor):
    if (
        not actor.is_authenticated
        or not actor.is_active
        or actor.pk != profile.user_id
    ):
        raise PermissionDenied("Only the profile owner can request verification.")

    locked_profile = InstitutionalProfile.objects.select_for_update().get(pk=profile.pk)
    if not locked_profile.institutional_email and not locked_profile.institutional_id:
        raise ValidationError(
            {
                "institutional_identity": (
                    "Provide an institutional email address or institutional ID before requesting review."
                )
            }
        )
    allowed = {
        InstitutionalProfile.VerificationStatus.UNVERIFIED,
        InstitutionalProfile.VerificationStatus.REJECTED,
    }
    if locked_profile.verification_status not in allowed:
        raise ValidationError({"verification_status": "This profile cannot be submitted in its current state."})

    previous_status = locked_profile.verification_status
    locked_profile.verification_status = InstitutionalProfile.VerificationStatus.PENDING
    locked_profile.save(update_fields=["verification_status", "updated_at"])
    return VerificationEvent.objects.create(
        profile=locked_profile,
        from_status=previous_status,
        to_status=locked_profile.verification_status,
        actor=actor,
    )


@transaction.atomic
def review_verification(
    profile_id,
    *,
    decision: str,
    actor,
    reason: str = "",
) -> VerificationEvent:
    if not actor.is_authenticated or not actor.is_active:
        raise PermissionDenied("Authentication is required.")
    if not actor.has_perm("accounts.verify_institutionalprofile"):
        raise PermissionDenied("You are not authorized to review institutional identities.")

    try:
        profile = InstitutionalProfile.objects.select_for_update().get(pk=profile_id)
    except InstitutionalProfile.DoesNotExist as exc:
        raise NotFound("Institutional profile not found.") from exc
    if actor.pk == profile.user_id:
        raise PermissionDenied("You cannot review your own institutional identity.")
    if decision not in {
        InstitutionalProfile.VerificationStatus.VERIFIED,
        InstitutionalProfile.VerificationStatus.REJECTED,
    }:
        raise ValidationError({"decision": "Decision must be VERIFIED or REJECTED."})
    if profile.verification_status != InstitutionalProfile.VerificationStatus.PENDING:
        raise ValidationError({"verification_status": "Only pending profiles can be reviewed."})

    previous_status = profile.verification_status
    profile.verification_status = decision
    if decision == InstitutionalProfile.VerificationStatus.VERIFIED:
        profile.verified_by = actor
        profile.verified_at = timezone.now()
    else:
        profile.verified_by = None
        profile.verified_at = None
    profile.save(
        update_fields=[
            "verification_status",
            "verified_by",
            "verified_at",
            "updated_at",
        ]
    )
    return VerificationEvent.objects.create(
        profile=profile,
        from_status=previous_status,
        to_status=decision,
        actor=actor,
        reason=reason,
    )
