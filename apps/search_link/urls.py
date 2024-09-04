from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('search_link/', views.search_link, name='search_link'),
]