from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AvailabilityViewSet,
    BookingViewSet,
    ChildProfileViewSet,
    LSAProfileViewSet,
    ProfileViewSet,
    ReviewViewSet,
    SpecializationViewSet,
    UserViewSet,
)

router = DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"profiles", ProfileViewSet, basename="profile")
router.register(r"specializations", SpecializationViewSet, basename="specialization")
router.register(r"lsa-profiles", LSAProfileViewSet, basename="lsaprofile")
router.register(r"children", ChildProfileViewSet, basename="childprofile")
router.register(r"availability", AvailabilityViewSet, basename="availability")
router.register(r"bookings", BookingViewSet, basename="booking")
router.register(r"reviews", ReviewViewSet, basename="review")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("rest_framework.urls")),
]
