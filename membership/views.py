from django.shortcuts import render,redirect
from django.contrib.auth.models import User
# Create your views here.


def Delete_user(request,pid):
    if not request.user.is_staff:  
        return redirect('login')
    user = User.objects.get(id=pid) 
    user.delete()
    return redirect('view_user') 


def View_user(request):
    if not request.user.is_staff:  
        return redirect('login')
    user = User.objects.all()  
    context = {'user': user} 
    return render(request, 'view_user.html', context)