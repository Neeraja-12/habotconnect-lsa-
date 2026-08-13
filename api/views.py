from django.db.models import Q
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

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
    UserRole,
)
from .serializers import (
    AvailabilitySerializer,
    BookingDetailSerializer,
    BookingListSerializer,
    BookingStatusUpdateSerializer,
    BookingWriteSerializer,
    ChildProfileSerializer,
    LSAProfileDetailSerializer,
    LSAProfileListSerializer,
    LSAProfileWriteSerializer,
    ProfileSerializer,
    ReviewSerializer,
    ReviewWriteSerializer,
    SpecializationSerializer,
    UserCreateSerializer,
    UserListSerializer,
)


class UserViewSet(viewsets.ModelViewSet):
    """Register and list platform users."""

    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        return UserListSerializer

    def get_queryset(self):
        return User.objects.select_related("profile")


class ProfileViewSet(viewsets.ModelViewSet):
    """Read/update a user's shared profile."""

    serializer_class = ProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Profile.objects.select_related("user").filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SpecializationViewSet(viewsets.ReadOnlyModelViewSet):
    """Reference data for LSA specializations."""

    queryset = Specialization.objects.all()
    serializer_class = SpecializationSerializer


class LSAProfileViewSet(viewsets.ModelViewSet):
    """Search and manage Learning Support Assistant profiles."""

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["headline", "qualifications", "user__first_name", "user__last_name"]
    ordering_fields = ["hourly_rate", "average_rating", "years_of_experience", "created_at"]
    ordering = ["-is_verified", "-average_rating"]

    def get_queryset(self):
        qs = (
            LSAProfile.objects.filter(is_available=True)
            .select_related("user")
            .prefetch_related("specializations")
        )

        specialization = self.request.query_params.get("specialization")
        if specialization:
            qs = qs.filter(specializations__name__iexact=specialization)

        max_rate = self.request.query_params.get("max_rate")
        if max_rate:
            try:
                qs = qs.filter(hourly_rate__lte=float(max_rate))
            except ValueError:
                raise ValidationError({"max_rate": "Must be a number."})

        verified = self.request.query_params.get("verified")
        if verified is not None:
            qs = qs.filter(is_verified=verified.lower() in ("true", "1", "yes"))

        min_rating = self.request.query_params.get("min_rating")
        if min_rating:
            try:
                qs = qs.filter(average_rating__gte=float(min_rating))
            except ValueError:
                raise ValidationError({"min_rating": "Must be a number."})

        return qs

    def get_serializer_class(self):
        if self.action in ["retrieve", "me"]:
            return LSAProfileDetailSerializer
        if self.action in ["create", "update", "partial_update"]:
            return LSAProfileWriteSerializer
        return LSAProfileListSerializer

    def perform_create(self, serializer):
        if self.request.user.role != UserRole.LSA:
            raise PermissionDenied("Only LSA users can create an LSA profile.")
        serializer.save(user=self.request.user)

    @action(detail=False, methods=["get", "put", "patch"], permission_classes=[IsAuthenticated])
    def me(self, request):
        """Current LSA's own profile."""
        try:
            profile = LSAProfile.objects.select_related("user", "user__profile").prefetch_related(
                "specializations"
            ).get(user=request.user)
        except LSAProfile.DoesNotExist:
            return Response({"detail": "LSA profile not found."}, status=status.HTTP_404_NOT_FOUND)

        if request.method in ("PUT", "PATCH"):
            serializer = LSAProfileWriteSerializer(
                profile,
                data=request.data,
                partial=request.method == "PATCH",
                context={"request": request},
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()

        serializer = LSAProfileDetailSerializer(profile, context={"request": request})
        return Response(serializer.data)


class ChildProfileViewSet(viewsets.ModelViewSet):
    """Parents manage their children's profiles."""

    serializer_class = ChildProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChildProfile.objects.filter(parent=self.request.user)

    def perform_create(self, serializer):
        if self.request.user.role != UserRole.PARENT:
            raise PermissionDenied("Only parents can add child profiles.")
        serializer.save(parent=self.request.user)


class AvailabilityViewSet(viewsets.ModelViewSet):
    """LSAs post availability; parents search open slots."""

    serializer_class = AvailabilitySerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated()]
        return super().get_permissions()

    def get_queryset(self):
        qs = Availability.objects.select_related("lsa").filter(is_booked=False)

        lsa_id = self.request.query_params.get("lsa")
        if lsa_id:
            qs = qs.filter(lsa_id=lsa_id)

        day = self.request.query_params.get("day")
        if day:
            try:
                qs = qs.filter(day_of_week=int(day))
            except ValueError:
                raise ValidationError({"day": "Must be an integer 0-6."})

        date = self.request.query_params.get("date")
        if date:
            qs = qs.filter(Q(specific_date=date) | Q(is_recurring=True))

        return qs

    def perform_create(self, serializer):
        if self.request.user.role != UserRole.LSA:
            raise PermissionDenied("Only LSAs can post availability.")
        serializer.save(lsa=self.request.user)


