from django.db import models

class Booking(models.Model):
    first_name = models.CharField(max_length=100)
    reservation_date = models.DateField()
    reservation_slot = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["reservation_date", "reservation_slot"]
        constraints = [
            models.UniqueConstraint(
                fields=["reservation_date", "reservation_slot"],
                name="unique_booking_date_slot",
            )
        ]

    def __str__(self):
        return f"{self.first_name} - {self.reservation_date} - {self.reservation_slot}:00"
