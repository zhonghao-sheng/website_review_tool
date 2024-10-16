from django.urls import path
from login.views import index,login_user, logout_user,signup, check_login, forgot_password
from django.contrib.auth import views as auth_views

from . import views
from django.urls import register_converter

urlpatterns = [
    path('', index, name='index'),
    path('index/', index, name='index'),
    path('signup/', signup, name='signup'), 
    path('login/', login_user, name='login'),
    path('logout/', logout_user, name='logout'),
    path('check_login/', check_login, name='check_login'),  # Check login and redirect
    path('forgot_password/', forgot_password, name='forgot_password'),
    # path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(next_page=None), name='logout'),  # Logout and redirect to home page
    path('reset_password/<uidb64>/<token>', views.reset_password, name='reset_password'),
    path('accept-registration/<uidb64>/<token>/', views.accept_registration, name='accept_registration'),
    path('reject-registration/<uidb64>/<token>/', views.reject_registration, name='reject_registration'),
    path('transition/', views.transition_view, name='transition'),
    ]