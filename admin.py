from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("first_name", "reservation_date", "reservation_slot", "created_at")
    list_filter = ("reservation_date", "reservation_slot")
    search_fields = ("first_name",)
