from django.shortcuts import render, redirect
from django.http import HttpRequest
from login.models import User
from django.http import JsonResponse
from .forms import SignUpForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You are now logged in.')
            return redirect('index')  # Redirect to a suitable page after login
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('index')  # Redirect to a suitable page after logout

def index(request):
    return render(request, 'index.html')


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
