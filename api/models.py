"""
HabotConnect domain models.

Designed to keep parent and LSA data normalized while allowing efficient
querying for matching, scheduling, and reviews.
"""

from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models import Avg, Count


class UserRole(models.TextChoices):
    PARENT = "parent", "Parent"
    LSA = "lsa", "Learning Support Assistant"
    ADMIN = "admin", "Admin"


class User(AbstractUser):
    """Platform user with a single role."""

    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.PARENT,
    )
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username", "first_name", "last_name"]

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.get_full_name() or self.email} ({self.role})"


class Profile(models.Model):
    """Shared profile data for every user."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    phone_number = models.CharField(max_length=30, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postcode = models.CharField(max_length=20, blank=True)
    county = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default="United Kingdom")
    bio = models.TextField(blank=True)
    profile_picture_url = models.URLField(blank=True)
    emergency_contact_name = models.CharField(max_length=150, blank=True)
    emergency_contact_phone = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["user__last_name", "user__first_name"]

    def __str__(self) -> str:
        return f"Profile for {self.user}"


class Specialization(models.Model):
    """Discrete learning difficulty / support area an LSA can specialize in."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class LSAProfile(models.Model):
    """Extended profile for Learning Support Assistants."""

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="lsa_profile",
        limit_choices_to={"role": UserRole.LSA},
    )
    headline = models.CharField(max_length=150, blank=True)
    years_of_experience = models.PositiveSmallIntegerField(default=0)
    hourly_rate = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    qualifications = models.TextField(blank=True)
    specializations = models.ManyToManyField(
        Specialization,
        related_name="lsa_profiles",
        blank=True,
    )
    crb_dbs_checked = models.BooleanField(default=False)
    first_aid_trained = models.BooleanField(default=False)
    safeguarding_trained = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    max_travel_distance_km = models.PositiveSmallIntegerField(default=10)
    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    review_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-average_rating", "-review_count", "user__last_name"]
        indexes = [
            models.Index(fields=["is_verified", "is_available", "hourly_rate"]),
            models.Index(fields=["average_rating"]),
            models.Index(fields=["max_travel_distance_km"]),
        ]

    def update_rating(self):
        """Recompute average rating and review count from related reviews."""
        aggregate = Review.objects.filter(
            booking__lsa=self.user
        ).aggregate(
            avg=Avg("rating"),
            count=Count("id"),
        )
        self.average_rating = aggregate["avg"] or 0.00
        self.review_count = aggregate["count"] or 0
        self.save(update_fields=["average_rating", "review_count", "updated_at"])

    def __str__(self) -> str:
        return f"LSA profile for {self.user.get_full_name() or self.user.email}"


class ChildProfile(models.Model):
    """A child looked after by a parent user."""

    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="children",
        limit_choices_to={"role": UserRole.PARENT},
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    diagnoses = models.TextField(
        blank=True,
        help_text="e.g. dyslexia, ADHD, autism, dyscalculia",
    )
    supportNeeds = models.TextField(
        blank=True,
        help_text="Specific support needs the LSA should be aware of",
    )
    interests = models.TextField(blank=True)
    school_name = models.CharField(max_length=255, blank=True)
    year_group = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["first_name", "last_name"]

    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}".strip()


class BookingStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    CONFIRMED = "confirmed", "Confirmed"
    CANCELLED = "cancelled", "Cancelled"
    COMPLETED = "completed", "Completed"
    DECLINED = "declined", "Declined"


class Booking(models.Model):
    """A session request/booking between a parent and an LSA."""

    parent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="parent_bookings",
        limit_choices_to={"role": UserRole.PARENT},
    )
    lsa = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="lsa_bookings",
        limit_choices_to={"role": UserRole.LSA},
    )
    child = models.ForeignKey(
        ChildProfile,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )
    status = models.CharField(
        max_length=20,
        choices=BookingStatus.choices,
        default=BookingStatus.PENDING,
    )
    starts_at = models.DateTimeField()
    ends_at = models.DateTimeField()
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    total_hours = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(0.5)],
    )
    notes = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-starts_at"]
        indexes = [
            models.Index(fields=["parent", "status", "starts_at"]),
            models.Index(fields=["lsa", "status", "starts_at"]),
        ]

    def __str__(self) -> str:
        return f"Booking {self.id}: {self.parent} ↔ {self.lsa} on {self.starts_at.date()}"


class Availability(models.Model):
    """Recurring or one-off availability slot posted by an LSA."""

    class DayOfWeek(models.IntegerChoices):
        MONDAY = 0, "Monday"
        TUESDAY = 1, "Tuesday"
        WEDNESDAY = 2, "Wednesday"
        THURSDAY = 3, "Thursday"
        FRIDAY = 4, "Friday"
        SATURDAY = 5, "Saturday"
        SUNDAY = 6, "Sunday"

    lsa = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="availability",
        limit_choices_to={"role": UserRole.LSA},
    )
    day_of_week = models.IntegerField(
        choices=DayOfWeek.choices,
        null=True,
        blank=True,
    )
    specific_date = models.DateField(
        null=True,
        blank=True,
        help_text="Overrides day_of_week when set",
    )
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_recurring = models.BooleanField(default=True)
    is_booked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Availability"
        ordering = ["day_of_week", "start_time"]
        indexes = [
            models.Index(fields=["lsa", "day_of_week", "is_booked"]),
            models.Index(fields=["specific_date", "is_booked"]),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(start_time__lt=models.F("end_time")),
                name="availability_start_before_end",
            ),
        ]

    def __str__(self) -> str:
        label = self.specific_date.isoformat() if self.specific_date else self.get_day_of_week_display()
        return f"{self.lsa} available {label} {self.start_time}-{self.end_time}"


class Review(models.Model):
    """Parent review of an LSA after a completed booking."""

    booking = models.OneToOneField(
        Booking,
        on_delete=models.CASCADE,
        related_name="review",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    comment = models.TextField(blank=True)
    would_recommend = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["rating", "created_at"]),
        ]

    def __str__(self) -> str:
        return f"Review {self.rating}★ for booking {self.booking_id}"
