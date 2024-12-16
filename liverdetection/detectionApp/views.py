from django.shortcuts import render, redirect
from .forms import ImageUploadForm
from django.conf import settings
from livermodel import  LiverModel
import os


def index(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():

            form.save()
            LiverModel().detection()
            return redirect('results')

    else:
        form = ImageUploadForm()
    return render(request, 'detectionApp/index.html', {'form': form})


def results(request):
    images_path = os.path.join(settings.MEDIA_ROOT, 'images/')
    images = [f for f in os.listdir(images_path) if os.path.isfile(os.path.join(images_path, f))]

    return render(request,
                  'detectionApp/results.html',
                  {'images': images})

