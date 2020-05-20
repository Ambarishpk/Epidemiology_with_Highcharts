from django.shortcuts import render
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import redirect
from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.files.storage import FileSystemStorage
import os
import csv
import pandas as pd
from pandas import DataFrame
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

    categorical_clms_lst = []
    date_time_clms_lst = []
    numerical_clms_lst = []

    for i in clm_list:
        if 'date' in i:
            df[i] = pd.to_datetime(df[i], dayfirst=True)
            date_time_clms_lst.append(i)
            df.to_csv(os.path.join(settings.MEDIA_ROOT,
                                   'processed/'+fName+'.csv'), index=False)
        elif df[i].dtypes == 'int64' or df[i].dtypes == 'float64':
            numerical_clms_lst.append(i)
        else:
            categorical_clms_lst.append(i)

    for date_time_col in date_time_clms_lst:
        df[date_time_col] = pd.to_datetime(df[date_time_col], dayfirst=True)

    categorical_clms = len(categorical_clms_lst)
    date_time_clms = len(date_time_clms_lst)
    numerical_clms = len(numerical_clms_lst)

    if categorical_clms <= 0:
        categorical_msg = "Categorical Features Does Not Exits"
    else:
        categorical_msg = ""
    if numerical_clms <= 0:
        numerical_msg = "Numerical Features Does Not Exits"
    else:
        numerical_msg = ""
    if date_time_clms <= 0:
        date_time_msg = "Date-Time Features Does Not Exits"
    else:
        date_time_msg = ""

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
        'clm_list': clm_list,
        'columns': columns,
        'zip': zippend_list,
        'total_NaN': total_Nan,
        'NaN_percent': NaN_percent,
        'categorical': categorical_clms,
        'numerical': numerical_clms,
        'datetime': date_time_clms,
        'cat_list': categorical_clms_lst,
        'num_list': numerical_clms_lst,
        'date_time_list': date_time_clms_lst,
        'cat_msg': categorical_msg,
        'num_msg': numerical_msg,
        'date_time_msg': date_time_msg,
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
                os.remove(file_path1)
                os.remove(file_path2)

            fs.save('processed/'+fullName, uploaded_file)
            fs.save('original/'+fullName, uploaded_file)
            df = pd.read_csv(os.path.join(settings.MEDIA_ROOT,
                                          'processed/'+fName+'.csv'), encoding='mbcs')
            df = df.replace(to_replace="?",
                            value="nan")
            df.to_csv(os.path.join(settings.MEDIA_ROOT,
                                   'processed/'+fName+'.csv'), index=False)
            context = Overview(fName)
            context['status'] = 'Success'
            context['message'] = 'Dataset Uploaded Successfully'
            return render(request, 'index.html', context)
        else:
            context = {
                'fName': fName,
                'status': 'Error',
                'message': 'Please upload .csv files'
            }
            return render(request, 'Upload.html', context)

    return render(request, 'Upload.html')


# routes


def Home(request, fName):
    context = Overview(fName)
    return render(request, 'index.html',  context)


def Visualize(request, fName):
    df = get_df(fName)
    clm_list = []
    for i in list(df):
        if df[i].dtype == 'int64' or df[i].dtype == 'float64':
            clm_list.append(i)
    nan_percent = get_NaN_percent(fName)
    context = {
        'fName': fName,
        'clm_list': clm_list,
        'NaN_percent': nan_percent,
        'data': [10, 20, 30, 40, 50, 60],
    }
    return render(request, 'Visualize.html', context)


