from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os
import csv
import pandas as pd
import numpy as np
import sklearn


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

    if len(categorical_clms_lst) <= 0:
        categorical_msg = "Categorical Columns Not Exits"
    else:
        categorical_msg = ""

    if len(numerical_clms_lst) <= 0:
        numerical_msg = "Numerical Columns Not Exits"
    else:
        numerical_msg = ""

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

    zippend_list = zip(clm_list, dataType_list)

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
        'cat_msg': categorical_msg,
        'num_msg': numerical_msg,
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
    df = pd.read_csv(os.path.join(settings.MEDIA_ROOT,
                                  fName+'.csv'), encoding='mbcs', error_bad_lines=False)
    clm_list = list(df)
    dataset_values = df.values

    corr = correlation(fName)
    correlation_list = zip(clm_list, corr)
    kurt_list = kurtosis(fName)
    skew_list = skewness(fName)
    NaN_list = get_NaN(fName)
    mean_list = get_mean(fName)

    context = {
        'fName': fName,
        'kurtosis_list': kurt_list,
        'skewness_list': skew_list,
        'correlation_list': correlation_list,
        'clm_list': clm_list,
        'dataset_values': dataset_values,
        'NaN_list': NaN_list,
        'mean_list': mean_list,
    }
    return render(request, 'Exploration.html', context)


def AttrDropNan(request):
    return render(request, 'AttrDropNan.html')


def AttrFillNan(request):
    return render(request, 'AttrFillNan.html')


# Calculations

def get_df(fName):
    data_frame = df = pd.read_csv(os.path.join(settings.MEDIA_ROOT,
                                               fName+'.csv'), encoding='mbcs')
    return data_frame

# Kurtosis


def kurtosis(fName):
    df = get_df(fName)
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
    df = get_df(fName)
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
    df = get_df(fName)
    correla = df.corr()
    values = correla.values
    main_list = []
    correlation_list = []
    for i in range(len(values)):
        sub_list = []
        for j in values[i]:
            sub_list.append(round(j, 2))
        main_list.append(sub_list)
    correlation_list.append(main_list)
    new = correlation_list[0]

    return new


def get_NaN(fName):
    df = get_df(fName)
    NaN_clm_list = list(df)
    features = df.columns[0:-1]
    for feature in features:
        df[feature] = df[feature].replace(
            r'\s+', np.nan, regex=True).replace('', np.nan)
    is_na = df.isna().sum()
    no_of_NaN = list(is_na)

    # find NaN percentage of each feature
    percent = []
    shape = list(df.shape)
    no_of_rows = shape[0]
    for i in no_of_NaN:
        i = (i/no_of_rows)*100
        percent.append(round(i, 2))

    NaN_list = zip(NaN_clm_list, no_of_NaN, percent)
    return NaN_list


def get_mean(fName):
    df = get_df(fName)
    df_mean = df.mean()
    clm_list = list(df)
    mean_lst = []
    for mean_val in df_mean:
        mean_lst.append(round(mean_val, 2))

    # percentage
    percent = []
    shape = list(df.shape)
    no_of_rows = shape[0]
    for i in df_mean:
        i = (i/no_of_rows)*100
        percent.append(round(i, 2))
    mean_list = zip(clm_list, mean_lst, percent)
    return mean_list
