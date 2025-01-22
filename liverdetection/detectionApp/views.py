from django.shortcuts import render, redirect
from .forms import ImageUploadForm
from .models import ImageUpload
from django.conf import settings
from livermodel import  LiverModel
import os
import datetime
import pytz
from pathlib import Path
import shutil
from django.views.decorators.http import require_POST
import base64
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, Http404

liver_model = LiverModel()

def index(request):
    if request.method == 'POST':
        for i in ('images', 'imagesDetection', 'imagesOverlay'):
            path = Path(os.path.join(settings.MEDIA_ROOT, i))
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
    folder_path = os.path.join(os.path.join(settings.MEDIA_ROOT, 'training'), folder_name)

    if not os.path.exists(folder_path):
        raise Http404("Папка не найдена")

    zip_path = os.path.join(settings.MEDIA_ROOT, f"{folder_name}.zip")
    shutil.make_archive(
        base_name=zip_path.replace('.zip', ''),
        format='zip',
        root_dir=os.path.join(settings.MEDIA_ROOT, 'training'),
        base_dir=folder_name
    )

    with open(zip_path, 'rb') as archive:
        response = HttpResponse(archive, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{folder_name}.zip"'

    os.remove(zip_path)

    return response

def download_results(request):
    folder_path = os.path.join(settings.MEDIA_ROOT, 'ImagesOverlay')

    if not os.path.exists(folder_path):
        raise Http404("Папка не найдена")

    zip_path = os.path.join(settings.MEDIA_ROOT, f"ImagesOverlay.zip")
    shutil.make_archive(
        base_name=zip_path.replace('.zip', ''),
        format='zip',
        root_dir=settings.MEDIA_ROOT,
        base_dir='ImagesOverlay'
    )

    with open(zip_path, 'rb') as archive:
        response = HttpResponse(archive, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="ImagesOverlay.zip"'

    os.remove(zip_path)

    moscow_tz = pytz.timezone('Europe/Moscow')
    current_time = datetime.datetime.now(moscow_tz)

    formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")
    folder_name = f'changed_{formatted_time}'

    src_folder = os.path.join(settings.MEDIA_ROOT, 'edited_images')
    dst_folder = os.path.join(settings.MEDIA_ROOT, 'training', folder_name, 'changed')
    src_folder_original = os.path.join(settings.MEDIA_ROOT, 'images')
    dst_folder_original = os.path.join(settings.MEDIA_ROOT, 'training', folder_name, 'original')

    files = [filename for filename in os.listdir(src_folder) if os.path.isfile(os.path.join(src_folder, filename))]

    if len(files) > 0:
        if not os.path.exists(dst_folder):
            os.makedirs(dst_folder)
        if not os.path.exists(dst_folder_original):
            os.makedirs(dst_folder_original)

        for filename in files:
            src_file = os.path.join(src_folder, filename)
            dst_file = os.path.join(dst_folder, filename)

            src_file_original = os.path.join(src_folder_original, filename)
            dst_file_original = os.path.join(dst_folder_original, filename)

            if os.path.isfile(src_file):
                shutil.copy(src_file, dst_file)
                shutil.copy(src_file_original, dst_file_original)
                os.remove(src_file)

    return response


@csrf_exempt
def save_image(request):
    if request.method == 'POST':
        image_name = request.GET.get('img_name', 'unknown')
        image_data = request.POST.get('image_data', '')

        if not image_data.startswith('data:image/png;base64,'):
            return JsonResponse({'error': 'Неверный формат изображения'}, status=400)

        image_data = image_data.split(',', 1)[1]
        image_binary = base64.b64decode(image_data)

        for name in ('edited_images', 'ImagesOverlay'):
            save_path = os.path.join(settings.MEDIA_ROOT, name, image_name)

            with open(save_path, 'wb') as f:
                f.write(image_binary)


        return redirect('results')

    return JsonResponse({'error': 'Метод не поддерживается'}, status=405)