def Dataset(request, fName):
    df = get_df(fName)
    clm_list = list(df)
    values = df.values

    paginator = Paginator(values, 200)
    page = request.GET.get('page', 1)
    try:
        data = paginator.page(page)
    except PageNotAnInteger:
        data = paginator.page(1)
    except EmptyPage:
        data = paginator.page(paginator.num_pages)

    context = {
        'fName': fName,
        'clm_list': clm_list,
        'for_filter': list(df),
        'values': data,
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
    context['status'] = 'Success'
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
        # print(selectedCols, selectOption)
        if selectedCols:
            if selectOption == "fill":
                fillType = request.POST.get('fillType')
                # print(fillType)
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
                    message = 'NaN values of selected columns are filled by Backward method.'
                elif fillType == 'mode':
                    for col in selectedCols:
                        df[col].fillna(df[col].mode()[0], inplace=True)
                    df.to_csv(os.path.join(settings.MEDIA_ROOT,
                                           'processed/'+fName+'.csv'), index=False)
                    status = 'Success'
                    message = 'NaN values of selected columns are filled by Mode method.'
                elif fillType == 'mean':
                    for col in selectedCols:
                        df[col].fillna(df[col].mean(), inplace=True)
                    df.to_csv(os.path.join(settings.MEDIA_ROOT,
                                           'processed/'+fName+'.csv'), index=False)
                    status = 'Success'
                    message = 'NaN values of selected columns are filled by Mean values.'

                else:
                    pass

            elif selectOption == "replace":
                replaceWord = request.POST.get('replaceBy')
                # print(replaceWord)
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
            # print(bins)
            l1 = len(bins)
            for j in range(1, l1):
                labels.append(j)
            # print(labels)
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
                df.to_csv(os.path.join(settings.MEDIA_ROOT,
                                       'processed/'+fName+'.csv'), index=False)
                ans = df[selected_col].value_counts(normalize=True) * 100
                # print(ans.sum())

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


def CountFrequencyEncoding(request, fName):
    df = get_df(fName)
    NaN_percent = get_NaN_percent(fName)
    clm_list = list(df)

    CF_Processed_list = []
    for col_name in clm_list:
        if 'cf' in col_name:
            CF_Processed_list.append(col_name)
        else:
            pass
    CF_list = list(set(clm_list) - set(CF_Processed_list))
    context = {
        'fName': fName,
        'cf_processing_list': CF_list,
        'cf_processed_list': CF_Processed_list,
        'NaN_percent': NaN_percent,

    }

    return render(request, 'CountFrequencyEncoding.html', context)


def CountFrequencyEncodingCalc(request, fName):
    df = get_df(fName)
    clm_list = list(df)
    if request.method == 'POST':
        selected_cols = request.POST.getlist('CFCol')
        for selected_col in selected_cols:
            df_frequency_map = df[selected_col].value_counts().to_dict()
            df[selected_col+' cf'] = df[selected_col].map(df_frequency_map)
            df.to_csv(os.path.join(settings.MEDIA_ROOT,
                                   'processed/'+fName+'.csv'), index=False)
        df_new = get_df(fName)
        NaN_percent = get_NaN_percent(fName)
        clm_list_2 = list(df_new)
        NaN_percent = get_NaN_percent(fName)
        CF_Processed_list = []
        for col_name in clm_list_2:
            if 'cf' in col_name:
                CF_Processed_list.append(col_name)
            else:
                pass
        CF_list = list(set(clm_list_2) - set(CF_Processed_list))
        context = {
            'fName': fName,
            'cf_processing_list': CF_list,
            'cf_processed_list': CF_Processed_list,
            'NaN_percent': NaN_percent,
            'status': 'Success',
            'message': 'Count Frequency Encoding was done on selected features.'
        }
        return render(request, 'CountFrequencyEncoding.html', context)


def Normalization(request, fName):
    df = get_df(fName)
    clm_list = list(df)
    NaN_percent = get_NaN_percent(fName)
    normalization_list = []
    for clm in clm_list:
        dt = df[clm].dtype
        if dt == 'int64' or dt == 'float64':
            normalization_list.append(clm)
        else:
            pass

    # labelled_list = []
    # for col_name in clm_list:
    #     if 'label' in col_name:
    #         labelled_list.append(col_name)
    #     else:
    #         pass
    context = {
        'fName': fName,
        'normalization_list': normalization_list,
        # 'labelled_list': labelled_list,
        'NaN_percent': NaN_percent,

    }

    return render(request, 'Normalization.html', context)


def NormalizationCalc(request, fName):
    df = get_df(fName)

    if request.method == 'POST':
        normMethod = request.POST.get('normMethod')
        selectedCols = request.POST.getlist('normCols')

        if normMethod == 'min-max':
            for featureName in selectedCols:
                mini = min(df[featureName])
                maxx = max(df[featureName])
                df[featureName] = (df[featureName] - mini) / (maxx - mini)
            message = 'Normalization done using Min: ' + \
                str(mini)+' and Max: '+str(maxx)+' for range (0,1)'
            status = 'Success'
        elif normMethod == 'z-score':
            for featureName in selectedCols:
                mean = df[featureName].mean()
                df1 = abs(df[featureName] - mean)
                mad = sum(df1) / len(df1)
                df[featureName] = (df[featureName] - mean) / mad
            message = 'Normalization done using Mean: ' + \
                str(mean)+' and Mean Absolute deviation: '+str(mad)
            status = 'Success'
        elif normMethod == 'decimal-scaling':
            for featureName in selectedCols:
                maxx = max(df[featureName])
                j = 1
                while maxx/j > 1:
                    j = j * 10
                df[featureName] = df[featureName] / j
            message = 'Normalization done using Decimal Scaling with value of ' + \
                str(j)
            status = 'Success'
        else:
            message = '*Please Select Atleast One Method for Normalization'
            status = 'Error'
    df.to_csv(os.path.join(settings.MEDIA_ROOT,
                           'processed/'+fName+'.csv'), index=False)
    clm_list = list(df)
    NaN_percent = get_NaN_percent(fName)
    normalization_list = []
    for clm in clm_list:
        dt = df[clm].dtype
        if dt == 'int64' or dt == 'float64':
            normalization_list.append(clm)
        else:
            pass

    context = {
        'fName': fName,
        'normalization_list': normalization_list,
        # 'labelled_list': labelled_list,
        'NaN_percent': NaN_percent,
        'message': message,
        'status': status,
    }

    return render(request, 'Normalization.html', context)


# getting dataframe


def get_df(fName):
    data_frame = pd.read_csv(os.path.join(settings.MEDIA_ROOT,
                                          'processed/'+fName+'.csv'), encoding='mbcs')

    data_frame.info()

    return data_frame


# Kurtosis
def kurtosis(fName):
    df = get_df(fName)
    df_kurtosis = df.kurt(axis=None, skipna=True).round(2)
    df_kurtosis_dict = df_kurtosis.to_dict()
    col = df_kurtosis_dict.keys()
    val = df_kurtosis_dict.values()
    kurtosis_list = zip(col, val)
    return kurtosis_list
# Skewness


def skewness(fName):
    df = get_df(fName)
    df_skewness = df.skew().round(2)
    df_skewness_dict = df_skewness.to_dict()
    col = df_skewness_dict.keys()
    val = df_skewness_dict.values()
    skewness_list = zip(col, val)

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


# Download Processed Dataset
def DownloadProcessed(request, fName):
    file_path = os.path.join(settings.MEDIA_ROOT, 'processed/'+fName+'.csv')
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(
                fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + \
                os.path.basename(file_path)
            return response
    raise Http404

# Remove Dataset


def RemoveDataset(request, fName):
    original_file_path = os.path.join(
        settings.MEDIA_ROOT, 'original/'+fName+'.csv')
    processed_file_path = os.path.join(
        settings.MEDIA_ROOT, 'processed/'+fName+'.csv')
    if os.path.exists(original_file_path and processed_file_path):
        os.remove(original_file_path)
        os.remove(processed_file_path)
    context = {
        'status': 'Success',
        'message': 'Dataset Removed Successfully.'
    }

    return render(request, 'Upload.html', context)


def fetchDataset(request, fName):
    df = get_df(fName)
    chartLabel = fName

    # skewness
    df_skewness = df.skew().round(2)
    df_skewness_dict = df_skewness.to_dict()
    skew_col = list(df_skewness_dict.keys())
    skew_val = list(df_skewness_dict.values())

    # print(df.corr().values)
    # print((df.corr().to_dict()).keys())

    # kurtosis
    df_kurtosis = df.kurt().round(2)
    df_kurtosis_dict = df_kurtosis.to_dict()
    kurt_col = list(df_kurtosis_dict.keys())
    kurt_val = list(df_kurtosis_dict.values())

    data = {
        "label": chartLabel,
        "skew_chartdata": skew_val,
        "kurt_chartdata": kurt_val,
        "skew_chartlabel": skew_col,
        "kurt_chartlabel": kurt_col,
    }
    return JsonResponse(data)


def ChangeDtype(request, fName):
    df = get_df(fName)
    clm_list = list(df)
    dtype_list = df.dtypes
    changeDt_list = zip(clm_list, dtype_list)
    # Datatype Conversions
    if request.method == 'POST':
        customDataType = request.POST.get('datatype')
        selectedColumns = request.POST.getlist('selectedColumnsDt')

        if customDataType == 'datetime':
            for col in selectedColumns:
                df[col] = df[col].add_suffix('_date')
            df.to_csv(os.path.join(settings.MEDIA_ROOT,
                                   'processed/'+fName+'.csv'), index=False)
            status = 'Success'
            message = 'Datatype Changed Succesfully.'
        elif customDataType == 'int':
            pass
        elif customDataType == 'float':
            pass
        elif customDataType == 'category':
            pass
        else:
            status = 'Error'
            message = '*Please Choose Datatype.'

        clm_list = list(df)
        dtype_list = df.dtypes
        changeDt_list = zip(clm_list, dtype_list)

        context = Overview(fName)
        context['status'] = status
        context['message'] = message

        return render(request, 'index.html', context)

    df.to_csv(os.path.join(settings.MEDIA_ROOT,
                           'processed/'+fName+'.csv'), index=False)
    context = Overview(fName)
    return render(request, 'index.html', context)
