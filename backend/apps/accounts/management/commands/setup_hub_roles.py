from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.accounts.models import InstitutionalProfile
from apps.accounts.roles import ROLE_PERMISSIONS


class Command(BaseCommand):
    help = "Create or synchronize the documented HubOS role groups."

    @transaction.atomic
    def handle(self, *args, **options):
        permissions = {
            permission.codename: permission
            for permission in Permission.objects.filter(
                content_type__app_label="accounts",
                content_type__model=InstitutionalProfile._meta.model_name,
            )
        }

        for role, codenames in ROLE_PERMISSIONS.items():
            missing = set(codenames) - permissions.keys()
            if missing:
                raise CommandError(
                    f"Missing profile permissions for {role}: {', '.join(sorted(missing))}. "
                    "Run migrations before provisioning roles."
                )
                return

            group, created = Group.objects.get_or_create(name=role)
            group.permissions.set(permissions[codename] for codename in codenames)
            action = "Created" if created else "Synchronized"
            self.stdout.write(f"{action} {role}")
