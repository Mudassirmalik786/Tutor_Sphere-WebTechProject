import base64
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
import requests
from django.contrib.auth.decorators import login_required

from gipfel_tutor import settings
from tutor_market.models import Tutor


@login_required
def connect_calendly(request: HttpRequest) -> HttpResponse:
    """
    Redirects the user to the Calendly OAuth authorization page.
    """
    client_id = settings.CALENDLY_CLIENT_ID
    redirect_uri = settings.CALENDLY_REDIRECT_URI

    url = (f'https://calendly.com/oauth/authorize?client_id={client_id}&redire'
           f'ct_uri={redirect_uri}&response_type=code'
           )

    return redirect(url)


def get_base64_string() -> str:
    """
    Returns the base64 encoded string of the Calendly client ID and client
    secret.
    """
    # -> Credit for base64 encodeing: https://www.geeksforgeeks.org/encoding-and-decoding-base64-strings-in-python/  # noqa
    client_id = settings.CALENDLY_CLIENT_ID
    client_secret = settings.CALENDLY_CLIENT_SECRET
    basic_auth_string = f"{client_id}:{client_secret}"
    basic_auth_string_bytes = basic_auth_string.encode('ascii')
    base64_bytes = base64.b64encode(basic_auth_string_bytes)
    return base64_bytes.decode('ascii')


@login_required
def calendly_auth(request: HttpRequest) -> HttpResponse:
    """
    Handles the Calendly OAuth authorization callback.
    """
    code = request.GET.get('code')

    url = "https://auth.calendly.com/oauth/token"

    base64_string = get_base64_string()
    redirect_uri = settings.CALENDLY_REDIRECT_URI

    payload = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Authorization": f"Basic {base64_string}"
    }

    response = requests.post(url, data=payload, headers=headers)

    response_data = response.json()

    if response.status_code != 200:
        messages.warning(request, f"{response_data['error']}: "
                         f"{response_data['error_description']}, "
                         f"please try again.")
        return redirect(reverse('dashboard', kwargs={'pk': request.user.pk}))

    messages.success(request, "Calendly connected successfully!")

    request.user.tutor.calendly_access_token = response_data['access_token']
    request.user.tutor.calendly_refresh_token = response_data['refresh_token']
    request.user.tutor.save()

    return redirect(reverse('dashboard', kwargs={'pk': request.user.pk}))


def introspect_access_token(tutor) -> dict:
    """
    Introspects the Calendly access token to check if it is still valid.
    If the token is invalid, it refreshes the token and returns the new token.
    CAREFUL: The introspection only works if the token was created on the
    deployed site.
    """
    access_token = tutor.calendly_access_token
    refresh_token = tutor.calendly_refresh_token

    url = "https://auth.calendly.com/oauth/introspect"

    payload = {
        "client_id": settings.CALENDLY_CLIENT_ID,
        "client_secret": settings.CALENDLY_CLIENT_SECRET,
        "token": access_token
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    response = requests.post(url, data=payload, headers=headers)

    response_data = response.json()

    if response.status_code != 200:
        return response_data

    if response_data['active'] is False:
        response_data = refresh_access_token(tutor)

    return response_data


def refresh_access_token(tutor) -> dict:
    """
    Refreshes the Calendly access token using the refresh token.
    """
    refresh_token = tutor.calendly_refresh_token

    url = "https://auth.calendly.com/oauth/token"

    base64_string = get_base64_string()

    payload = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "Authorization": f"Basic {base64_string}"
    }

    response = requests.post(url, data=payload, headers=headers)

    response_data = response.json()

    if response.status_code != 200:
        return response_data

    tutor.calendly_access_token = response_data['access_token']
    tutor.calendly_refresh_token = response_data['refresh_token']
    tutor.save()

    return response_data


@login_required
def disconnect_calendly(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Disconnects the Calendly integration for a tutor.
    """
    tutor = Tutor.objects.get(pk=pk)
    user = tutor.user

    tutor.calendly_access_token = None
    tutor.calendly_refresh_token = None
    tutor.calendly_token_expires_at = None
    tutor.save()

    messages.info(
        request, "Calendly disconnected successfully! You can reconnect at any"
        " time.")

    return redirect(reverse('dashboard', kwargs={'pk': user.pk}))
