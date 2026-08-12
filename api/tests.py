"""
API tests for HabotConnect.

Run with: python manage.py test
"""

from datetime import datetime, time

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import (
    Availability,
    Booking,
    BookingStatus,
    LSAProfile,
    Review,
    User,
    UserRole,
)


def make_parent():
    return User.objects.create_user(
        username="parent",
        email="parent@example.com",
        password="securepass123",
        first_name="Jane",
        last_name="Doe",
        role=UserRole.PARENT,
    )


def make_lsa():
    user = User.objects.create_user(
        username="lsa",
        email="lsa@example.com",
        password="securepass123",
        first_name="John",
        last_name="Smith",
        role=UserRole.LSA,
    )
    LSAProfile.objects.create(
        user=user,
        headline="SEN support specialist",
        hourly_rate=30.00,
    )
    return user


class UserModelTests(TestCase):
    def test_create_parent_user(self):
        user = make_parent()
        self.assertEqual(user.role, UserRole.PARENT)
        self.assertEqual(user.get_full_name(), "Jane Doe")

    def test_create_lsa_user(self):
        user = make_lsa()
        self.assertEqual(user.role, UserRole.LSA)


class LSAProfileTests(TestCase):
    def test_update_rating(self):
        lsa = make_lsa()
        parent = make_parent()
        for i, rating in enumerate([4, 5], start=1):
            booking = Booking.objects.create(
                parent=parent,
                lsa=lsa,
                starts_at=datetime(2026, 8, i, 10, 0),
                ends_at=datetime(2026, 8, i, 11, 0),
                hourly_rate=25.00,
                total_hours=1.0,
                status=BookingStatus.COMPLETED,
            )
            Review.objects.create(booking=booking, rating=rating)

        lsa.lsa_profile.update_rating()
        self.assertEqual(lsa.lsa_profile.review_count, 2)
        self.assertEqual(float(lsa.lsa_profile.average_rating), 4.5)


class BookingAPITests(APITestCase):
    def setUp(self):
        self.parent = make_parent()
        self.lsa = make_lsa()

    def test_parent_can_create_booking(self):
        self.client.force_authenticate(user=self.parent)
        url = reverse("booking-list")
        data = {
            "lsa": self.lsa.id,
            "starts_at": "2026-08-15T10:00:00Z",
            "ends_at": "2026-08-15T11:00:00Z",
            "hourly_rate": "30.00",
            "total_hours": "1.00",
            "notes": "First session",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Booking.objects.count(), 1)

    def test_lsa_can_confirm_booking(self):
        booking = Booking.objects.create(
            parent=self.parent,
            lsa=self.lsa,
            starts_at=datetime(2026, 8, 15, 10, 0),
            ends_at=datetime(2026, 8, 15, 11, 0),
            hourly_rate=30.00,
            total_hours=1.0,
        )
        self.client.force_authenticate(user=self.lsa)
        url = reverse("booking-update-status", kwargs={"pk": booking.id})
        response = self.client.patch(url, {"status": "confirmed"}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        booking.refresh_from_db()
        self.assertEqual(booking.status, BookingStatus.CONFIRMED)

    def test_unauthenticated_cannot_create_booking(self):
        url = reverse("booking-list")
        data = {
            "lsa": self.lsa.id,
            "starts_at": "2026-08-15T10:00:00Z",
            "ends_at": "2026-08-15T11:00:00Z",
            "hourly_rate": "30.00",
            "total_hours": "1.00",
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class AvailabilityAPITests(APITestCase):
    def setUp(self):
        self.lsa = make_lsa()

    def test_lsa_can_post_availability(self):
        self.client.force_authenticate(user=self.lsa)
        url = reverse("availability-list")
        data = {
            "day_of_week": 1,
            "start_time": "09:00:00",
            "end_time": "12:00:00",
            "is_recurring": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Availability.objects.count(), 1)

    def test_public_can_list_availability(self):
        Availability.objects.create(
            lsa=self.lsa,
            day_of_week=1,
            start_time=time(9, 0),
            end_time=time(12, 0),
        )
        url = reverse("availability-list")
        response = self.client.get(url, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)


class ReviewAPITests(APITestCase):
    def setUp(self):
        self.parent = make_parent()
        self.lsa = make_lsa()
        self.booking = Booking.objects.create(
            parent=self.parent,
            lsa=self.lsa,
            starts_at=datetime(2026, 8, 15, 10, 0),
            ends_at=datetime(2026, 8, 15, 11, 0),
            hourly_rate=30.00,
            total_hours=1.0,
            status=BookingStatus.COMPLETED,
        )

    def test_parent_can_review_completed_booking(self):
        self.client.force_authenticate(user=self.parent)
        url = reverse("review-list")
        data = {
            "booking": self.booking.id,
            "rating": 5,
            "comment": "Excellent support",
            "would_recommend": True,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Review.objects.count(), 1)

    def test_lsa_cannot_review_booking(self):
        self.client.force_authenticate(user=self.lsa)
        url = reverse("review-list")
        data = {
            "booking": self.booking.id,
            "rating": 5,
        }
        response = self.client.post(url, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
