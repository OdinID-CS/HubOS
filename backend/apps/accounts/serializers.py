from collections.abc import Mapping

from rest_framework import serializers

from .models import InstitutionalProfile, VerificationEvent


class StrictInputMixin:
    def to_internal_value(self, data):
        if not isinstance(data, Mapping):
            return super().to_internal_value(data)
        unknown_fields = set(data) - set(self.fields)
        if unknown_fields:
            raise serializers.ValidationError(
                {field: "This field is not permitted." for field in sorted(unknown_fields)}
            )
        read_only_fields = {
            field_name for field_name, field in self.fields.items() if field.read_only
        }
        attempted_read_only_fields = set(data) & read_only_fields
        if attempted_read_only_fields:
            raise serializers.ValidationError(
                {
                    field: "This field cannot be changed."
                    for field in sorted(attempted_read_only_fields)
                }
            )
        return super().to_internal_value(data)


class OwnInstitutionalProfileSerializer(StrictInputMixin, serializers.ModelSerializer):
    class Meta:
        model = InstitutionalProfile
        fields = (
            "id",
            "institutional_email",
            "institutional_id",
            "department",
            "designation",
            "verification_status",
            "verified_at",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "id",
            "verification_status",
            "verified_at",
            "created_at",
            "updated_at",
        )

    def validate_institutional_email(self, value):
        if value is None:
            return None
        return value.strip().lower() or None


class VerificationRequestSerializer(StrictInputMixin, serializers.Serializer):
    pass


class VerificationDecisionSerializer(StrictInputMixin, serializers.Serializer):
    profile_id = serializers.UUIDField()
    decision = serializers.ChoiceField(
        choices=(
            InstitutionalProfile.VerificationStatus.VERIFIED,
            InstitutionalProfile.VerificationStatus.REJECTED,
        )
    )
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)


class VerificationQueueProfileSerializer(serializers.ModelSerializer):
    user_id = serializers.UUIDField(read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    user_first_name = serializers.CharField(source="user.first_name", read_only=True)
    user_last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = InstitutionalProfile
        fields = (
            "id",
            "user_id",
            "user_email",
            "user_first_name",
            "user_last_name",
            "institutional_email",
            "institutional_id",
            "department",
            "designation",
            "verification_status",
            "created_at",
        )


class VerificationDecisionResultSerializer(serializers.Serializer):
    profile_id = serializers.UUIDField(read_only=True)
    from_status = serializers.CharField(read_only=True)
    to_status = serializers.CharField(read_only=True)
    actor_id = serializers.UUIDField(read_only=True)
    reason = serializers.CharField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)


class VerificationEventSerializer(serializers.ModelSerializer):
    actor_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = VerificationEvent
        fields = ("from_status", "to_status", "actor_id", "reason", "created_at")
