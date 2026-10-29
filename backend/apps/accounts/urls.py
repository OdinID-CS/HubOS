from django.urls import path

from .views import (
    MyInstitutionalProfileView,
    VerificationDecisionView,
    VerificationHistoryView,
    VerificationQueueView,
    VerificationRequestView,
)

urlpatterns = [
    path("me/profile/", MyInstitutionalProfileView.as_view(), name="my-institutional-profile"),
    path(
        "me/profile/verification-request/",
        VerificationRequestView.as_view(),
        name="request-institutional-verification",
    ),
    path("verification-queue/", VerificationQueueView.as_view(), name="verification-queue"),
    path(
        "verification-history/<uuid:profile_id>/",
        VerificationHistoryView.as_view(),
        name="verification-history",
    ),
    path(
        "verification-decisions/",
        VerificationDecisionView.as_view(),
        name="verification-decision",
    ),
]
