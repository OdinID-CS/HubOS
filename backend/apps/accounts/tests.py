from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIClient

from .models import InstitutionalProfile, VerificationEvent
from .roles import ROLE_PERMISSIONS, has_hub_role
from .services import review_verification


User = get_user_model()


class InstitutionalIdentityTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            "owner@example.test",
            "Strong-password-123!",
            first_name="Owner",
            last_name="One",
        )
        self.other = User.objects.create_user(
            "other@example.test",
            "Strong-password-123!",
            first_name="Other",
            last_name="Two",
        )
        self.profile = self.owner.institutional_profile
        self.client = APIClient()

    def provision_hub_admin(self, user):
        call_command("setup_hub_roles", verbosity=0)
        user.groups.add(Group.objects.get(name="HUB_ADMIN"))
        user.refresh_from_db()
        return user

    def test_new_user_profile_is_unverified(self):
        self.assertEqual(
            self.profile.verification_status,
            InstitutionalProfile.VerificationStatus.UNVERIFIED,
        )
        self.assertIsNone(self.profile.verified_at)
        self.assertIsNone(self.profile.verified_by)

    def test_unauthenticated_user_cannot_access_profile(self):
        response = self.client.get("/api/accounts/me/profile/")
        self.assertEqual(response.status_code, 403)

    def test_owner_can_read_and_update_only_permitted_profile_fields(self):
        self.client.force_authenticate(self.owner)
        response = self.client.get("/api/accounts/me/profile/")
        self.assertEqual(response.status_code, 200)
        self.assertNotIn("verified_by", response.data)
        self.assertNotIn("user_email", response.data)

        response = self.client.patch(
            "/api/accounts/me/profile/",
            {"institutional_email": "  PERSON@EXAMPLE.EDU ", "department": "Science"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.institutional_email, "person@example.edu")
        self.assertEqual(self.profile.department, "Science")

    def test_profile_update_rejects_verification_and_role_fields(self):
        self.client.force_authenticate(self.owner)
        for data in (
            {"verification_status": "VERIFIED"},
            {"verified_by": str(self.other.pk)},
            {"role": "HUB_ADMIN"},
            {"groups": ["HUB_ADMIN"]},
        ):
            with self.subTest(data=data):
                response = self.client.patch(
                    "/api/accounts/me/profile/", data, format="json"
                )
                self.assertEqual(response.status_code, 400)
        self.profile.refresh_from_db()
        self.assertEqual(
            self.profile.verification_status,
            InstitutionalProfile.VerificationStatus.UNVERIFIED,
        )
        self.assertFalse(has_hub_role(self.owner, "HUB_ADMIN"))

    def test_owner_can_request_review_but_cannot_resubmit_pending_profile(self):
        self.profile.institutional_id = "ID-100"
        self.profile.save(update_fields=["institutional_id", "updated_at"])
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            "/api/accounts/me/profile/verification-request/", {}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["verification_status"], "PENDING")
        event = VerificationEvent.objects.get(profile=self.profile)
        self.assertEqual(event.actor, self.owner)
        self.assertEqual(event.from_status, "UNVERIFIED")
        self.assertEqual(event.to_status, "PENDING")

        response = self.client.post(
            "/api/accounts/me/profile/verification-request/", {}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(VerificationEvent.objects.filter(profile=self.profile).count(), 1)

    def test_owner_cannot_request_review_without_an_institutional_identifier(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            "/api/accounts/me/profile/verification-request/", {}, format="json"
        )
        self.assertEqual(response.status_code, 400)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.verification_status, "UNVERIFIED")
        self.assertFalse(VerificationEvent.objects.filter(profile=self.profile).exists())

    def test_ordinary_user_cannot_verify_self_or_another_user(self):
        self.client.force_authenticate(self.owner)
        response = self.client.post(
            "/api/accounts/verification-decisions/",
            {"profile_id": str(self.profile.pk), "decision": "VERIFIED"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

        response = self.client.post(
            "/api/accounts/verification-decisions/",
            {"profile_id": str(self.other.institutional_profile.pk), "decision": "VERIFIED"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.verification_status, "UNVERIFIED")

    def test_authorized_verification_records_reviewer_timestamp_and_event(self):
        self.profile.institutional_id = "ID-100"
        self.profile.save(update_fields=["institutional_id", "updated_at"])
        self.client.force_authenticate(self.owner)
        self.client.post(
            "/api/accounts/me/profile/verification-request/", {}, format="json"
        )
        reviewer = self.provision_hub_admin(self.other)
        self.client.force_authenticate(reviewer)

        response = self.client.post(
            "/api/accounts/verification-decisions/",
            {
                "profile_id": str(self.profile.pk),
                "decision": "VERIFIED",
                "reason": "Identity reviewed in person",
            },
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.verification_status, "VERIFIED")
        self.assertEqual(self.profile.verified_by, reviewer)
        self.assertIsNotNone(self.profile.verified_at)
        self.assertEqual(response.data["actor_id"], str(reviewer.pk))
        event = VerificationEvent.objects.get(
            profile=self.profile, to_status="VERIFIED"
        )
        self.assertEqual(event.actor, reviewer)
        self.assertEqual(event.reason, "Identity reviewed in person")
        self.assertIsNotNone(response.data["created_at"])

    def test_editing_verified_identity_returns_profile_to_pending_with_audit(self):
        self.profile.institutional_id = "ID-100"
        self.profile.verification_status = "VERIFIED"
        reviewer = self.provision_hub_admin(self.other)
        self.profile.verified_by = reviewer
        self.profile.verified_at = timezone.now()
        self.profile.save()

        self.client.force_authenticate(self.owner)
        response = self.client.patch(
            "/api/accounts/me/profile/",
            {"institutional_id": "ID-101"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.institutional_id, "ID-101")
        self.assertEqual(self.profile.verification_status, "PENDING")
        self.assertIsNone(self.profile.verified_at)
        self.assertIsNone(self.profile.verified_by)
        event = VerificationEvent.objects.get(profile=self.profile)
        self.assertEqual(event.from_status, "VERIFIED")
        self.assertEqual(event.to_status, "PENDING")
        self.assertEqual(event.actor, self.owner)

    def test_hub_admin_cannot_review_their_own_profile(self):
        admin = self.provision_hub_admin(self.owner)
        self.profile.institutional_id = "ID-100"
        self.profile.save(update_fields=["institutional_id", "updated_at"])
        self.client.force_authenticate(admin)
        self.client.post(
            "/api/accounts/me/profile/verification-request/", {}, format="json"
        )
        response = self.client.post(
            "/api/accounts/verification-decisions/",
            {"profile_id": str(self.profile.pk), "decision": "VERIFIED"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)

    def test_invalid_transitions_are_rejected(self):
        reviewer = self.provision_hub_admin(self.other)
        with self.assertRaises(ValidationError) as context:
            review_verification(
                self.profile.pk,
                decision="VERIFIED",
                actor=reviewer,
            )
        self.assertIn("Only pending profiles", str(context.exception))
        self.assertEqual(VerificationEvent.objects.filter(profile=self.profile).count(), 0)

    def test_verification_queue_is_restricted_to_hub_admin(self):
        self.profile.institutional_id = "ID-100"
        self.profile.save(update_fields=["institutional_id", "updated_at"])
        self.client.force_authenticate(self.owner)
        self.assertEqual(
            self.client.get("/api/accounts/verification-queue/").status_code, 403
        )
        self.client.post(
            "/api/accounts/me/profile/verification-request/", {}, format="json"
        )
        reviewer = self.provision_hub_admin(self.other)
        self.client.force_authenticate(reviewer)
        response = self.client.get("/api/accounts/verification-queue/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["user_email"], self.owner.email)
        self.assertEqual(response.data[0]["institutional_id"], "ID-100")

    def test_only_hub_admin_can_read_verification_history(self):
        self.profile.institutional_id = "ID-100"
        self.profile.save(update_fields=["institutional_id", "updated_at"])
        self.client.force_authenticate(self.owner)
        self.client.post(
            "/api/accounts/me/profile/verification-request/", {}, format="json"
        )
        history_url = f"/api/accounts/verification-history/{self.profile.pk}/"
        self.assertEqual(self.client.get(history_url).status_code, 403)

        reviewer = self.provision_hub_admin(self.other)
        self.client.force_authenticate(reviewer)
        response = self.client.get(history_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

    def test_session_authentication_requires_csrf_for_unsafe_requests(self):
        client = APIClient(enforce_csrf_checks=True)
        self.assertTrue(client.login(email=self.owner.email, password="Strong-password-123!"))
        response = client.patch(
            "/api/accounts/me/profile/",
            {"department": "Science"},
            format="json",
        )
        self.assertEqual(response.status_code, 403)


class HubRoleTests(TestCase):
    def test_role_setup_is_repeatable_and_synchronizes_permissions(self):
        call_command("setup_hub_roles", verbosity=0)
        call_command("setup_hub_roles", verbosity=0)
        self.assertEqual(Group.objects.count(), len(ROLE_PERMISSIONS))

        for role, codenames in ROLE_PERMISSIONS.items():
            with self.subTest(role=role):
                group = Group.objects.get(name=role)
                self.assertSetEqual(
                    set(group.permissions.values_list("codename", flat=True)),
                    set(codenames),
                )

        hub_admin = Group.objects.get(name="HUB_ADMIN")
        profile_permission = Permission.objects.get(
            content_type__app_label="accounts",
            codename="verify_institutionalprofile",
        )
        hub_admin.permissions.remove(profile_permission)
        call_command("setup_hub_roles", verbosity=0)
        self.assertTrue(hub_admin.permissions.filter(pk=profile_permission.pk).exists())

    def test_superuser_privilege_is_not_a_hub_role(self):
        superuser = User.objects.create_superuser(
            "root@example.test",
            "Strong-password-123!",
            first_name="Root",
            last_name="Admin",
        )
        self.assertFalse(has_hub_role(superuser, "HUB_ADMIN"))
        self.assertTrue(superuser.is_superuser)

    def test_existing_email_authentication_remains_case_insensitive(self):
        User.objects.create_user(
            "login@example.test",
            "Strong-password-123!",
            first_name="Login",
            last_name="User",
        )
        user = authenticate(
            username="LOGIN@EXAMPLE.TEST",
            password="Strong-password-123!",
        )
        self.assertIsNotNone(user)
        self.assertEqual(user.email, "login@example.test")
