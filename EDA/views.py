from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect

# Create your views here.


def home(request):
    return render(request, 'index.html')


def Visualize(request):
    return render(request, 'Visualize.html')


def Explore(request):
    return render(request, 'Exploration.html')


def AttrDropNan(request):
    return render(request, 'AttrDropNan.html')


def AttrFillNan(request):
    return render(request, 'AttrFillNan.html')
