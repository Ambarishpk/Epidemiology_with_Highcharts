from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import os


# Create your views here.


def Overview(fName):
    context = {
        'fName': fName
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
                pass
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
