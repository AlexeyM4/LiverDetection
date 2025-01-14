from django.shortcuts import render, redirect
from .forms import ImageUploadForm
from .models import ImageUpload
from django.conf import settings
from livermodel import  LiverModel
import os


liver_model = LiverModel()

def index(request):
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            images = request.FILES.getlist('image')
            for image in images:
                ImageUpload.objects.create(image=image)

            liver_model.detection()
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

def edit_page(request, image_name):
    return render(request,
                  'detectionApp/edit_page.html',
                  {'image_name': image_name})