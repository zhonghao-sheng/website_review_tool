from django.urls import path
from search_link import views

urlpatterns = [
    # path('', views.search, name='search'),
    path('search_link/', views.search_link, name='search_link'),  # Search page
    path('results/<uuid:job_id>/', views.results, name='results'),
    path('search_task/', views.search_task, name='search_task')
]