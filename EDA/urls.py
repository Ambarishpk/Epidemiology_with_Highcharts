from django.urls import path

from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('Visualize', views.Visualize, name='Visualize'),
    path('Explore', views.Explore, name='Explore'),
    path('AttrDropNan', views.AttrDropNan, name='AttrDropNan'),
    path('AttrFillNan', views.AttrFillNan, name='AttrFillNan'),
]
