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


def get_NaN_percent(fName):
    df = get_df(fName)
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
    percent = []
    shape = list(df.shape)
    no_of_rows = shape[0]
    no_of_columns = shape[1]
    for i in no_of_NaN:
        i = (i/no_of_rows)*100
        percent.append(round(i, 2))
    total_NaN_percentage = 0
    for i in percent:
        total_NaN_percentage += i
    NaN_percent = (total_NaN_percentage/no_of_columns)
    NaN_percent = round(NaN_percent, 2)
    return NaN_percent


def Overview(fName):
    df = get_df(fName)
    file_path = os.path.join(settings.MEDIA_ROOT, 'processed/'+fName+'.csv')
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
    percent = []
    shape = list(df.shape)
    no_of_rows = shape[0]
    no_of_columns = shape[1]
    for i in no_of_NaN:
        i = (i/no_of_rows)*100
        percent.append(round(i, 2))
    total_NaN_percentage = 0
    for i in percent:
        total_NaN_percentage += i
    NaN_percent = (total_NaN_percentage/no_of_columns)
    NaN_percent = round(NaN_percent, 2)

    zippend_list = zip(clm_list, dataType_list)

    context = {
        'fName': fName,
        'fSize': fileSize,
        'zip': zippend_list,
        'total_NaN': total_Nan,
        'NaN_percent': NaN_percent,
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
            file_path2 = os.path.join(
                settings.MEDIA_ROOT, 'processed/'+fullName)

            if os.path.exists(file_path1 and file_path2):
                context = Overview(fName)
                return render(request, 'index.html', context)

            else:
                fs.save('processed/'+fullName, uploaded_file)
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
    nan_percent = get_NaN_percent(fName)
    context = {
        'fName': fName,
        'NaN_percent': nan_percent,
    }
    return render(request, 'Visualize.html', context)


def Explore(request, fName):
    df = get_df(fName)

    # NaN percent
    nan_percent = get_NaN_percent(fName)

    # dataset
    clm_list = list(df)
    dataset_values = df.head(500).values

    # explore
    corr = correlation(fName)
    correlation_list = zip(clm_list, corr)
    kurt_list = kurtosis(fName)
    skew_list = skewness(fName)
    NaN_list = get_NaN(fName)
    mean_list = get_mean(fName)
    median_list = get_median(fName)

    context = {
        'fName': fName,
        'kurtosis_list': kurt_list,
        'skewness_list': skew_list,
        'correlation_list': correlation_list,
        'clm_list': clm_list,
        'dataset_values': dataset_values,
        'NaN_list': NaN_list,
        'NaN_percent': nan_percent,
        'mean_list': mean_list,
        'median_list': median_list,
    }
    return render(request, 'Exploration.html', context)


def AttrDropNan(request, fName):
    attr_drop1 = get_NaN(fName)
    attr_drop2 = get_NaN(fName)

    nan_percent = get_NaN_percent(fName)

    context = {
        'fName': fName,
        'attr_drop_list': attr_drop1,
        'attr_drop_col_list': attr_drop2,
        'NaN_percent': nan_percent,
    }
    return render(request, 'AttrDropNan.html', context)


def AttrDropNanCalc(request, fName):
    df = get_df(fName)
    attr_drop = get_NaN(fName)
    nan_percent = get_NaN_percent(fName)

    if request.method == 'POST':
        selected_col = request.POST.getlist('attrDropCols')
        for single_col in selected_col:
            df = df.dropna(subset=[single_col])

        df.to_csv(os.path.join(settings.MEDIA_ROOT,
                               'processed/'+fName+'.csv'), index=False)
        context = {
            'fName': fName,
            'attr_drop_list': attr_drop,
            'NaN_percent': nan_percent,
            'status': 'Success',
            'message': "NaN values are dropped."
        }
        return render(request, 'AttrDropNan.html', context)

    return HttpResponse("Error ! Please go back.")


def AttrDropColCalc(request, fName):
    df = get_df(fName)

    if request.method == 'POST':
        selected_col = request.POST.getlist('attrDropCompleteCols')
        for single_col in selected_col:
            print(single_col)
        df.drop(selected_col, axis=1, inplace=True)

        df.to_csv(os.path.join(settings.MEDIA_ROOT,
                               'processed/'+fName+'.csv'), index=False)

        attr_drop = get_NaN(fName)
        attr_drop_col = get_NaN(fName)

        nan_percent = get_NaN_percent(fName)

        context = {
            'fName': fName,
            'attr_drop_list': attr_drop,
            'attr_drop_col_list': attr_drop_col,
            'NaN_percent': nan_percent,
            'status': 'Success',
            'message': "Selected columns are dropped."
        }
        return render(request, 'AttrDropNan.html', context)

    return HttpResponse("Error ! Please go back.")


def CompleteDropNan(request, fName):
    df = get_df(fName)
    clm_list = list(df)
    for col in clm_list:
        df[col] = df[col].replace('-', np.nan)
        df = df.dropna(axis=0, subset=[col])
    df.to_csv(os.path.join(settings.MEDIA_ROOT,
                           'processed/'+fName+'.csv'), index=False)

    context = Overview(fName)
    context['status'] = 'Success !'
    context['message'] = 'All the NaN values are dropped'

    return render(request, 'index.html', context)


def AttrFillNan(request, fName):
    attr_fill = get_NaN(fName)

    nan_percent = get_NaN_percent(fName)

    context = {
        'fName': fName,
        'NaN_percent': nan_percent,
        'attr_fill_list': attr_fill,
    }
    return render(request, 'AttrFillNan.html', context)


def AttrFillNanCalc(request, fName):

    if request.method == "POST":
        df = get_df(fName)

        selectOption = request.POST.get('fillnaMethods')

        selectedCols = request.POST.getlist('attrFillCols')
        print(selectedCols)

        if selectOption == "fill":
            fillType = request.POST.get('fillType')
            # forward fill
            if fillType == 'ffill':
                for col in selectedCols:
                    df[col].fillna(method=fillType, inplace=True)
                status = 'Success'
                message = 'NaN values of selected columns are filled by Forward method.'
            # backward fill
            elif fillType == 'bfill':
                for col in selectedCols:
                    df[col].fillna(method=fillType, inplace=True)
                status = 'Success'
                message = 'NaN values of selected columns are filled bt Backward method.'

            else:
                pass

        elif selectOption == "replace":
            replaceWord = request.POST.get('replaceBy')
            for col in selectedCols:
                df[col].fillna(replaceWord, inplace=True)
            status = 'Success'
            message = 'NaN values of selected columns are replaced by '+replaceWord

        elif selectOption == "interpolate":
            pass

        df.to_csv(os.path.join(settings.MEDIA_ROOT,
                               'processed/'+fName+'.csv'), index=False)

        attr_fill = get_NaN(fName)
        nan_percent = get_NaN_percent(fName)
        context = {
            'fName': fName,
            'NaN_percent': nan_percent,
            'attr_fill_list': attr_fill,
            'status': status,
            'message': message,
        }

        return render(request, 'AttrFillNan.html', context)

    return HttpResponse("Error ! Go back.")


def Binning(request, fName):

    df = get_df(fName)
    clm_list = list(df)
    NaN_percent = get_NaN_percent(fName)
    numerical_list = []
    for clm in clm_list:
        dt = df[clm].dtype
        if dt == 'int64' or dt == 'float64':
            numerical_list.append(clm)
        else:
            pass
    context = {
        'fName': fName,
        'binning_list': numerical_list,
        'percent': NaN_percent,

    }

    return render(request, 'Binning.html', context)


def BinningCalc(request, fName):
    df = get_df(fName)

    if request.method == "POST":

        selectedCols = request.POST.getlist('binCol')
        binRange = request.POST.get('rangeVal')

        if binRange != '':
            pass
        else:
            binRange = 10

        for col in selectedCols:
            dt = df[col].dtype
            if dt == 'float64':
                df[col] = df[col].round()
                df[col] = df[col].astype(int)
                df.to_csv(os.path.join(settings.MEDIA_ROOT,
                                       fName+'.csv'), index=False, inplace=True)
            else:
                pass

        for selected_col in selectedCols:
            # binning starts
            bins = []
            labels = []
            Min = min(df[selected_col])
            Max = max(df[selected_col])
            for i in range(Min, Max, int(binRange)):
                bins.append(i)
            l1 = len(bins)
            for i in range(1, l1):
                labels.append(i)
            new_col = selected_col+' bins'
            df[new_col] = pd.cut(df[selected_col], bins=bins,
                                 labels=labels, include_lowest=True)
            # binning ends

        df.to_csv(os.path.join(settings.MEDIA_ROOT,
                               'processed/'+fName+'.csv'), index=False)

        df_new = get_df(fName)
        clm_list = list(df_new)
        NaN_percent = get_NaN_percent(fName)
        numerical_list = []
        for clm in clm_list:
            dt = df_new[clm].dtype
            if dt == 'int64' or dt == 'float64':
                numerical_list.append(clm)
            else:
                pass
        context = {
            'fName': fName,
            'binning_list': numerical_list,
            'percent': NaN_percent,
            'status': 'Success',
            'message': 'Binning was done on selected features.'
        }

        return render(request, 'Binning.html', context)

    return HttpResponse("Error ! Please go back.")

# getting dataframe


def get_df(fName):
    data_frame = df = pd.read_csv(os.path.join(settings.MEDIA_ROOT,
                                               'processed/'+fName+'.csv'), encoding='mbcs')
    return data_frame


# percentage calculation
def get_percent(fName, lst):
    lst_val = lst
    df = get_df(fName)
    percent = []
    shape = list(df.shape)
    no_of_rows = shape[0]
    for i in lst_val:
        i = (i/no_of_rows)*100
        percent.append(round(i, 2))
    return percent


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


# NaN Percentage
def get_NaN(fName):
    df = get_df(fName)
    NaN_clm_list = list(df)
    features = df.columns[0:-1]
    for feature in features:
        df[feature] = df[feature].replace(
            r'\s+', np.nan, regex=True).replace('', np.nan)
    is_na = df.isna().sum()
    no_of_NaN = list(is_na)

    percent = get_percent(fName, no_of_NaN)

    total_percent = 0
    for i in percent:
        total_percent += i
    shape = list(df.shape)
    no_of_columns = shape[1]

    NaN_list = zip(NaN_clm_list, no_of_NaN, percent)
    return NaN_list


# Mean
def get_mean(fName):
    df = get_df(fName)
    df_mean = df.mean()
    clm_list = list(df)
    mean_lst = []
    for mean_val in df_mean:
        mean_lst.append(round(mean_val, 2))
    percent = get_percent(fName, df_mean)
    mean_list = zip(clm_list, mean_lst, percent)
    return mean_list


# Median
def get_median(fName):
    df = get_df(fName)
    df_median = df.median()
    median_values = list(df_median)
    column_name = list(df)
    median_list = []
    for med_val in median_values:
        median_list.append(round(med_val, 2))
    percent = get_percent(fName, median_values)
    med_list = zip(column_name, median_list, percent)
    return med_list
