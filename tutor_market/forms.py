from django import forms
from .models import Rating, Tutor, Subject
from localflavor.generic.forms import IBANFormField


class TutorForm(forms.ModelForm):
    """
    A form for creating or updating a tutor profile.

    This form includes fields for the tutor's display name, subjects, hourly
    rate, teaching values, catch phrase, description, profile image, IBAN, and
    Calendly event URL.
    """

    # -> Credit for testing IBAN: https://ibanvalidieren.de/beispiele.html
    iban = IBANFormField(
        required=False,
        help_text="Enter your IBAN for payments we make to you after lessons. "
        "For testing purposes, use DE02 5001 0517 0137 0750 30 or any other "
        "valid IBAN."
    )

    class Meta:
        model = Tutor
        fields = [
            "display_name",
            "subjects",
            "hourly_rate",
            "values",
            "catch_phrase",
            "description",
            "profile_image",
            "iban",
            "calendly_event_url",
        ]

    def __init__(self, *args, **kwargs):
        """Sets the help text for the form fields."""
        super(TutorForm, self).__init__(*args, **kwargs)
        self.fields["display_name"].help_text = (
            "Enter the Name you would like your Students to see."
        )
        self.fields["subjects"].help_text = (
            "Select the subjects you teach. (Select Multiple by holding Ctrl /"
            " Command and clicking)"
        )
        self.fields["hourly_rate"].help_text = (
            "Specify your hourly rate. For tutors just starting off €15 is "
            "recommended but it is completely up to you."
        )
        self.fields["values"].help_text = (
            "Pick the teaching values, that resonate with you the most."
        )
        self.fields["catch_phrase"].help_text = (
            "Enter a catchy phrase that represents you as a tutor. This is one"
            " of the first things students will see about you."
        )
        self.fields["description"].help_text = (
            "Provide a detailed description of your tutoring services."
        )
        self.fields["profile_image"].help_text = "Upload your profile image."
        self.fields["calendly_event_url"].help_text = (
            "Provide your Calendly event URL for scheduling sessions."
        )


class RatingForm(forms.ModelForm):
    """
    A form for creating or updating a rating.

    This form allows users to provide a score and comment for a rating.

    Attributes:
        comment (CharField): A field for entering the comment.
    """

    comment = forms.CharField(widget=forms.Textarea(attrs={"rows": 2}))

    class Meta:
        """Defines the model and fields for the form."""
        model = Rating
        fields = ["score", "comment"]

    def __init__(self, *args, **kwargs):
        """Sets the attributes for the form fields."""
        super(RatingForm, self).__init__(*args, **kwargs)
        self.fields["score"].widget.attrs.update(
            {"min": 1, "max": 5, "placeholder": "Select a score between "
                                                "1 and 5."}
        )
        self.fields["comment"].widget.attrs.update(
            {"placeholder": "Leave a comment about your experience."}
        )
        self.fields["score"].label = False
        self.fields["comment"].label = False
        

from .models import Message

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Enter message here...'}),
        }

