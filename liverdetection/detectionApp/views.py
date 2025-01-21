from django.shortcuts import render, redirect
from .forms import ImageUploadForm
from .models import ImageUpload
from django.conf import settings
from livermodel import  LiverModel
import os
from pathlib import Path
import shutil
from django.views.decorators.http import require_POST

from django.http import HttpResponse, Http404

liver_model = LiverModel()

def index(request):
    if request.method == 'POST':
        for i in ('images', 'imagesDetection', 'imagesOverlay'):
            path = Path(f'detectionApp/static/detectionApp/media/{i}')
            for item in path.iterdir():
                if item.is_file():
                    item.unlink()

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
                  {'images': images, 'has_images': bool(images)})

def edit_page(request, image_name):
    return render(request,
                  'detectionApp/edit_page.html',
                  {'image_name': image_name})

def training(request):
    path = os.path.join(settings.MEDIA_ROOT, 'training/')
    files = sorted([f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))])
    return render(request,
                  'detectionApp/training.html',
                  {'files': files})

@require_POST
def delete_file(request):
    fileName = request.POST.get('fileName')
    file_path = os.path.join(os.path.join(settings.MEDIA_ROOT, 'training/'), fileName)

    if os.path.exists(file_path):
        shutil.rmtree(file_path)
    return redirect('training')


def download_folder(request, folder_name):
    page = request.GET.get('source', 'unknown')
    if page == 'training':
        folder_path = os.path.join(os.path.join(settings.MEDIA_ROOT, 'training'), folder_name)
        root_dir = os.path.join(settings.MEDIA_ROOT, 'training')
    elif page == 'results':
        folder_path = os.path.join(settings.MEDIA_ROOT, folder_name)
        root_dir = settings.MEDIA_ROOT
    else:
        raise Http404("Папка не найдена")

    if not os.path.exists(folder_path):
        raise Http404("Папка не найдена")


    zip_path = os.path.join(settings.MEDIA_ROOT, f"{folder_name}.zip")
    shutil.make_archive(
        base_name=zip_path.replace('.zip', ''),
        format='zip',
        root_dir=root_dir,
        base_dir=folder_name
    )

    with open(zip_path, 'rb') as archive:
        response = HttpResponse(archive, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{folder_name}.zip"'

    os.remove(zip_path)

    return response