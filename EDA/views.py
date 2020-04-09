from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect

# Create your views here.


def Upload(request):
    return render(request, 'Upload.html')


def Home(request):
    return render(request, 'Visualize.html')


def Visualize(request):
    return render(request, 'Visualize.html')


def Explore(request):
    return render(request, 'Exploration.html')


def AttrDropNan(request):
    return render(request, 'AttrDropNan.html')


def AttrFillNan(request):
    return render(request, 'AttrFillNan.html')
