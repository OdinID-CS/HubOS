from rest_framework.permissions import BasePermission


class CanReviewInstitutionalIdentity(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("accounts.verify_institutionalprofile")


class CanViewVerificationQueue(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("accounts.view_verification_queue")


class CanViewVerificationHistory(BasePermission):
    def has_permission(self, request, view):
        return request.user.has_perm("accounts.view_verificationhistory")
