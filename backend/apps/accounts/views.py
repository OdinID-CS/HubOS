from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import InstitutionalProfile
from .permissions import (
    CanReviewInstitutionalIdentity,
    CanViewVerificationHistory,
    CanViewVerificationQueue,
)
from .serializers import (
    OwnInstitutionalProfileSerializer,
    VerificationDecisionResultSerializer,
    VerificationDecisionSerializer,
    VerificationEventSerializer,
    VerificationQueueProfileSerializer,
    VerificationRequestSerializer,
)
from .services import (
    request_verification,
    review_verification,
    update_institutional_profile,
)


class MyInstitutionalProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, request):
        return get_object_or_404(InstitutionalProfile, user=request.user)

    def get(self, request):
        serializer = OwnInstitutionalProfileSerializer(self.get_object(request))
        return Response(serializer.data)

    def patch(self, request):
        profile = self.get_object(request)
        serializer = OwnInstitutionalProfileSerializer(
            profile,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        updated_profile = update_institutional_profile(
            profile,
            fields=serializer.validated_data,
            actor=request.user,
        )
        return Response(OwnInstitutionalProfileSerializer(updated_profile).data)


class VerificationRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = VerificationRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = get_object_or_404(InstitutionalProfile, user=request.user)
        event = request_verification(profile, request.user)
        return Response(
            OwnInstitutionalProfileSerializer(event.profile).data,
            status=status.HTTP_200_OK,
        )


class VerificationQueueView(APIView):
    permission_classes = [IsAuthenticated, CanViewVerificationQueue]

    def get(self, request):
        profiles = (
            InstitutionalProfile.objects.filter(
                verification_status=InstitutionalProfile.VerificationStatus.PENDING
            )
            .select_related("user")
            .order_by("created_at")
        )
        return Response(VerificationQueueProfileSerializer(profiles, many=True).data)


class VerificationDecisionView(APIView):
    permission_classes = [IsAuthenticated, CanReviewInstitutionalIdentity]

    def post(self, request):
        serializer = VerificationDecisionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = review_verification(
            serializer.validated_data["profile_id"],
            decision=serializer.validated_data["decision"],
            actor=request.user,
            reason=serializer.validated_data.get("reason", ""),
        )
        return Response(
            VerificationDecisionResultSerializer(event).data,
            status=status.HTTP_200_OK,
        )


class VerificationHistoryView(APIView):
    permission_classes = [IsAuthenticated, CanViewVerificationHistory]

    def get(self, request, profile_id):
        profile = get_object_or_404(InstitutionalProfile, pk=profile_id)
        events = profile.verification_events.select_related("actor").all()
        return Response(VerificationEventSerializer(events, many=True).data)
