from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
def index(request):
    return render(request, 'index.html')
def product(request):
    a1 = int(request.POST.get('a1'))
    a2 = int(request.POST.get('a2'))
    number = a1 * a2
    return HttpResponse(number)