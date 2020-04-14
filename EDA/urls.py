from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [

    path('', views.Upload, name='Upload'),


    # Overview and Exploration
    url(r'^Home/(?P<fName>[-\w.]+\w{0,50})/$',
        views.Home, name='Home'),
    url(r'^Explore/(?P<fName>[-\w.]+\w{0,50})/$',
        views.Explore, name='Explore'),

    # Visualization
    url(r'^Visualize/(?P<fName>[-\w.]+\w{0,50})/$',
        views.Visualize, name='Visualize'),


    # Data Imputation
    url(r'^CompleteDropNan/(?P<fName>[-\w.]+\w{0,50})/$',
        views.CompleteDropNan, name='CompleteDropNan'),
    url(r'^AttrDropNan/(?P<fName>[-\w.]+\w{0,50})/$',
        views.AttrDropNan, name='AttrDropNan'),
    url(r'^AttrDropNanCalc/(?P<fName>[-\w.]+\w{0,50})/$',
        views.AttrDropNanCalc, name='AttrDropNanCalc'),
]
