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
from sklearn.preprocessing import LabelEncoder, OneHotEncoder


def get_NaN_percent(fName):
    df = get_df(fName)
    clm_list = list(df)
    NaN_percent = (df.isnull().sum() * 100 / len(df)
                   ).sum() / len(clm_list)
    NaN_percent = NaN_percent.round(2)
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
    numerical_clms_lst = df._get_numeric_data().columns
    numerical_clms = len(numerical_clms_lst)
    categorical_clms_lst = list(set(list(df)) - set(numerical_clms_lst))
    categorical_clms = len(categorical_clms_lst)
    if categorical_clms <= 0:
        categorical_msg = "Categorical Features Does Not Exits"
    else:
        categorical_msg = ""
    if numerical_clms <= 0:
        numerical_msg = "Numerical Features Does Not Exits"
    else:
        numerical_msg = ""

    # No of rows and columns
    rows = len(df.index)
    columns = len(list(df))

    # NaN Values
    NaN_percent = get_NaN_percent(fName)
    total_Nan = (df.isnull().sum(axis=0)).sum()

    zippend_list = zip(clm_list, dataType_list)

    context = {
        'fName': fName,
        'fSize': fileSize,
        'rows': rows,
        'columns': columns,
        'zip': zippend_list,
        'total_NaN': total_Nan,
        'NaN_percent': NaN_percent,
        'categorical': categorical_clms,
        'numerical': numerical_clms,
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


def Dataset(request, fName):
    df = get_df(fName)
    clm_list = list(df)
    values = df.head(2000).values
    context = {
        'fName': fName,
        'clm_list': clm_list,
        'values': values,
    }
    return render(request, 'Dataset.html', context)


def Explore(request, fName):
    df = get_df(fName)

    # NaN percent
    nan_percent = get_NaN_percent(fName)

    clm_list = list(df)

    # explore

    # corr = correlation(fName)
    # correlation_list = zip(clm_list, corr)

    # mean_list = get_mean(fName)
    # median_list = get_median(fName)

    kurt_list = kurtosis(fName)
    skew_list = skewness(fName)

    # NaN_Percentage
    NaN_values = df.isnull().sum(axis=0)
    NaN_list = get_NaN(fName)
    NaN_list = NaN_list.round(2)
    NaN_list_zip = zip(clm_list, NaN_values, NaN_list)

    context = {
        'fName': fName,
        'kurtosis_list': kurt_list,
        'skewness_list': skew_list,
        'clm_list': clm_list,
        'NaN_list': NaN_list_zip,
        'NaN_percent': nan_percent,
        # 'correlation_list': correlation_list,
        # 'mean_list': mean_list,
        # 'median_list': median_list,
    }
    return render(request, 'Exploration.html', context)


def AttrDropNan(request, fName):
    df = get_df(fName)
    clm_list = list(df)
    NaN_percent = get_NaN(fName)

    drop_nan = zip(clm_list, NaN_percent)
    drop_col = zip(clm_list, NaN_percent)

    nan_percent = get_NaN_percent(fName)

    context = {
        'fName': fName,
        'attr_drop_list': drop_nan,
        'attr_drop_col_list': drop_col,
        'NaN_percent': nan_percent,
    }
    return render(request, 'AttrDropNan.html', context)


def AttrDropNanCalc(request, fName):
    df = get_df(fName)

    clm_list = list(df)
    NaN_percent = get_NaN(fName)
    drop_nan = zip(clm_list, NaN_percent)
    drop_col = zip(clm_list, NaN_percent)

    nan_percent = get_NaN_percent(fName)

    if request.method == 'POST':
        selected_col = request.POST.getlist('attrDropCols')
        for single_col in selected_col:
            df = df.dropna(subset=[single_col])

        df.to_csv(os.path.join(settings.MEDIA_ROOT,
                               'processed/'+fName+'.csv'), index=False)
        context = {
            'fName': fName,
            'attr_drop_list': drop_nan,
            'attr_drop_col_list': drop_col,
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
        df.drop(selected_col, axis=1, inplace=True)

        df.to_csv(os.path.join(settings.MEDIA_ROOT,
                               'processed/'+fName+'.csv'), index=False)

        clm_list = list(df)
        NaN_percent = get_NaN(fName)
        drop_nan = zip(clm_list, NaN_percent)
        drop_col = zip(clm_list, NaN_percent)

        nan_percent = get_NaN_percent(fName)

        context = {
            'fName': fName,
            'attr_drop_list': drop_nan,
            'attr_drop_col_list': drop_col,
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
    df = get_df(fName)
    NaN_percent = get_NaN(fName)
    clm_list = list(df)
    attr_fill = zip(clm_list, NaN_percent)

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
        print(selectedCols, selectOption)
        if selectedCols:
            if selectOption == "fill":
                fillType = request.POST.get('fillType')
                print(fillType)
                # forward fill
                if fillType == 'ffill':
                    for col in selectedCols:
                        df[col].fillna(method=fillType, inplace=True)
                    df.to_csv(os.path.join(settings.MEDIA_ROOT,
                                           'processed/'+fName+'.csv'), index=False)
                    status = 'Success'
                    message = 'NaN values of selected columns are filled by Forward method.'
                # backward fill
                elif fillType == 'bfill':
                    for col in selectedCols:
                        df[col].fillna(method=fillType, inplace=True)
                    df.to_csv(os.path.join(settings.MEDIA_ROOT,
                                           'processed/'+fName+'.csv'), index=False)
                    status = 'Success'
                    message = 'NaN values of selected columns are filled bt Backward method.'

                else:
                    pass

            elif selectOption == "replace":
                replaceWord = request.POST.get('replaceBy')
                print(replaceWord)
                for col in selectedCols:
                    df[col].fillna(replaceWord, inplace=True)
                df.to_csv(os.path.join(settings.MEDIA_ROOT,
                                       'processed/'+fName+'.csv'), index=False)
                status = 'Success'
                message = 'NaN values of selected columns are replaced by '+replaceWord

            elif selectOption == "interpolate":
                pass

        else:
            status = 'Alert'
            message = 'Please Choose atleast one feature for Fill NaN.'

        NaN_percent = get_NaN(fName)
        nan_percent = get_NaN_percent(fName)
        clm_list = list(df)
        attr_fill = zip(clm_list, NaN_percent)
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
    bin_list = []
    for clm in clm_list:
        dt = df[clm].dtype
        if dt == 'int64' or dt == 'float64':
            bin_list.append(clm)
        else:
            pass
    binning_list = []
    binned_list = []
    for col_name in bin_list:
        if 'bins' in col_name:
            binned_list.append(col_name)
        else:
            binning_list.append(col_name)
    context = {
        'fName': fName,
        'binning_list': binning_list,
        'binned_list': binned_list,
        'NaN_percent': NaN_percent,

    }

    return render(request, 'Binning.html', context)


def BinningCalc(request, fName):
    df = get_df(fName)

    if request.method == "POST":

        selectedCols = request.POST.getlist('binCol')
        binRange = request.POST.get('rangeVal')

        # check bin range
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
                                       'processed/'+fName+'.csv'), index=False)
            else:
                pass

        for selected_col in selectedCols:
            bins = []
            labels = []
            Min = int(min(df[selected_col]))
            Max = int(max(df[selected_col]))

            # binning starts

            for i in range(Min, Max, int(binRange)):
                bins.append(i)
            if Max not in bins:
                bins.append(Max)
            print(bins)
            l1 = len(bins)
            for j in range(1, l1):
                labels.append(j)
            print(labels)
            new_col = selected_col+' bins'
            df[new_col] = pd.cut(df[selected_col], bins=bins,
                                 labels=labels, include_lowest=True)
            df[new_col].fillna(method='bfill', inplace=True)

            # binning ends

        df.to_csv(os.path.join(settings.MEDIA_ROOT,
                               'processed/'+fName+'.csv'), index=False)

        # print(df[new_col].dtype)

        df_new = get_df(fName)
        clm_list = list(df_new)
        NaN_percent = get_NaN_percent(fName)
        bin_list = []
        for clm in clm_list:
            dt = df_new[clm].dtype
            if dt == 'int64' or dt == 'float64':
                bin_list.append(clm)
            else:
                pass
        binning_list = []
        binned_list = []
        for col_name in bin_list:
            if 'bins' in col_name:
                binned_list.append(col_name)
            else:
                binning_list.append(col_name)
        # print(binning_list)
        context = {
            'fName': fName,
            'binning_list': binning_list,
            'binned_list': binned_list,
            'NaN_percent': NaN_percent,
            'status': 'Success',
            'message': 'Binning was done on selected features.'
        }

        return render(request, 'Binning.html', context)

    return HttpResponse("Error ! Please go back.")


def LabelEncoding(request, fName):

    df = get_df(fName)
    clm_list = list(df)
    NaN_percent = get_NaN_percent(fName)
    labelling_list = []
    for clm in clm_list:
        dt = df[clm].dtype
        if dt == 'int64' or dt == 'float64':
            pass
        else:
            labelling_list.append(clm)

    labelled_list = []
    for col_name in clm_list:
        if 'label' in col_name:
            labelled_list.append(col_name)
        else:
            pass
    context = {
        'fName': fName,
        'labelling_list': labelling_list,
        'labelled_list': labelled_list,
        'NaN_percent': NaN_percent,

    }

    return render(request, 'LabelEncoding.html', context)


def LabelEncodingCalc(request, fName):

    df = get_df(fName)

    label_encoder = LabelEncoder()
    if request.method == 'POST':
        selected_cols = request.POST.getlist('labelCol')
        for selected_col in selected_cols:
            new_col = selected_col+' label'
            df[new_col] = label_encoder.fit_transform(
                df[selected_col].astype(str))
        df.to_csv(os.path.join(settings.MEDIA_ROOT,
                               'processed/'+fName+'.csv'), index=False)

        df_new = get_df(fName)
        clm_list = list(df_new)
        NaN_percent = get_NaN_percent(fName)
        label_list = []
        for clm in clm_list:
            dt = df_new[clm].dtype
            if dt == 'int64' or dt == 'float64':
                pass
            else:
                label_list.append(clm)
        labelling_list = []
        labelled_list = []
        for col_name in clm_list:
            if 'label' in col_name:
                labelled_list.append(col_name)
            else:
                labelling_list.append(col_name)

        context = {
            'fName': fName,
            'labelling_list': labelling_list,
            'labelled_list': labelled_list,
            'NaN_percent': NaN_percent,
            'status': 'Success',
            'message': 'Label Encoding was done on selected features.'
        }

        return render(request, 'LabelEncoding.html', context)

    return HttpResponse("Error ! Please go back.")


def OneHotEncoding(request, fName):
    df = get_df(fName)
    clm_list = list(df)
    NaN_percent = get_NaN_percent(fName)
    oneHot_list = []
    for clm in clm_list:
        dt = df[clm].dtype
        if dt == 'int64' or dt == 'float64':
            pass
        else:
            oneHot_list.append(clm)

    oneHotProcessed_list = []
    for col_name in clm_list:
        if 'onehot' in col_name:
            oneHotProcessed_list.append(col_name)
        else:
            pass
    context = {
        'fName': fName,
        'processing_list': oneHot_list,
        'processed_list': oneHotProcessed_list,
        'NaN_percent': NaN_percent,

    }

    return render(request, 'OneHotEncoding.html', context)


def OneHotEncodingCalc(request, fName):
    df = get_df(fName)
    if request.method == 'POST':
        selected_cols = request.POST.getlist('oneHotCol')
        drop_column = request.POST.get('drop-column')
        for selected_col in selected_cols:
            dummies = pd.get_dummies(df[selected_col], prefix=selected_col)
            df = pd.concat([df, dummies], axis='columns')
            if drop_column == 'on':
                del df[selected_col]
                df.to_csv(os.path.join(settings.MEDIA_ROOT,
                                       'processed/'+fName+'.csv'), index=False)
            else:
                # df.to_csv(os.path.join(settings.MEDIA_ROOT,
                #                        'processed/'+fName+'.csv'), index=False)
                ans = df[selected_col].value_counts(normalize=True) * 100
                print(ans.sum())

        df_new = get_df(fName)
        clm_list = list(df_new)
        NaN_percent = get_NaN_percent(fName)
        oneHot_list = []
        for clm in clm_list:
            dt = df_new[clm].dtype
            if dt == 'int64' or dt == 'float64':
                pass
            else:
                oneHot_list.append(clm)

        oneHotProcessed_list = selected_cols
        context = {
            'fName': fName,
            'processing_list': oneHot_list,
            'processed_list': oneHotProcessed_list,
            'NaN_percent': NaN_percent,
            'status': 'Success',
            'message': 'One-Hot Encoding was done on selected features.'

        }
        return render(request, 'OneHotEncoding.html', context)


# getting dataframe


def get_df(fName):
    data_frame = pd.read_csv(os.path.join(settings.MEDIA_ROOT,
                                          'processed/'+fName+'.csv'), encoding='mbcs')

    return data_frame


# Kurtosis
def kurtosis(fName):
    df = get_df(fName)
    df_kurtosis = df.kurt().round(2)
    column_name = list(df)
    kurtosis_list = zip(column_name, df_kurtosis)
    print(df_kurtosis)
    return kurtosis_list

# Skewness


def skewness(fName):
    df = get_df(fName)
    df_skewness = df.skew().round(2)
    column_name = list(df)
    skewness_list = zip(column_name, df_skewness)

    return skewness_list


# Correlation
# def correlation(fName):
#     df = get_df(fName)
#     correla = df.corr()
#     values = correla.values
#     main_list = []
#     correlation_list = []
#     for i in range(len(values)):
#         sub_list = []
#         for j in values[i]:
#             sub_list.append(round(j, 2))
#         main_list.append(sub_list)
#     correlation_list.append(main_list)
#     new = correlation_list[0]

#     return new


# NaN Percentage
def get_NaN(fName):
    df = get_df(fName)
    NaN_list = (df.isnull().sum() * 100 / len(df)).round(2)
    return NaN_list


# Mean
def get_mean(fName):
    df = get_df(fName)
    df_mean = df.mean().round(2)
    clm_list = list(df)
    percent = (df_mean * 100 / len(df)).round(2)
    mean_list = zip(clm_list, df_mean, percent)
    return mean_list


# Median
def get_median(fName):
    df = get_df(fName)
    df_median = df.median().round(2)
    clm_list = list(df)
    percent = (df_median * 100 / len(df)).round(2)
    median_list = zip(clm_list, df_median, percent)
    return median_list
