from django.shortcuts import render
from .models import CustomUser

def index(request):
    objects = CustomUser.objects.all()
    return render(request, 'index.html', {'objects': objects})
