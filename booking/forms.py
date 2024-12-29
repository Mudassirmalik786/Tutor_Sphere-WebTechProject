from django import forms

from booking.models import Payment


class CalendlyUriForm(forms.Form):
    """
    A form for capturing Calendly event and invitee URIs.
    """
    event_uri = forms.URLField(label='Calendly Event URI', max_length=200)
    invitee_uri = forms.URLField(label='Calendly Invitee URI', max_length=200)


class PaymentForm(forms.ModelForm):
    """
    A form for capturing payment details.
    """
    sessions = forms.CharField(max_length=200, required=False)

    class Meta:
        model = Payment
        exclude = []


class CancelForm(forms.Form):
    """
    A form for capturing cancellation reasons.
    """
    cancel_reason = forms.CharField(max_length=200, required=False)

    def __init__(self, *args, **kwargs):
        super(CancelForm, self).__init__(*args, **kwargs)
        self.fields['cancel_reason'].label = (
            'Let us know why you are cancelling the session (not required)'
        )
