from django.urls import path
from django.contrib.auth import views as auth_views
from search_link import views

urlpatterns = [
    path('', views.index, name='index'),
    path('check_login/', views.check_login, name='check_login'),  # Check login and redirect
    path('search_link/', views.search_link, name='search_link'),  # Search page
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # Logout and redirect to home page
]