class BookingViewSet(viewsets.ModelViewSet):
    """Parents request bookings; LSAs confirm/decline/cancel."""

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        base_qs = Booking.objects.select_related(
            "parent", "lsa", "child"
        ).prefetch_related("review")

        if user.role == UserRole.PARENT:
            return base_qs.filter(parent=user)
        if user.role == UserRole.LSA:
            return base_qs.filter(lsa=user)
        return base_qs

    def get_serializer_class(self):
        if self.action == "create":
            return BookingWriteSerializer
        if self.action == "retrieve":
            return BookingDetailSerializer
        if self.action == "update_status":
            return BookingStatusUpdateSerializer
        return BookingListSerializer

    def perform_create(self, serializer):
        if self.request.user.role != UserRole.PARENT:
            raise PermissionDenied("Only parents can create bookings.")

        lsa = serializer.validated_data["lsa"]
        if lsa.role != UserRole.LSA:
            raise ValidationError({"lsa": "Selected user is not an LSA."})

        serializer.save(parent=self.request.user)

    @action(detail=True, methods=["patch"])
    def update_status(self, request, pk=None):
        booking = self.get_object()
        serializer = BookingStatusUpdateSerializer(
            booking, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data.get("status")
        user = request.user

        if user.role == UserRole.LSA and booking.lsa != user:
            raise PermissionDenied("You can only update your own bookings.")
        if user.role == UserRole.PARENT and booking.parent != user:
            raise PermissionDenied("You can only update your own bookings.")

        if new_status == BookingStatus.CONFIRMED and user.role != UserRole.LSA:
            raise PermissionDenied("Only the assigned LSA can confirm a booking.")

        serializer.save()

        if new_status == BookingStatus.COMPLETED:
            booking.status = BookingStatus.COMPLETED
            booking.save(update_fields=["status", "updated_at"])

        return Response(BookingDetailSerializer(booking).data)

    @action(detail=True, methods=["patch"])
    def complete(self, request, pk=None):
        """Mark a confirmed booking as completed."""
        booking = self.get_object()
        if booking.parent != request.user:
            raise PermissionDenied("Only the parent can mark a booking as completed.")
        if booking.status != BookingStatus.CONFIRMED:
            raise ValidationError({"status": "Only confirmed bookings can be completed."})

        booking.status = BookingStatus.COMPLETED
        booking.save(update_fields=["status", "updated_at"])
        return Response(BookingDetailSerializer(booking).data)


class ReviewViewSet(viewsets.ModelViewSet):
    """Parents review completed bookings; LSAs read their reviews."""

    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return ReviewWriteSerializer
        return ReviewSerializer

    def get_queryset(self):
        user = self.request.user
        qs = Review.objects.select_related(
            "booking__parent", "booking__lsa"
        )

        if user.role == UserRole.LSA:
            return qs.filter(booking__lsa=user)
        if user.role == UserRole.PARENT:
            return qs.filter(booking__parent=user)
        return qs.none()

    def perform_create(self, serializer):
        serializer.save()
        