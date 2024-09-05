from django.shortcuts import render, redirect
from django.http import HttpRequest
from login.models import User
from django.http import JsonResponse
from .forms import SignUpForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
import json
from authlib.integrations.django_client import OAuth
from django.conf import settings
from django.shortcuts import redirect, render, redirect
from django.urls import reverse
from urllib.parse import quote_plus, urlencode

oauth = OAuth()

oauth.register(
    "auth0",
    client_id=settings.AUTH0_CLIENT_ID,
    client_secret=settings.AUTH0_CLIENT_SECRET,
    client_kwargs={
        "scope": "openid profile email",
    },
    server_metadata_url=f"https://{settings.AUTH0_DOMAIN}/.well-known/openid-configuration",
)



def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You are now logged in.')
            return oauth.auth0.authorize_redirect(
                request, request.build_absolute_uri(reverse("callback"))
            )

        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})
def callback(request):
    token = oauth.auth0.authorize_access_token(request)
    request.session["user"] = token
    print("callback function invoked")
    return redirect(request.build_absolute_uri(reverse("index")))
def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    request.session.clear()

    return redirect(
        f"https://{settings.AUTH0_DOMAIN}/v2/logout?"
        + urlencode(
            {
                "returnTo": request.build_absolute_uri(reverse("index")),
                "client_id": settings.AUTH0_CLIENT_ID,
            },
            quote_via=quote_plus,
        ),
    )
    return redirect('index')  # Redirect to a suitable page after logout


def index(request):

    return render(
        request,
        "index.html",
        context={
            "session": request.session.get("user"),
            "pretty": json.dumps(request.session.get("user"), indent=4),
        },
    )


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()  # Load the profile instance created by the signal
            user.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('index')  # Redirect to home page after successful signup
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def check_login(request):
    if request.user.is_authenticated:
        return redirect('search_link')  # Redirect to the search page if logged in
    else:
        return redirect('login')  # Redirect to the login page if not logged in
