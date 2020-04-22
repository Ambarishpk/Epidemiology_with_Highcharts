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
    url(r'^AttrDropColCalc/(?P<fName>[-\w.]+\w{0,50})/$',
        views.AttrDropColCalc, name='AttrDropColCalc'),
    url(r'^AttrFillNan/(?P<fName>[-\w.]+\w{0,50})/$',
        views.AttrFillNan, name='AttrFillNan'),
    url(r'^AttrFillNanCalc/(?P<fName>[-\w.]+\w{0,50})/$',
        views.AttrFillNanCalc, name='AttrFillNanCalc'),



    # Feature Engineering
    # Binning
    url(r'^Binning/(?P<fName>[-\w.]+\w{0,50})/$',
        views.Binning, name="Binning"),
    url(r'^BinningCalc/(?P<fName>[-\w.]+\w{0,50})/$',
        views.BinningCalc, name="BinningCalc"),
    # Label Encoding
    url(r'^LabelEncoding/(?P<fName>[-\w.]+\w{0,50})/$',
        views.LabelEncoding, name="LabelEncoding"),
    url(r'^LabelEncodingCalc/(?P<fName>[-\w.]+\w{0,50})/$',
        views.LabelEncodingCalc, name="LabelEncodingCalc"),
]
