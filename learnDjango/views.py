from django.http import HttpResponse
from django.shortcuts import render

def home(request) :
    # return HttpResponse("Hello, World , Welcome to the Home page")
    return render(request, 'index.html')

def login(request) :
    # return HttpResponse("Hello Let's Learn about Django")
    return render(request, 'login.html')

def register(request) :
    # return HttpResponse("Currently learning Basics of Django")
    return render(request, 'register.html')

def booking(request):
    return render(request, 'booking.html')