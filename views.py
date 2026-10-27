import json
from datetime import date, datetime
from django.db import IntegrityError, transaction
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST
from .models import Booking

SLOTS = list(range(10, 22))

def _parse_date(value):
    try:
        return datetime.strptime(value, "%Y-%m-%d").date()
    except (TypeError, ValueError):
        return None

def book_table(request):
    return render(request, "restaurant/book.html", {
        "today": date.today().isoformat(),
        "slots": SLOTS,
    })

def reservations_page(request):
    # The page's data is fetched from the same JSON endpoint used by the booking form.
    return render(request, "restaurant/reservations.html", {"today": date.today().isoformat()})

@require_GET
def bookings_api(request):
    date_value = request.GET.get("date")
    qs = Booking.objects.all()
    if date_value:
        selected_date = _parse_date(date_value)
        if selected_date is None:
            return JsonResponse({"error": "Invalid date. Use YYYY-MM-DD."}, status=400)
        qs = qs.filter(reservation_date=selected_date)

    data = [
        {
            "id": booking.id,
            "first_name": booking.first_name,
            "reservation_date": booking.reservation_date.isoformat(),
            "reservation_slot": booking.reservation_slot,
        }
        for booking in qs
    ]
    return JsonResponse(data, safe=False)

@require_POST
def create_booking(request):
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    first_name = str(payload.get("first_name", "")).strip()
    selected_date = _parse_date(payload.get("reservation_date"))
    try:
        slot = int(payload.get("reservation_slot"))
    except (TypeError, ValueError):
        slot = None

    if not first_name:
        return JsonResponse({"error": "Please enter your first name."}, status=400)
    if selected_date is None:
        return JsonResponse({"error": "Please select a valid reservation date."}, status=400)
    if selected_date < date.today():
        return JsonResponse({"error": "Reservations cannot be made for a past date."}, status=400)
    if slot not in SLOTS:
        return JsonResponse({"error": "Please select a valid reservation slot."}, status=400)
    if Booking.objects.filter(reservation_date=selected_date, reservation_slot=slot).exists():
        return JsonResponse({"error": "That time slot is already booked. Please choose another."}, status=409)

    try:
        with transaction.atomic():
            booking = Booking.objects.create(
                first_name=first_name,
                reservation_date=selected_date,
                reservation_slot=slot,
            )
    except IntegrityError:
        return JsonResponse({"error": "That time slot was just booked. Please choose another."}, status=409)

    return JsonResponse({
        "message": "Reservation created successfully.",
        "booking": {
            "id": booking.id,
            "first_name": booking.first_name,
            "reservation_date": booking.reservation_date.isoformat(),
            "reservation_slot": booking.reservation_slot,
        },
    }, status=201)
