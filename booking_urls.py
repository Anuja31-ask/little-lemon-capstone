from django.urls import path
from . import views

urlpatterns = [
    path("bookings", views.bookings_api, name="bookings_api"),
    path("bookings/", views.bookings_api),
    path("create-booking/", views.create_booking, name="create_booking"),
]
