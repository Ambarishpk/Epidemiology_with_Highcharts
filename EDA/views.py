from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import csv
import pandas as pd
import numpy as np


# Create your views here.


def Overview(fName):
    df = pd.read_csv(os.path.join(settings.MEDIA_ROOT,
                                  fName+'.csv'), encoding='mbcs', error_bad_lines=False)
    file_path = os.path.join(settings.MEDIA_ROOT, fName+'.csv')
    statInfo = os.stat(file_path)
    fileSize = statInfo.st_size
    fileSize = fileSize // 1000
    temp_clm_list = list(df)
    clm_list = []
    for col in temp_clm_list:
        clm_list.append(col.capitalize())

    # datatype
    dataType_list = df.dtypes
    categorical_clms = 0
    numerical_clms = 0
    for dt in dataType_list:
        if dt == 'object':
            categorical_clms += 1
        else:
            numerical_clms += 1

    # NaN Values
    featues = []
    features = df.columns[0:-1]
    for feature in featues:
        df[feature] = df[feature].replace(
            r'\s+', np.nan, regex=True).replace('', np.nan)
    is_na = df.isna().sum()
    no_of_NaN = list(is_na)
    total_Nan = 0
    for Nan in no_of_NaN:
        total_Nan += Nan

    zippend_list = zip(clm_list, dataType_list, no_of_NaN)

    context = {
        'fName': fName,
        'fSize': fileSize,
        'zip': zippend_list,
        'total_NaN': total_Nan,
        'categorical': categorical_clms,
        'numerical': numerical_clms,
    }
    return context


def Upload(request):

    if request.method == 'POST':
        uploaded_file = request.FILES['dataset']
        arr = uploaded_file.name.split('.', 1)
        fName = arr[0]
        extension = arr[1]
        fullName = fName+'.'+extension

        # Validating the uploaded file
        if extension == 'csv':
            fs = FileSystemStorage()
            file_path1 = os.path.join(
                settings.MEDIA_ROOT, 'original/'+fullName)
            file_path2 = os.path.join(settings.MEDIA_ROOT, fName+'/'+fullName)

            if os.path.exists(file_path1 and file_path2):
                context = Overview(fName)
                return render(request, 'index.html', context)
            else:
                fs.save(fullName, uploaded_file)
                fs.save(fName+'/'+fullName, uploaded_file)
                fs.save('original/'+fullName, uploaded_file)

                context = Overview(fName)
                return render(request, 'index.html', context)
        else:
            context = {
                'fName': fName,
                'status': 'Error !',
                'message': 'Please upload .csv files'
            }
            return render(request, 'Upload.html', context)

    return render(request, 'Upload.html')


def Home(request, fName):
    context = Overview(fName)
    return render(request, 'index.html',  context)


def Visualize(request, fName):
    context = {
        'fName': fName
    }
    return render(request, 'Visualize.html', context)


def Explore(request, fName):
    context = {
        'fName': fName
    }
    return render(request, 'Exploration.html', context)


def AttrDropNan(request):
    return render(request, 'AttrDropNan.html')


def AttrFillNan(request):
    return render(request, 'AttrFillNan.html')
