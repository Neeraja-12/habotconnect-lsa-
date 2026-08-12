"""
DRF serializers for HabotConnect.

Serializers are kept flat and focused to avoid N+1 issues; viewsets are
responsible for selecting and prefetching related data.
"""

from django.db import transaction
from rest_framework import serializers

from .models import (
    Availability,
    Booking,
    BookingStatus,
    ChildProfile,
    LSAProfile,
    Profile,
    Review,
    Specialization,
    User,
)


class UserListSerializer(serializers.ModelSerializer):
    """Compact user representation for list endpoints."""

    full_name = serializers.CharField(source="get_full_name", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "full_name",
            "role",
            "is_email_verified",
            "created_at",
        ]


class UserCreateSerializer(serializers.ModelSerializer):
    """Used when registering a new parent or LSA."""

    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "email",
            "first_name",
            "last_name",
            "role",
            "password",
        ]

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)

    class Meta:
        model = Profile
        fields = [
            "id",
            "email",
            "full_name",
            "phone_number",
            "address_line_1",
            "address_line_2",
            "city",
            "postcode",
            "county",
            "country",
            "bio",
            "profile_picture_url",
            "emergency_contact_name",
            "emergency_contact_phone",
        ]


class SpecializationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specialization
        fields = ["id", "name", "description"]


class LSAProfileListSerializer(serializers.ModelSerializer):
    """Lightweight LSA card used in search/matching results."""

    lsa_id = serializers.IntegerField(source="user_id", read_only=True)
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    specializations = SpecializationSerializer(many=True, read_only=True)

    class Meta:
        model = LSAProfile
        fields = [
            "lsa_id",
            "full_name",
            "headline",
            "years_of_experience",
            "hourly_rate",
            "specializations",
            "crb_dbs_checked",
            "first_aid_trained",
            "safeguarding_trained",
            "is_verified",
            "is_available",
            "max_travel_distance_km",
            "average_rating",
            "review_count",
        ]


class LSAProfileDetailSerializer(serializers.ModelSerializer):
    """Full LSA profile with nested user profile data."""

    email = serializers.EmailField(source="user.email", read_only=True)
    full_name = serializers.CharField(source="user.get_full_name", read_only=True)
    profile = ProfileSerializer(source="user.profile", read_only=True)
    specializations = SpecializationSerializer(many=True, read_only=True)

    class Meta:
        model = LSAProfile
        fields = [
            "id",
            "email",
            "full_name",
            "profile",
            "headline",
            "years_of_experience",
            "hourly_rate",
            "qualifications",
            "specializations",
            "crb_dbs_checked",
            "first_aid_trained",
            "safeguarding_trained",
            "is_verified",
            "is_available",
            "max_travel_distance_km",
            "average_rating",
            "review_count",
            "created_at",
            "updated_at",
        ]


class LSAProfileWriteSerializer(serializers.ModelSerializer):
    """Writable LSA profile used for onboarding/updates."""

    specializations = serializers.PrimaryKeyRelatedField(
        queryset=Specialization.objects.all(),
        many=True,
        required=False,
    )

    class Meta:
        model = LSAProfile
        fields = [
            "headline",
            "years_of_experience",
            "hourly_rate",
            "qualifications",
            "specializations",
            "crb_dbs_checked",
            "first_aid_trained",
            "safeguarding_trained",
            "is_available",
            "max_travel_distance_km",
        ]


class ChildProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChildProfile
        fields = [
            "id",
            "first_name",
            "last_name",
            "date_of_birth",
            "diagnoses",
            "supportNeeds",
            "interests",
            "school_name",
            "year_group",
            "created_at",
        ]
        read_only_fields = ["parent"]


class AvailabilitySerializer(serializers.ModelSerializer):
    lsa_name = serializers.CharField(source="lsa.get_full_name", read_only=True)

    class Meta:
        model = Availability
        fields = [
            "id",
            "lsa",
            "lsa_name",
            "day_of_week",
            "specific_date",
            "start_time",
            "end_time",
            "is_recurring",
            "is_booked",
            "created_at",
        ]
        read_only_fields = ["lsa", "is_booked"]


class BookingListSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(source="parent.get_full_name", read_only=True)
    lsa_name = serializers.CharField(source="lsa.get_full_name", read_only=True)
    child_name = serializers.CharField(source="child", read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "parent",
            "parent_name",
            "lsa",
            "lsa_name",
            "child",
            "child_name",
            "status",
            "starts_at",
            "ends_at",
            "hourly_rate",
            "total_hours",
            "created_at",
        ]


class BookingDetailSerializer(serializers.ModelSerializer):
    parent = UserListSerializer(read_only=True)
    lsa = UserListSerializer(read_only=True)
    child = ChildProfileSerializer(read_only=True)

    class Meta:
        model = Booking
        fields = [
            "id",
            "parent",
            "lsa",
            "child",
            "status",
            "starts_at",
            "ends_at",
            "hourly_rate",
            "total_hours",
            "notes",
            "cancellation_reason",
            "created_at",
            "updated_at",
        ]


class BookingWriteSerializer(serializers.ModelSerializer):
    """Writable booking serializer with lightweight validation."""

    class Meta:
        model = Booking
        fields = [
            "lsa",
            "child",
            "starts_at",
            "ends_at",
            "hourly_rate",
            "total_hours",
            "notes",
        ]

    def validate(self, data):
        if data["ends_at"] <= data["starts_at"]:
            raise serializers.ValidationError(
                {"ends_at": "End time must be after start time."}
            )
        return data


class BookingStatusUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ["status", "cancellation_reason"]

    def validate_status(self, value):
        allowed = {BookingStatus.CONFIRMED, BookingStatus.CANCELLED, BookingStatus.DECLINED}
        if value not in allowed:
            raise serializers.ValidationError(
                f"Status can only be updated to one of: {', '.join(allowed)}"
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    parent_name = serializers.CharField(
        source="booking.parent.get_full_name", read_only=True
    )
    lsa_name = serializers.CharField(
        source="booking.lsa.get_full_name", read_only=True
    )

    class Meta:
        model = Review
        fields = [
            "id",
            "booking",
            "parent_name",
            "lsa_name",
            "rating",
            "comment",
            "would_recommend",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["booking"]


class ReviewWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ["booking", "rating", "comment", "would_recommend"]

    def validate_booking(self, booking):
        user = self.context["request"].user
        if booking.parent_id != user.id:
            raise serializers.ValidationError(
                "You can only review bookings you created."
            )
        if booking.status != BookingStatus.COMPLETED:
            raise serializers.ValidationError(
                "Reviews are only allowed for completed bookings."
            )
        if Review.objects.filter(booking=booking).exists():
            raise serializers.ValidationError(
                "A review already exists for this booking."
            )
        return booking

    @transaction.atomic
    def create(self, validated_data):
        review = super().create(validated_data)
        review.booking.lsa.lsa_profile.update_rating()
        return review
