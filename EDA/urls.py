from django.urls import path
from django.conf.urls import url
from . import views

urlpatterns = [
    path('', views.Upload, name='Upload'),
    # path('Home', views.Home, name='Home'),
    url(r'^Home/(?P<fName>[-\w.]+\w{0,50})/$',
        views.Home, name='Home'),
    url(r'^Visualize/(?P<fName>[-\w.]+\w{0,50})/$',
        views.Visualize, name='Visualize'),
    url(r'^Explore/(?P<fName>[-\w.]+\w{0,50})/$',
        views.Explore, name='Explore'),
    # path('Visualize', views.Visualize, name='Visualize'),
    # path('Explore', views.Explore, name='Explore'),
    path('AttrDropNan', views.AttrDropNan, name='AttrDropNan'),
    path('AttrFillNan', views.AttrFillNan, name='AttrFillNan'),
]
