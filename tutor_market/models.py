from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Tutor(models.Model):
   

    user = models.OneToOneField(
        'auth.User', on_delete=models.CASCADE, related_name='tutor')
    display_name = models.CharField(max_length=200)
    subjects = models.ManyToManyField('Subject', related_name='tutors')
    # -> Credit for decimal fields: https://docs.djangoproject.com/en/5.0/ref/models/fields/#decimalfield  # noqa
    hourly_rate = models.DecimalField(max_digits=6, decimal_places=2)
    catch_phrase = models.CharField(
        max_length=200, default='Tutoring with a smile!')
    description = models.TextField()
    profile_image = models.ImageField(
        upload_to='tutor_images', null=True, blank=True)
    values = models.ManyToManyField('Value', related_name='tutors')
    iban = models.CharField(max_length=34, null=True, blank=True)
    calendly_event_url = models.URLField(null=True, blank=True)
    calendly_personal_token = models.CharField(
        max_length=600, null=True, blank=True)
    calendly_access_token = models.CharField(
        max_length=600, null=True, blank=True)
    calendly_refresh_token = models.CharField(
        max_length=600, null=True, blank=True)
    calendly_token_expires_at = models.DateTimeField(null=True, blank=True)
    profile_status = models.BooleanField(default=False)
    testing_profile = models.BooleanField(default=False)

    def average_rating(self):

        return Rating.objects.filter(tutor=self).aggregate(Avg('score'))

    def __str__(self):
        return self.display_name

    class Meta:
        ordering = ['display_name']


class Student(models.Model):


    display_name = models.CharField(max_length=200)
    profile_image = models.ImageField(
        upload_to='student_images', null=True, blank=True)

    def __str__(self):
        return self.display_name

from django.contrib.auth.models import User

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_messages", null=True)  # Added null=True
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f" From {self.sender} to {self.recipient}"





class Rating(models.Model):
    """
    Represents a rating given by a student to a tutor.

    Attributes:
        tutor (Tutor): The tutor being rated.
        student (Student): The student who gave the rating.
        score (int): The score given by the student (between 0 and 5).
        comment (str): Additional comment provided by the student.
    """

    tutor = models.ForeignKey(
        Tutor, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='ratings',
        default=None
    )
    score = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()

    def __str__(self):
        return f'{self.score} - {self.comment}'


class Subject(models.Model):
    """
    Represents a subject in the tutor market.
    """

    name = models.CharField(max_length=200, default='Other')

    def __str__(self):
        return f"{self.name} - {self.id}"


class Value(models.Model):
    """
    Represents a teaching value that a tutor may have.
    """
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name




# from django.db import models
# from django.contrib.auth.models import User  # Import the User model

class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name="conversations")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Conversation between {[user.username for user in self.participants.all()]}"

# class Message(models.Model):
#     conversation = models.ForeignKey(Conversation, related_name="messages", on_delete=models.CASCADE)
#     sender = models.ForeignKey(User, related_name="messages_sent", on_delete=models.CASCADE)
#     content = models.TextField()
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"{self.sender.username}: {self.content[:20]}"
