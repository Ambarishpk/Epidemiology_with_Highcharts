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
    url(r'^Dataset/(?P<fName>[-\w.]+\w{0,50})/$',
        views.Dataset, name='Dataset'),
    url(r'^OriginalDataset/(?P<fName>[-\w.]+\w{0,50})/$',
        views.OriginalDataset, name='OriginalDataset'),
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
    # One Hot Encoding
    url(r'^OneHotEncoding/(?P<fName>[-\w.]+\w{0,50})/$',
        views.OneHotEncoding, name="OneHotEncoding"),
    url(r'^OneHotEncodingCalc/(?P<fName>[-\w.]+\w{0,50})/$',
        views.OneHotEncodingCalc, name="OneHotEncodingCalc"),
    # Binary Encoding
    # One Hot Encoding
    url(r'^BinaryEncoding/(?P<fName>[-\w.]+\w{0,50})/$',
        views.BinaryEncoding, name="BinaryEncoding"),
    url(r'^BinaryEncodingCalc/(?P<fName>[-\w.]+\w{0,50})/$',
        views.BinaryEncodingCalc, name="BinaryEncodingCalc"),
    # Count Frequency Encoding
    url(r'^CountFrequencyEncoding/(?P<fName>[-\w.]+\w{0,50})/$',
        views.CountFrequencyEncoding, name="CountFrequencyEncoding"),
    url(r'^CountFrequencyEncodingCalc/(?P<fName>[-\w.]+\w{0,50})/$',
        views.CountFrequencyEncodingCalc, name="CountFrequencyEncodingCalc"),
    # Normalization
    url(r'^Normalization/(?P<fName>[-\w.]+\w{0,50})/$',
        views.Normalization, name="Normalization"),
    url(r'^NormalizationCalc/(?P<fName>[-\w.]+\w{0,50})/$',
        views.NormalizationCalc, name="NormalizationCalc"),





    # Download Processed
    url(r'^DownloadProcessed/(?P<fName>[-\w.]+\w{0,50})/$',
        views.DownloadProcessed, name="DownloadProcessed"),

    # Remove Processed
    url(r'^RemoveDataset/(?P<fName>[-\w.]+\w{0,50})/$',
        views.RemoveDataset, name="RemoveDataset"),
    url(r'^api/(?P<fName>[-\w.]+\w{0,50})/$',
        views.fetchDataset, name="fetchDataset"),
    url(r'^customChart/(?P<fName>[-\w.]+\w{0,50})/$',
        views.customChart, name="customChart"),
    url(r'^ChangeDtypeColumn/(?P<fName>[-\w.]+\w{0,50})/$',
        views.ChangeDtype, name="ChangeDtype"),

    url(r'^KNNImputation/(?P<fName>[-\w.]+\w{0,50})/$',
        views.KNNImputation, name="KNNImputation"),




]
