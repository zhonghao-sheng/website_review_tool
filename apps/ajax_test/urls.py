from ajax_test.views import index,product
from django.urls import path

urlpatterns = [
    path('', index, name='index'),
    path('pro/', product, name='pro')
]