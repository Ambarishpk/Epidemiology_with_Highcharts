from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import csv
import pandas as pd
import numpy as np


def Overview(fName):
    df = pd.read_csv(os.path.join(settings.MEDIA_ROOT,
                                  fName+'.csv'), encoding='mbcs', error_bad_lines=False)
    file_path = os.path.join(settings.MEDIA_ROOT, fName+'.csv')
    statInfo = os.stat(file_path)
    fileSize = statInfo.st_size
    fileSize = fileSize // 1000
    clm_list = list(df)

    # datatype
    dataType_list = df.dtypes

    # numerical and categorical
    categorical_clms = 0
    numerical_clms = 0
    categorical_clms_lst = []
    numerical_clms_lst = []
    for clm in clm_list:
        dt = df[clm].dtype
        if dt == 'object':
            categorical_clms += 1
            categorical_clms_lst.append(clm)
        else:
            numerical_clms += 1
            numerical_clms_lst.append(clm)

    # No of rows and columns

    shape = df.shape
    df_shape = list(shape)
    rows = df_shape[0]
    columns = df_shape[1]

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
        'rows': rows,
        'columns': columns,
        'cat_list': categorical_clms_lst,
        'num_list': numerical_clms_lst,
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


# routes


def Home(request, fName):
    context = Overview(fName)
    return render(request, 'index.html',  context)


def Visualize(request, fName):
    context = {
        'fName': fName
    }
    return render(request, 'Visualize.html', context)


def Explore(request, fName):
    kurt_list = kurtosis(fName)
    skew_list = skewness(fName)
    corr_list = correlation(fName)
    print(corr_list)
    context = {
        'fName': fName,
        'kurtosis_list': kurt_list,
        'skewness_list': skew_list,
        'correlation_list': corr_list,
    }
    return render(request, 'Exploration.html', context)


def AttrDropNan(request):
    return render(request, 'AttrDropNan.html')


def AttrFillNan(request):
    return render(request, 'AttrFillNan.html')


# Calculations

# Kurtosis
def kurtosis(fName):
    df = pd.read_csv(os.path.join(settings.MEDIA_ROOT,
                                  fName + '.csv'), encoding='mbcs')
    df_kurtosis = df.kurt()
    k_values = list(df_kurtosis)
    kurt_value = []
    for i in k_values:
        kurt_value.append(round(i, 2))
    column_name = list(df)
    kurtosis_list = zip(column_name, kurt_value)

    return kurtosis_list

# Skewness


def skewness(fName):
    df = pd.read_csv(os.path.join(settings.MEDIA_ROOT,
                                  fName + '.csv'), encoding='mbcs')
    df_skewness = df.skew()
    s_values = list(df_skewness)
    skew_values = []
    for i in s_values:
        skew_values.append(round(i, 2))
    column_name = list(df)
    skewness_list = zip(column_name, skew_values)

    return skewness_list


# Correlation

def correlation(fName):
    df = pd.read_csv(os.path.join(settings.MEDIA_ROOT,
                                  fName+'.csv'), encoding='mbcs')
    correlation = []
    corr_values = []
    correlation = df.corr()
    values = correlation.values
    colms = correlation.columns
    corr_values = []
    # for i in values:
    #     corr_values.append(round(i, 2))
    correlation_list = zip(colms, values)
    return correlation_list
