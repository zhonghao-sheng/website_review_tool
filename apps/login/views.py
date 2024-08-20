from django.shortcuts import render
from django.http import HttpRequest
from login.models import User
from django.http import JsonResponse
# Create your views here.
def login(request:HttpRequest):
    dic = {'status':None, 'msg':None}
    if request.is_ajax():
        name = request.POST.get('username')
        pwd = request.POST.get('password')
        user_obj = User.objects.filter(username=name, password=pwd).first()
        if user_obj:
            dic['status']=200
        else:
            dic['status']=201
            dic['msg']='error in password or username'
        return JsonResponse(dic)
    return render(request, 'login.html')
