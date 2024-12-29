from datetime import timedelta
from django.db import models


class TutoringSession(models.Model):
    """
    Model representing a tutoring session.
    """

    tutor = models.ForeignKey(
        "tutor_market.Tutor", on_delete=models.CASCADE, related_name="sessions"
    )
    student = models.ForeignKey(
        "auth.User", on_delete=models.CASCADE, related_name="sessions"
    )
    price = models.DecimalField(max_digits=6, decimal_places=2)
    payment_complete = models.BooleanField(default=False)
    # -> Credit for model.SET_NULL: https://stackoverflow.com/questions/70395921/is-there-any-other-option-for-on-delete-other-than-models-cascade-for-a-foreignk  # noqa
    payment = models.ForeignKey(
        "booking.Payment",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sessions"
    )
    subject = models.ForeignKey(
        "tutor_market.Subject", on_delete=models.CASCADE, default=2)

    # Calendly json fields
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    created_at = models.DateTimeField()
    location_url = models.URLField()
    session_name = models.CharField(max_length=200)
    event_uri = models.CharField(max_length=200)
    invitee_uri = models.CharField(max_length=200)
    cancel_url = models.URLField()
    reschedule_url = models.URLField()
    invitee_email = models.EmailField()
    invitee_notes = models.TextField(blank=True, null=True)

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("scheduled", "Scheduled"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("rescheduled", "Rescheduled"),
    ]
    session_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending"
    )

    def duration(self) -> timedelta:
        """
        Calculate the duration of the tutoring session.

        Returns:
            timedelta: The duration of the session.
        """
        return self.end_time - self.start_time


class Payment(models.Model):
    """
    Model representing a payment.
    """

    # cascade has to be changed because payments should not be deleted when a user is deleted (probably smart)  # noqa
    user = models.ForeignKey("auth.User", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=6, decimal_places=2)

    PAYMENT_CHOICES = [
        ("pending", "Pending"),
        ("succeeded", "Succeeded"),
        ("failed", "Failed"),
        ("refunded", "Refunded"),
    ]

    status = models.CharField(
        max_length=20, choices=PAYMENT_CHOICES, default="pending")
    date = models.DateTimeField(auto_now_add=True)

    client_secret = models.CharField(max_length=200, default="")
    currency = models.CharField(max_length=3, default="eur")
    stripe_id = models.CharField(max_length=200, default="")
