from django.shortcuts import render, redirect
from django.http import HttpRequest
from login.models import User
from django.http import JsonResponse
from .forms import SignUpForm, VerifyUserForm, ResetPasswordForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from urllib.parse import quote_plus

from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from .tokens import account_activation_token, reset_password_token, account_register_token
from django.contrib.auth import get_user_model
from django.utils.safestring import mark_safe
from django.db.models.query_utils import Q

def login_user(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'You are now logged in.')
            # Redirect to the transition page with a custom message
            next_url = request.POST.get('next', '/search_link/')
            message = quote_plus('Login Successful!')  # Encodes the message to be URL-safe
            return redirect(f'/transition/?next={next_url}&message={message}')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def transition_view(request):
    # Logic to decide the next URL
    next_url = request.GET.get('next', '/default_redirect_url/')
    # Get the custom message from the query parameters, with a default message
    message = request.GET.get('message', 'Operation Successful!')
    # Render the transition page with the URL and message
    response = render(request, 'transition.html', {'redirect_url': next_url, 'message': message})
    return response

def logout_user(request):
    logout(request)
    # Specify where the user should be redirected after the transition
    next_url = '/login/' 
    # Custom message for logging out
    message = quote_plus('You have been logged out successfully!')
    # Redirect to the transition view with next URL and message
    return redirect(f'/transition/?next={next_url}&message={message}')

def check_login(request):
    if request.user.is_authenticated:
        return redirect('search_link')  # Redirect to the search page if logged in
    else:
        return redirect('login')  # Redirect to the login page if not logged in

def index(request):
    return render(request, 'index.html')

# Send email to the admin to approve the registration request
def reg_request_email(request, user, email):
    subject = "New User Registration Request"
    message = render_to_string("registration_request.html", {
        'user': user,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_register_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    admin_email = 'website.review.tool@gmail.com'
    email_message = EmailMessage(subject, message, to=[admin_email])
    email_message.content_subtype = "html"  # Ensure the email is sent as HTML
    if email_message.send():
        messages.success(request, f"Thank you {user.username} for signing up to the website review tool. An email has been sent to the admin for approval.")
    else:
        messages.error(request, f"Problem sending email to the admin. Please try again later.")

# Send email to the user to inform them of the registration status which is approved
def success_registration_email(request, user, email):
    subject = "Registration Approved"
    message = render_to_string("registration_accepted.html", {
        'user': user,
    })
    email_message = EmailMessage(subject, message, to=[email])
    # if email_message.send():
    #     messages.success(request, f"Thank you {user.username} for signing up to the website review tool. Your registration has been approved.")
    # else:
    #     messages.error(request, f"Problem sending email to {email}. Please ensure you have typed it correctly.")

# Send email to the user to inform them of the registration status which is rejected
def reject_registration_email(request, user, email):
    subject = "Registration Rejected"
    message = render_to_string("registration_rejected.html", {
        'user': user,
    })
    email_message = EmailMessage(subject, message, to=[email])
    # if email_message.send():
    #     messages.success(request, f"Thank you {user.username} for signing up to the website review tool. Your registration has been rejected.")
    # else:
    #     messages.error(request, f"Problem sending email to {email}. Please ensure you have typed it correctly.")

# Function to accept registration request
def accept_registration(request, uidb64, token):
    model = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, model.DoesNotExist):
        user = None

    if user is not None and account_register_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, f"User {user.username} has been successfully activated.")

        # Send email to user to inform them of the registration status
        success_registration_email(request, user, user.email)
    else:
        messages.error(request, "The activation link is invalid!")

    return redirect('login')

# Function to reject registration request
def reject_registration(request, uidb64, token):
    model = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = model.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, model.DoesNotExist):
        user = None

    if user is not None and account_register_token.check_token(user, token):
        # Send email to user to inform them of the registration status
        reject_registration_email(request, user, user.email)

        user.delete()
        messages.success(request, f"User {user.username} has been successfully rejected and deleted.")
    else:
        messages.error(request, "The rejection link is invalid!")

    return redirect('signup')
    

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit = False)
            # mark the user as inactive until the admin approves the registration
            user.is_active = False
            user.save()

            # Send email to admin to approve registration
            reg_request_email(request, user, form.cleaned_data.get('email'))
            next_url = '/login/' 
            message = quote_plus('Register Successful!')  
            return redirect(f'/transition/?next={next_url}&message={message}')

        else:
            messages.error(request, mark_safe("".join([f"{msg}<br/>" for error_list in form.errors.as_data().values() for error in error_list for msg in error.messages])))
    else:
        form = SignUpForm()
    return render(request, 'signup.html', {'form': form})

def forgot_password(request):
    if request.method == 'POST':
        form = VerifyUserForm(request.POST)
        if form.is_valid():
            user_email = form.cleaned_data.get('email')
            found_user = get_user_model().objects.filter(Q(email=user_email)).first()
            if found_user:
                reset_password_email(request, found_user, found_user.email)
                return redirect('index')
            else:
                messages.error(request, f"No account found with the provided username and email.")
        else:
            messages.error(request, f"Username or password were invalid.")
    else:
        form = VerifyUserForm()
    return render(request, 'forgot_password.html', {'form': form})

def reset_password_email(request, user, email):
    subject = "Reset your password."
    message = render_to_string("reset_password_email.html", {
        'user': user.username,
        'domain': get_current_site(request).domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': reset_password_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'
    })
    email_message = EmailMessage(subject, message, to=[email])
    if email_message.send():
        messages.success(request, f"An email has been sent to {email}. Please check your inbox or spam.")
    else:
        messages.error(request, f"Problem sending email to {email}. Please ensure you have typed it correctly.")

def reset_password(request, uidb64, token):
    model = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = model.objects.get(pk=uid)
    except:
        user = None

    if user is not None and reset_password_token.check_token(user, token):
        if request.method == "POST":
            form = ResetPasswordForm(user, request.POST)
            if form.is_valid():
                user.set_password(form.cleaned_data.get('password'))
                user.save()
                # Redirect to the transition page with a custom message
                next_url = '/login/'  # Directs users to log in with their new password
                message = quote_plus('Password reset Successful!')  # Encodes the message to be URL-safe
                return redirect(f'/transition/?next={next_url}&message={message}')
            else:
                messages.error(request, mark_safe("".join(
                    [f"{msg}<br/>" for error_list in form.errors.as_data().values() for error in error_list for msg in
                     error.messages])))
        else:
            form = ResetPasswordForm(user)
            return render(request, 'resetPassword.html', {'form': form})
    else:
        messages.error(request, "Link is invalid or expired.")

    return redirect('index')

