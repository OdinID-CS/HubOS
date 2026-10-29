"""Stable HubOS group names and the permissions provisioned for each role."""

ROLE_PERMISSIONS = {
    "MEMBER": (),
    "PROJECT_LEAD": (),
    "REVIEWER": (),
    "ASSET_MANAGER": (),
    "HUB_ADMIN": (
        "view_verification_queue",
        "verify_institutionalprofile",
        "view_verificationhistory",
    ),
    "EXECUTIVE": (),
}


def has_hub_role(user, role: str) -> bool:
    """Check explicit HubOS group membership without treating superusers as a role."""
    if role not in ROLE_PERMISSIONS or not getattr(user, "is_authenticated", False):
        return False
    return user.groups.filter(name=role).exists()
